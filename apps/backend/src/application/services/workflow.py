"""
Self-Healing Workflow for GenTestsSH
"""
import json
from typing import Any, Dict
from agent_framework import WorkflowBuilder, AgentExecutorResponse
from .agents import AgentFactory, AnalysisResult, PatchResult, ValidationResult
from ...infrastructure.config.logger import get_logger

logger = get_logger(__name__)

# Condition functions for routing

def high_confidence(message: Any) -> bool:
    """Route to PatchAgent if confidence >= 80%"""
    if not isinstance(message, AgentExecutorResponse):
        return False
    try:
        # Parse the analysis response
        text = message.agent_run_response.text if hasattr(message, 'agent_run_response') else str(message)
        # More robust JSON cleaning
        import re
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            clean_text = json_match.group(0)
        else:
            clean_text = text.replace("```json", "").replace("```", "").strip()
            
        analysis = AnalysisResult.model_validate_json(clean_text)
        return analysis.confidence >= 0.80
    except Exception as e:
        logger.error(f"Error parsing analysis for confidence check: {e}")
        return False

def low_confidence(message: Any) -> bool:
    """Route to HumanReview if confidence < 80%"""
    return not high_confidence(message)

def is_valid_patch(message: Any) -> bool:
    """Route to AutoApply if validation passes"""
    if not isinstance(message, AgentExecutorResponse):
        return True
    try:
        text = message.agent_run_response.text if hasattr(message, 'agent_run_response') else str(message)
        clean_text = text.replace("```json", "").replace("```", "").strip()
        validation = ValidationResult.model_validate_json(clean_text)
        return validation.is_valid and validation.quality_score >= 0.70
    except Exception as e:
        logger.error(f"Error parsing validation result: {e}")
        return False

def needs_review(message: Any) -> bool:
    """Route to HumanReview if validation fails"""
    return not is_valid_patch(message)

# Export for hot reload compatibility
def get_workflow():
    """Build the workflow lazily"""
    # Create agents only when requested
    analysis_agent = AgentFactory.create_analysis_agent()
    patch_agent = AgentFactory.create_patch_agent()
    validation_agent = AgentFactory.create_validation_agent()

    return (
        WorkflowBuilder()
        .set_start_executor(analysis_agent)
        .add_edge(analysis_agent, patch_agent, condition=high_confidence)
        .add_edge(patch_agent, validation_agent)
        .build()
    )

# Use a lazy property or global that is initialized on first access
_workflow = None

def self_healing_workflow():
    global _workflow
    if _workflow is None:
        _workflow = get_workflow()
    return _workflow

def create_workflow():
    """Factory function to create the workflow"""
    return workflow
