"""
Self-Healing Workflow for GenTestsSH
"""
import json
from typing import Any, Dict
from agent_framework import WorkflowBuilder, AgentExecutorResponse
from .agents import AgentFactory, AnalysisResult, PatchResult, ValidationResult
from ..core.logger import get_logger

logger = get_logger(__name__)

# Condition functions for routing

def high_confidence(message: Any) -> bool:
    """Route to PatchAgent if confidence >= 80%"""
    if not isinstance(message, AgentExecutorResponse):
        return False
    try:
        # Parse the analysis response
        text = message.agent_run_response.text if hasattr(message, 'agent_run_response') else str(message)
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

# Create agents
analysis_agent = AgentFactory.create_analysis_agent()
patch_agent = AgentFactory.create_patch_agent()
validation_agent = AgentFactory.create_validation_agent()

# Build the workflow
workflow = (
    WorkflowBuilder(
        name="SelfHealingWorkflow",
        description="Automated test self-healing with conditional routing (Analysis → Patch → Validation → Apply/Review)",
    )
    .set_start_executor(analysis_agent)
    
    # Branch 1: High confidence (>= 80%) → generate patch
    .add_edge(analysis_agent, patch_agent, condition=high_confidence)
    
    # Branch 2: Low confidence (< 80%) → human review (terminal)
    # Note: We don't add an edge for low_confidence as it's a terminal state
    
    # After patch generation → validate
    .add_edge(patch_agent, validation_agent)
    
    # Branch 3a: Valid patch (quality >= 70%) → auto-apply (terminal)
    # Branch 3b: Invalid patch → human review (terminal)
    # Note: Terminal states don't need edges, they end the workflow
    
    .build()
)

# Export for hot reload compatibility
self_healing_workflow = workflow

def create_workflow():
    """Factory function to create the workflow"""
    return workflow
