"""
Orchestrator for GenTestsSH Agents
"""
import json
import asyncio
import redis
import os
from typing import Dict, Any, Optional
from agent_framework import Workflow
from .agents import AgentFactory, AnalysisResult, PatchResult
from ..core.logger import get_logger

logger = get_logger(__name__)

class AgentOrchestrator:
    """Orchestrates the self-healing process using agents"""

    def __init__(self):
        self.analysis_agent = AgentFactory.create_analysis_agent()
        self.patch_agent = AgentFactory.create_patch_agent()
        self.validation_agent = AgentFactory.create_validation_agent()
        
        # Redis client for Dev UI sync (if REDIS_URL is available)
        self.redis_client = None
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            try:
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
            except Exception as e:
                logger.warning(f"Failed to initialize Redis client in Library Orchestrator: {e}")

    def _emit_devui_event(self, executor_id: str, state: str, output: str = "", error: Optional[str] = None):
        """Emit event to Redis for Dev UI bridge"""
        if not self.redis_client:
            return
        try:
            import time
            event = {
                "type": "executor_event",
                "executor_id": executor_id,
                "state": state,
                "output": output,
                "error": error,
                "timestamp": time.time()
            }
            self.redis_client.publish("agent-events", json.dumps(event))
            logger.debug(f"Emitted DevUI event: {executor_id} ({state})")
        except Exception as e:
            logger.warning(f"Failed to emit DevUI event: {e}")

    async def heal_test(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the self-healing workflow
        
        Args:
            context: Failure context
            
        Returns:
            Patch information dictionary
        """
        logger.info("Starting agentic self-healing workflow...")

        # 1. Analysis Step
        analysis_prompt = self._build_analysis_prompt(context)
        logger.info("Requesting analysis from AnalysisAgent...")
        self._emit_devui_event("AnalysisAgent", "running")
        
        try:
            # Agent.run() returns an AgentRunResponse object
            analysis_response = await self.analysis_agent.run(analysis_prompt)
            
            # Extract text from response
            if hasattr(analysis_response, 'text'):
                response_text = analysis_response.text
            elif hasattr(analysis_response, 'content'):
                response_text = analysis_response.content
            elif isinstance(analysis_response, str):
                response_text = analysis_response
            else:
                response_text = str(analysis_response)
            
            logger.info(f"Raw analysis response: {response_text}")
            
            # Robust cleaning
            clean_response = response_text.replace("```json", "").replace("```", "").strip()
            # Replace backticks with single quotes to avoid breaking JSON strings
            clean_response = clean_response.replace('`', "'")
            
            # Clean AI markers and block text
            clean_response = re.sub(r'\{\{ai-generated-.*?\}\}', '', clean_response, flags=re.IGNORECASE)

            # Robust JSON extraction using regex
            import re
            json_match = re.search(r'\{.*\}', clean_response, re.DOTALL)
            if json_match:
                clean_response = json_match.group(0)
            
            # Remove parenthetical noise
            clean_response = re.sub(r'\s*\([^)]*\)', '', clean_response)
                
            analysis_data = json.loads(clean_response)
            
            # Normalize keys
            import re
            normalized_data = {}
            for k, v in analysis_data.items():
                norm_key = k.replace(" ", "_").replace("-", "_").lower()
                norm_key = re.sub(r'_+', '_', norm_key).strip("_")
                normalized_data[norm_key] = v
                
            # Fuzzy mapping for suggested_selector
            if "suggested_selector" not in normalized_data:
                for target in ["suggested_correct_selector", "correct_selector", "new_selector", "selector", "suggested_fixer"]:
                    if target in normalized_data:
                        normalized_data["suggested_selector"] = normalized_data[target]
                        break
                if "suggested_selector" not in normalized_data:
                    for k in normalized_data:
                        if "selector" in k and k != "alternative_selectors":
                            normalized_data["suggested_selector"] = normalized_data[k]
                            break

            if "root_cause" not in normalized_data:
                for target in ["root", "cause", "issue", "failure_reason"]:
                    if target in normalized_data:
                        normalized_data["root_cause"] = normalized_data[target]
                        break

            if "selector_method" not in normalized_data:
                normalized_data["selector_method"] = "css"
                
            analysis = AnalysisResult(**normalized_data)
                
            logger.info(f"Analysis complete. Root cause: {analysis.root_cause}")
            logger.info(f"Confidence: {analysis.confidence}")
            self._emit_devui_event("AnalysisAgent", "completed", output=analysis.root_cause)

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            self._emit_devui_event("AnalysisAgent", "failed", error=str(e))
            return {"confidence": 0.0, "error": str(e)}

        # 2. Patch Step
        patch_prompt = self._build_patch_prompt(context, analysis)
        logger.info("Requesting patch from PatchAgent...")
        
        try:
            patch_response = await self.patch_agent.run(patch_prompt)
            
            # Extract text from response
            if hasattr(patch_response, 'text'):
                response_text = patch_response.text
            elif hasattr(patch_response, 'content'):
                response_text = patch_response.content
            elif isinstance(patch_response, str):
                response_text = patch_response
            else:
                response_text = str(patch_response)
            
            logger.info(f"Raw patch response: {response_text}")
            
            # Robust cleaning
            clean_response = response_text.replace("```json", "").replace("```", "").strip()
            # Replace backticks with single quotes to avoid breaking JSON strings
            clean_response = clean_response.replace('`', "'")
            
            # Robust JSON extraction using regex
            import re
            json_match = re.search(r'\{.*\}', clean_response, re.DOTALL)
            if json_match:
                clean_response = json_match.group(0)
                
            # Remove parenthetical noise
            clean_response = re.sub(r'\s*\([^)]*\)', '', clean_response)
                
            patch_data = json.loads(clean_response)
            
            # Normalize keys
            import re
            normalized_patch = {}
            for k, v in patch_data.items():
                norm_key = k.replace(" ", "_").replace("-", "_").lower()
                norm_key = re.sub(r'_+', '_', norm_key).strip("_")
                normalized_patch[norm_key] = v
                
            # Fuzzy mapping for patch_code
            if "patch_code" not in normalized_patch:
                for target in ["patch_original_code", "patch_originalcode", "code", "patch"]:
                    if target in normalized_patch:
                        normalized_patch["patch_code"] = normalized_patch[target]
                        break

            patch = PatchResult(**normalized_patch)
                
            logger.info("Patch generated successfully")
            self._emit_devui_event("PatchAgent", "completed", output=patch.patch_code)

            # 3. Validation Step
            validation_prompt = self._build_validation_prompt(context, analysis, patch)
            logger.info("Requesting validation from ValidationAgent...")
            self._emit_devui_event("ValidationAgent", "running")
            
            try:
                validation_response = await self.validation_agent.run(validation_prompt)
                
                # Extract text from response
                if hasattr(validation_response, 'text'):
                    response_text = validation_response.text
                elif hasattr(validation_response, 'content'):
                    response_text = validation_response.content
                elif isinstance(validation_response, str):
                    response_text = validation_response
                else:
                    response_text = str(validation_response)
                
                logger.info(f"Raw validation response: {response_text}")
                
                # Robust cleaning
                clean_response = response_text.replace("```json", "").replace("```", "").strip()
                clean_response = clean_response.replace('`', "'")
                
                import re
                json_match = re.search(r'\{.*\}', clean_response, re.DOTALL)
                if json_match:
                    clean_response = json_match.group(0)
                
                from .agents import ValidationResult
                validation_data = json.loads(clean_response)
                validation = ValidationResult(**validation_data)
                
                logger.info(f"Validation complete. Score: {validation.quality_score}")
                
                if not validation.is_valid or validation.quality_score < 0.7:
                    logger.warning(f"Patch quality low: {validation.issues}")
                
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
            logger.error(f"Patch generation failed: {e}")
            self._emit_devui_event("PatchAgent", "failed", error=str(e))
            return {"confidence": 0.0, "error": str(e)}

    def _build_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for analysis"""
        dom_snapshot = context.get("dom_snapshot", "")
        if len(dom_snapshot) > 50000:
            dom_snapshot = dom_snapshot[:50000] + "\n... [DOM truncated]"

        return f"""
Analyze this test failure:

Error: {context.get('message')}
Failed Selector: {context.get('selector')}
Line: {context.get('line_number')}
Code: {context.get('original_code')}

DOM Snapshot:
{dom_snapshot}
"""

    def _build_patch_prompt(self, context: Dict[str, Any], analysis: AnalysisResult) -> str:
        """Build prompt for patch generation"""
        return f"""
Generate a patch for this failure.

Original Code: {context.get('original_code')}
Analysis: {analysis.root_cause}
Suggested Selector: {analysis.suggested_selector}
Method: {analysis.selector_method}
Reasoning: {analysis.reasoning}

Return the complete Python line to replace the original code.
"""
    def _build_validation_prompt(self, context: Dict[str, Any], analysis: AnalysisResult, patch: PatchResult) -> str:
        """Build prompt for patch validation"""
        return f"""
Validate this proposed patch.

Context:
Error: {context.get('message')}
Original Code: {context.get('original_code')}

Analysis:
Root Cause: {analysis.root_cause}
Suggested Selector: {analysis.suggested_selector}

Proposed Patch:
{patch.patch_code}

Judge if the patch is syntactically correct and effectively addresses the root cause.
"""
