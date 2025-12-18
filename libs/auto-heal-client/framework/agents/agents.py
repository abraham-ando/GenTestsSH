"""
Agent definitions for GenTestsSH
"""
import os
import json
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from agent_framework.openai import OpenAIResponsesClient
from ..core.config import config
from ..core.logger import get_logger

logger = get_logger(__name__)

class AnalysisResult(BaseModel):
    """Result of the failure analysis"""
    root_cause: str = Field(description="The root cause of the failure")
    suggested_selector: str = Field(description="The new selector to use")
    selector_method: str = Field(description="The Playwright method (e.g. get_by_role)")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")
    reasoning: str = Field(description="Explanation of why this selector is better", default="No reasoning provided")
    alternative_selectors: list[str] = Field(description="Alternative selectors", default_factory=list)

class PatchResult(BaseModel):
    """Result of the patch generation"""
    patch_code: str = Field(description="The Python code to replace the failing line")
    explanation: str = Field(description="Brief explanation of the patch", default="No explanation provided")

class ValidationResult(BaseModel):
    """Result of patch validation"""
    is_valid: bool = Field(description="Whether the patch is syntactically valid")
    quality_score: float = Field(description="Quality score between 0.0 and 1.0")
    issues: list[str] = Field(description="List of issues found", default_factory=list)
    recommendations: list[str] = Field(description="List of recommendations", default_factory=list)

class AgentFactory:
    """Factory to create agents"""

    @staticmethod
    def create_analysis_agent():
        """Create the Analysis Agent"""
        api_key = config.llm.openai_api_key
        model = config.llm.openai_model
        
        # Handle LM Studio local URL if present
        base_url = getattr(config.llm, 'openai_base_url', None)
        
        client_args = {
            "api_key": api_key,
            "model_id": model,
        }
        if base_url:
            client_args["base_url"] = base_url

        # Note: In a real implementation of Agent Framework, we would pass the response_model
        # to the client or the run method if supported. 
        # For now, we'll rely on the system prompt and JSON parsing if the framework 
        # doesn't automatically handle the Pydantic model in the .run() method yet.
        # But since we are using "ResponsesClient", it likely supports it.
        
        client = OpenAIResponsesClient(**client_args)
        
        return client.create_agent(
            name="AnalysisAgent",
            instructions="""You are an expert Playwright Test Automation Engineer.

**CRITICAL**: You MUST respond with ONLY valid JSON. No explanations, no markdown, no code blocks.
Start with { and end with }. Nothing else.

Your task:
1. Analyze the test failure
2. Identify why the selector failed
3. Propose a better selector

Prefer semantic selectors: get_by_role, get_by_text, get_by_label.
Avoid unstable IDs or long CSS chains.

Response format (EXACT JSON):
{
  "root_cause": "brief explanation",
  "suggested_selector": "new selector",
  "selector_method": "method name",
  "confidence": 0.85,
  "reasoning": "why this selector is better",
  "alternative_selectors": ["alt1", "alt2"]
}

Do NOT include any text before or after the JSON object.
"""
        )

    @staticmethod
    def create_patch_agent():
        """Create the Patch Agent"""
        api_key = config.llm.openai_api_key
        model = config.llm.openai_model
        
        base_url = getattr(config.llm, 'openai_base_url', None)
        client_args = {
            "api_key": api_key,
            "model_id": model,
        }
        if base_url:
            client_args["base_url"] = base_url

        client = OpenAIResponsesClient(**client_args)
        
        return client.create_agent(
            name="PatchAgent",
            instructions="""You are an expert Python Developer specializing in Playwright.

**CRITICAL**: You MUST respond with ONLY valid JSON. No explanations, no markdown, no code blocks.
Start with { and end with }. Nothing else.

Your task:
1. Generate Python code to fix the failing test
2. Use the analysis provided
3. Write clean, valid Playwright code

Response format (EXACT JSON):
{
  "patch_code": "page.get_by_role('button', name='Submit').click()",
  "explanation": "brief explanation of the fix"
}

Do NOT include markdown (```python) in patch_code.
Do NOT include any text before or after the JSON object.
"""
        )

    @staticmethod
    def create_validation_agent():
        """Create the Validation Agent"""
        api_key = config.llm.openai_api_key
        model = config.llm.openai_model
        
        base_url = getattr(config.llm, 'openai_base_url', None)
        client_args = {
            "api_key": api_key,
            "model_id": model,
            "timeout": 120.0,
        }
        if base_url:
            client_args["base_url"] = base_url

        client = OpenAIResponsesClient(**client_args)
        
        return client.create_agent(
            name="ValidationAgent",
            instructions="""You are an expert Python code reviewer specializing in Playwright.

**CRITICAL**: You MUST respond with ONLY valid JSON. No explanations, no markdown, no code blocks.
Start with { and end with }. Nothing else.

Your task:
1. Validate the proposed patch
2. Check Python syntax and Playwright API
3. Assess selector robustness

Response format (EXACT JSON):
{
  "is_valid": true,
  "quality_score": 0.85,
  "issues": ["issue1", "issue2"],
  "recommendations": ["rec1", "rec2"]
}

Do NOT include any text before or after the JSON object.
"""
        )
