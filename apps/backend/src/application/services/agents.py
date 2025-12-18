"""
Agent definitions for GenTestsSH
"""
import os
import json
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from agent_framework.openai import OpenAIResponsesClient
from ...infrastructure.config.config import config
from ...infrastructure.config.logger import get_logger

logger = get_logger(__name__)

class AnalysisResult(BaseModel):
    """Result of the failure analysis"""
    root_cause: str = Field(description="The root cause of the failure")
    suggested_selector: str = Field(description="The new selector to use")
    selector_method: str = Field(description="The Playwright method (e.g. get_by_role)")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")
    reasoning: str = Field(description="Explanation of why this selector is better", default="No reasoning provided")
    alternative_selectors: list[str] = Field(description="Alternative selectors", default_factory=list)
    tool_call: Optional[Dict[str, Any]] = Field(description="Optional tool call to MCP browser", default=None)

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
        api_key = config.OPENAI_API_KEY
        model = config.OPENAI_MODEL
        
        base_url = config.OPENAI_BASE_URL
        client_args = {
            "api_key": api_key,
            "model_id": model,
            "timeout": 120.0,
        }
        if base_url:
            client_args["base_url"] = base_url

        client = OpenAIResponsesClient(**client_args)
        
        return client.create_agent(
            name="AnalysisAgent",
            instructions="""You are an expert Playwright Test Automation Engineer.

**CRITICAL**: You MUST respond with ONLY valid JSON. 
NO EXPLANATIONS, NO MARKDOWN, NO CODE BLOCKS, NO CONVERSATION.
Your response MUST start with '{' and end with '}'. Nothing else.

Your task:
1. Analyze the test failure
2. Identify why the selector failed
3. Propose a better selector
4. **OPTIONAL**: If you need more info (e.g. current viewport, dynamic element state), you can call a BROWSER TOOL.

**AVAILABLE BROWSER TOOLS**:
- `playwright_navigate(url: str)`
- `playwright_screenshot()`: Returns a screenshot of the current page.
- `playwright_click(selector: str)`
- `playwright_fill(selector: str, value: str)`
- `playwright_hover(selector: str)`

To use a tool, include a `tool_call` object in your JSON.

**EXAMPLE WITH TOOL CALL**:
{
  "root_cause": "I need to see the element state to be sure.",
  "suggested_selector": "pending",
  "selector_method": "pending",
  "confidence": 0.5,
  "reasoning": "Element might be hidden or dynamic.",
  "tool_call": {
    "name": "playwright_screenshot",
    "arguments": {}
  }
}

Response format (EXACT JSON):
{
  "root_cause": "string",
  "suggested_selector": "string",
  "selector_method": "string",
  "confidence": number,
  "reasoning": "string",
  "alternative_selectors": ["string"],
  "tool_call": {"name": "string", "arguments": "object"} | null
}

Do NOT include any text before or after the JSON object.
"""
        )

    @staticmethod
    def create_patch_agent():
        """Create the Patch Agent"""
        api_key = config.OPENAI_API_KEY
        model = config.OPENAI_MODEL
        
        base_url = config.OPENAI_BASE_URL
        client_args = {
            "api_key": api_key,
            "model_id": model,
            "timeout": 120.0,
        }
        if base_url:
            client_args["base_url"] = base_url

        client = OpenAIResponsesClient(**client_args)
        
        return client.create_agent(
            name="PatchAgent",
            instructions="""You are an expert Python Developer specializing in Playwright.

**CRITICAL**: You MUST respond with ONLY valid JSON. 
NO EXPLANATIONS, NO MARKDOWN, NO CODE BLOCKS, NO CONVERSATION.
Your response MUST start with '{' and end with '}'. Nothing else.

Your task:
1. Generate Python code to fix the failing test
2. Use the analysis provided
3. Write clean, valid Playwright code

**EXAMPLE VALID RESPONSE**:
{
  "patch_code": "await page.locator('#password').fill('my-secret-pass')",
  "explanation": "Updated selector to use stable ID instead of unstable CSS path."
}

Response format (EXACT JSON):
{
  "patch_code": "string",
  "explanation": "string"
}

Do NOT output 'await page.css' or 'await page.get_by_css'.
Use standard Playwright methods: locator(), get_by_label(), get_by_role(), etc.
Do NOT include markdown (```python) in patch_code.
Do NOT include any text before or after the JSON object.
"""
        )

    @staticmethod
    def create_validation_agent():
        """Create the Validation Agent"""
        api_key = config.OPENAI_API_KEY
        model = config.OPENAI_MODEL
        
        base_url = config.OPENAI_BASE_URL
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

**CRITICAL**: You MUST respond with ONLY valid JSON. 
NO EXPLANATIONS, NO MARKDOWN, NO CODE BLOCKS, NO CONVERSATION.
Your response MUST start with '{' and end with '}'. Nothing else.

Your task:
1. Validate the proposed patch
2. Check Python syntax and Playwright API
3. Assess selector robustness

**EXAMPLE VALID RESPONSE**:
{
  "is_valid": true,
  "quality_score": 0.9,
  "issues": [],
  "recommendations": ["Ensure the password is not hardcoded in real scenarios."]
}

Response format (EXACT JSON):
{
  "is_valid": boolean,
  "quality_score": number,
  "issues": ["string"],
  "recommendations": ["string"]
}

Do NOT include any text before or after the JSON object.
"""
        )
