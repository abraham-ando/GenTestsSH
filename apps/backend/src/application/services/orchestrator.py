"""
Orchestrates the self-healing process using agents
"""
import json
import asyncio
import redis
import re
from typing import Dict, Any, Optional
from agent_framework import Workflow
from .agents import AgentFactory, AnalysisResult, PatchResult
from ...infrastructure.mcp.client import mcp_client
from ...infrastructure.config.logger import get_logger

logger = get_logger(__name__)

class AgentOrchestrator:
    """Orchestrates the self-healing process using agents"""

    def __init__(self):
        self.analysis_agent = None
        self.patch_agent = None
        self.validation_agent = None

    def _ensure_agents(self):
        """Lazy load agents to avoid crashes if API key is missing during import"""
        if self.analysis_agent is None:
            self.analysis_agent = AgentFactory.create_analysis_agent()
        if self.patch_agent is None:
            self.patch_agent = AgentFactory.create_patch_agent()
        if self.validation_agent is None:
            self.validation_agent = AgentFactory.create_validation_agent()
        
        if not hasattr(self, 'redis_client'):
            try:
                from ...infrastructure.config.config import config
                self.redis_client = redis.from_url(config.REDIS_URL, decode_responses=True)
            except Exception as e:
                logger.warning(f"Failed to initialize Redis client: {e}")
                self.redis_client = None

    def _emit_devui_event(self, executor_id: str, state: str, output: str = "", error: Optional[str] = None):
        if not hasattr(self, 'redis_client') or self.redis_client is None: return
        try:
            import time
            event = {"type": "executor_event", "executor_id": executor_id, "state": state, "output": output, "error": error, "timestamp": time.time()}
            self.redis_client.publish("agent-events", json.dumps(event))
        except Exception as e: logger.warning(f"Failed to emit event: {e}")

    def _parse_analysis(self, response_text: str) -> AnalysisResult:
        """Helper to parse and normalize analysis response"""
        clean_response = response_text.replace("```json", "").replace("```", "").strip()
        clean_response = clean_response.replace('`', "'")
        clean_response = re.sub(r'\{\{ai-generated-.*?\}\}', '', clean_response, flags=re.IGNORECASE)
        json_match = re.search(r'\{.*\}', clean_response, re.DOTALL)
        if json_match: clean_response = json_match.group(0)
        clean_response = re.sub(r'\s*\([^)]*\)', '', clean_response)
        
        data = json.loads(clean_response)
        normalized = {}
        for k, v in data.items():
            norm_key = re.sub(r'_+', '_', k.replace(" ", "_").replace("-", "_").lower()).strip("_")
            normalized[norm_key] = v
        
        if "suggested_selector" not in normalized:
            for target in ["suggested_correct_selector", "correct_selector", "new_selector", "selector", "suggested_fixer"]:
                if target in normalized: normalized["suggested_selector"] = normalized[target]; break
        
        if "root_cause" not in normalized:
            for target in ["root", "cause", "issue", "failure_reason"]:
                if target in normalized: normalized["root_cause"] = normalized[target]; break

        if "selector_method" not in normalized: normalized["selector_method"] = "css"
        if "confidence" not in normalized: normalized["confidence"] = 0.5

        return AnalysisResult(**normalized)

    async def heal_test(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run the self-healing workflow"""
        self._ensure_agents()
        logger.info("Starting agentic self-healing workflow...")

        # 1. Analysis Step
        analysis_prompt = self._build_analysis_prompt(context)
        logger.info("Requesting analysis from AnalysisAgent...")
        self._emit_devui_event("AnalysisAgent", "running")
        
        try:
            # First pass
            resp = await self.analysis_agent.run(analysis_prompt)
            text = getattr(resp, 'text', getattr(resp, 'content', str(resp)))
            analysis = self._parse_analysis(text)

            # MCP Reasoning Loop
            mcp_iterations = 0
            while analysis.tool_call and mcp_iterations < 3:
                mcp_iterations += 1
                tool_name = analysis.tool_call["name"]
                tool_args = analysis.tool_call.get("arguments", {})
                
                logger.info(f"Executing MCP Tool: {tool_name} (Iteration {mcp_iterations})")
                self._emit_devui_event("AnalysisAgent", "running", output=f"Using tool: {tool_name}")
                
                try:
                    tool_res = await mcp_client.call_tool(tool_name, tool_args)
                    analysis_prompt += f"\n\n[MCP TOOL RESULT ({tool_name})]:\n{tool_res}\n"
                    analysis_prompt += "\nPlease continue your analysis."
                    
                    resp = await self.analysis_agent.run(analysis_prompt)
                    text = getattr(resp, 'text', getattr(resp, 'content', str(resp)))
                    analysis = self._parse_analysis(text)
                except Exception as te:
                    logger.error(f"MCP Error: {te}")
                    analysis.tool_call = None

            logger.info(f"Analysis complete: {analysis.root_cause}")
            self._emit_devui_event("AnalysisAgent", "completed", output=analysis.root_cause)

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            self._emit_devui_event("AnalysisAgent", "failed", error=str(e))
            return {"confidence": 0.0, "error": str(e)}

        # 2. Patch Step
        patch_prompt = self._build_patch_prompt(context, analysis)
        logger.info("Requesting patch...")
        self._emit_devui_event("PatchAgent", "running")
        
        try:
            resp = await self.patch_agent.run(patch_prompt)
            text = getattr(resp, 'text', getattr(resp, 'content', str(resp)))
            
            clean = re.sub(r'\{.*\}', lambda m: m.group(0), text.replace("```json", "").replace("```", ""), flags=re.DOTALL)
            json_match = re.search(r'\{.*\}', clean, re.DOTALL)
            patch_data = json.loads(json_match.group(0)) if json_match else {}
            
            patch = PatchResult(
                patch_code=patch_data.get("patch_code", patch_data.get("code", "")),
                explanation=patch_data.get("explanation", "")
            )
            
            self._emit_devui_event("PatchAgent", "completed", output=patch.patch_code)

            # 3. Validation Step
            val_prompt = self._build_validation_prompt(context, analysis, patch)
            logger.info("Requesting validation...")
            self._emit_devui_event("ValidationAgent", "running")
            
            try:
                v_resp = await self.validation_agent.run(val_prompt)
                v_text = getattr(v_resp, 'text', getattr(v_resp, 'content', str(v_resp)))
                v_match = re.search(r'\{.*\}', v_text, re.DOTALL)
                v_data = json.loads(v_match.group(0)) if v_match else {}
                
                from .agents import ValidationResult
                validation = ValidationResult(**v_data)
                self._emit_devui_event("ValidationAgent", "completed", output=f"Score: {validation.quality_score}")
            except Exception as ve:
                logger.error(f"Validation failed: {ve}")
                self._emit_devui_event("ValidationAgent", "failed", error=str(ve))

            return {
                "selector": analysis.suggested_selector,
                "selector_method": analysis.selector_method,
                "patch_code": patch.patch_code,
                "explanation": patch.explanation,
                "confidence": analysis.confidence,
                "root_cause": analysis.root_cause,
                "validation_score": validation.quality_score if 'validation' in locals() else 0.0
            }

        except Exception as e:
            logger.error(f"Patch failed: {e}")
            self._emit_devui_event("PatchAgent", "failed", error=str(e))
            return {"confidence": 0.0, "error": str(e)}

    def _build_analysis_prompt(self, context: Dict[str, Any]) -> str:
        dom = context.get("dom_snapshot", "")
        if len(dom) > 50000: dom = dom[:50000] + "\n... [truncated]"
        return f"Error: {context.get('message')}\nSelector: {context.get('selector')}\nDOM:\n{dom}"

    def _build_patch_prompt(self, context: Dict[str, Any], analysis: AnalysisResult) -> str:
        return f"Fix: {context.get('original_code')}\nAnalysis: {analysis.root_cause}\nSelector: {analysis.suggested_selector}"

    def _build_validation_prompt(self, context: Dict[str, Any], analysis: AnalysisResult, patch: PatchResult) -> str:
        return f"Original: {context.get('original_code')}\nPatch: {patch.patch_code}"
