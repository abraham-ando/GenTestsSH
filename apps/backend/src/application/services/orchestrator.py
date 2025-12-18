"""
Orchestrator for GenTestsSH Agents
"""
import json
import asyncio
from typing import Dict, Any, Optional
from agent_framework import Workflow
from .agents import AgentFactory, AnalysisResult, PatchResult
# Fix import to point to infrastructure
from ...infrastructure.config.logger import get_logger

logger = get_logger(__name__)

class AgentOrchestrator:
    """Orchestrates the self-healing process using agents"""

    def __init__(self):
        self.analysis_agent = None
        self.patch_agent = None

    def _ensure_agents(self):
        """Lazy load agents to avoid crashes if API key is missing during import"""
        if self.analysis_agent is None:
            self.analysis_agent = AgentFactory.create_analysis_agent()
        if self.patch_agent is None:
            self.patch_agent = AgentFactory.create_patch_agent()

    async def heal_test(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the self-healing workflow
        """
        self._ensure_agents()
        logger.info("Starting agentic self-healing workflow...")

        # 1. Analysis Step
        analysis_prompt = self._build_analysis_prompt(context)
        logger.info("Requesting analysis from AnalysisAgent...")
        
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
            
            # Robust JSON extraction using regex
            import re
            json_match = re.search(r'\{.*\}', clean_response, re.DOTALL)
            if json_match:
                clean_response = json_match.group(0)
            
            analysis_data = json.loads(clean_response)
            
            # Normalize keys (remove spaces, lowercase, collapse underscores)
            import re
            normalized_data = {}
            for k, v in analysis_data.items():
                norm_key = k.replace(" ", "_").replace("-", "_").lower()
                norm_key = re.sub(r'_+', '_', norm_key).strip("_")
                normalized_data[norm_key] = v
            
            # Fuzzy mapping for suggested_selector
            if "suggested_selector" not in normalized_data:
                for target in ["suggested_correct_selector", "correct_selector", "new_selector", "selector"]:
                    if target in normalized_data:
                        normalized_data["suggested_selector"] = normalized_data[target]
                        break
                # Last resort: find any key containing 'selector'
                if "suggested_selector" not in normalized_data:
                    for k in normalized_data:
                        if "selector" in k and k != "alternative_selectors":
                            normalized_data["suggested_selector"] = normalized_data[k]
                            break
            
            # Map common synonyms or handle missing vital fields
            if "root_cause" not in normalized_data:
                for target in ["root", "cause", "issue", "failure_reason"]:
                    if target in normalized_data:
                        normalized_data["root_cause"] = normalized_data[target]
                        break
            
            if "selector_method" not in normalized_data:
                normalized_data["selector_method"] = "css" # Default fallback
            
            analysis = AnalysisResult(**normalized_data)
                
            logger.info(f"Analysis complete. Root cause: {analysis.root_cause}")
            logger.info(f"Confidence: {analysis.confidence}")

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
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
                
            patch_data = json.loads(clean_response)
            
            # Normalize keys (remove spaces, lowercase, collapse underscores)
            import re
            normalized_patch = {}
            for k, v in patch_data.items():
                norm_key = k.replace(" ", "_").replace("-", "_").lower()
                norm_key = re.sub(r'_+', '_', norm_key).strip("_")
                normalized_patch[norm_key] = v
                
            patch = PatchResult(**normalized_patch)
                
            logger.info("Patch generated successfully")

            return {
                "selector": analysis.suggested_selector,
                "selector_method": analysis.selector_method,
                "patch_code": patch.patch_code,
                "explanation": patch.explanation,
                "confidence": analysis.confidence,
                "root_cause": analysis.root_cause
            }

        except Exception as e:
            logger.error(f"Patch generation failed: {e}")
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
