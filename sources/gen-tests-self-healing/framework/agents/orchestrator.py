"""
Orchestrator for GenTestsSH Agents
"""
import json
import asyncio
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
        
        try:
            # We expect the agent to return a JSON string matching AnalysisResult
            analysis_response = await self.analysis_agent.run(analysis_prompt)
            
            # Parse the response
            # Note: In a full integration, we would check if response is already an object
            if isinstance(analysis_response, str):
                # Clean up markdown if present
                clean_response = analysis_response.replace("```json", "").replace("```", "").strip()
                analysis_data = json.loads(clean_response)
                analysis = AnalysisResult(**analysis_data)
            else:
                # Assume it's already the model or dict
                analysis = AnalysisResult(**analysis_response)
                
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
            
            if isinstance(patch_response, str):
                clean_response = patch_response.replace("```json", "").replace("```", "").strip()
                patch_data = json.loads(clean_response)
                patch = PatchResult(**patch_data)
            else:
                patch = PatchResult(**patch_response)
                
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
