"""
LLM Analyzer - Analyzes test failures and generates patches
"""
import json
from typing import Dict, Any, Optional
from pathlib import Path
import openai
from anthropic import Anthropic

from ..core.config import config
from ..core.logger import get_logger

logger = get_logger(__name__)


class LLMAnalyzer:
    """Analyzes test failures using LLM and generates patches"""

    def __init__(self):
        self.provider = config.llm.provider
        self.setup_client()

    def setup_client(self):
        """Setup LLM client based on provider"""
        if self.provider == "openai":
            if not config.llm.openai_api_key:
                logger.warning("OpenAI API key not configured")
                return

            # Configuration pour OpenAI ou LM Studio
            openai.api_key = config.llm.openai_api_key

            # Support pour LM Studio (local) via base_url personnalisée
            if hasattr(config.llm, 'openai_base_url') and config.llm.openai_base_url:
                openai.api_base = config.llm.openai_base_url
                logger.info(f"Using custom OpenAI base URL: {config.llm.openai_base_url}")
                logger.info("LM Studio mode detected - using local model")

            self.model = config.llm.openai_model
            logger.info(f"Model configured: {self.model}")

        elif self.provider == "anthropic":
            if not config.llm.anthropic_api_key:
                logger.warning("Anthropic API key not configured")
                return
            self.client = Anthropic(api_key=config.llm.anthropic_api_key)
            self.model = config.llm.anthropic_model
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")

    async def analyze_failure(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze test failure and generate patch

        Args:
            context: Dictionary containing error information, DOM snapshot, etc.

        Returns:
            Dictionary with selector, patch_code, and confidence
        """
        logger.info(f"Analyzing failure with {self.provider}")

        # Truncate DOM snapshot if too large
        dom_snapshot = context.get("dom_snapshot", "")
        if len(dom_snapshot) > 50000:
            dom_snapshot = dom_snapshot[:50000] + "\n... [DOM truncated for brevity]"

        prompt = self._build_prompt(context, dom_snapshot)

        try:
            if self.provider == "openai":
                result = await self._analyze_with_openai(prompt)
            elif self.provider == "anthropic":
                result = await self._analyze_with_anthropic(prompt)
            else:
                raise ValueError(f"Unknown provider: {self.provider}")

            logger.info(f"Analysis complete. Confidence: {result.get('confidence', 0)}")
            return result

        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return {
                "selector": None,
                "patch_code": None,
                "confidence": 0.0,
                "error": str(e)
            }

    def _build_prompt(self, context: Dict[str, Any], dom_snapshot: str) -> str:
        """Build prompt for LLM"""
        return f"""You are an expert test automation engineer specializing in Playwright with Python.

A Playwright test has failed with the following context:

**Error Type:** {context.get('error', 'Unknown')}
**Error Message:** {context.get('message', 'Unknown')}
**URL:** {context.get('url', 'Unknown')}
**Failed Selector:** {context.get('selector', 'Unknown')}
**Test File:** {context.get('test_file', 'Unknown')}
**Line Number:** {context.get('line_number', 'Unknown')}

**DOM Snapshot (at time of failure):**
```html
{dom_snapshot}
```

**Original Code (that failed):**
```python
{context.get('original_code', 'Unknown')}
```

Your task is to:
1. Analyze why the selector failed
2. Propose an alternative, more robust selector (prefer text-based or role-based selectors)
3. Generate a minimal Python patch to fix the issue
4. Assess your confidence in the solution (0.0 to 1.0)

**Important Guidelines:**
- Prefer data-testid, aria-label, or visible text selectors over IDs/classes
- Use Playwright best practices (e.g., `get_by_role()`, `get_by_text()`, `get_by_label()`)
- Keep the patch minimal - only change what's necessary
- Consider accessibility (WCAG 2.2 compliance)
- The patch should be valid Python code that can be directly inserted

Return your response as a JSON object with this exact structure:
{{
    "selector": "the new selector string",
    "selector_method": "the Playwright method to use (e.g., 'get_by_role', 'get_by_text', 'locator')",
    "patch_code": "complete line(s) of Python code to replace the failing line",
    "explanation": "brief explanation of why the original failed and why this will work",
    "confidence": 0.9,
    "alternative_selectors": ["backup option 1", "backup option 2"]
}}

Respond ONLY with valid JSON, no additional text.
"""

    async def _analyze_with_openai(self, prompt: str) -> Dict[str, Any]:
        """Analyze using OpenAI API"""
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert test automation engineer. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=config.llm.temperature,
                max_tokens=config.llm.max_tokens
            )

            content = response.choices[0].message.content.strip()

            # Extract JSON if wrapped in markdown
            if content.startswith("```json"):
                content = content.split("```json")[1].split("```")[0].strip()
            elif content.startswith("```"):
                content = content.split("```")[1].split("```")[0].strip()

            result = json.loads(content)
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Raw response: {content}")
            return self._create_fallback_result(f"JSON parse error: {e}")
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._create_fallback_result(str(e))

    async def _analyze_with_anthropic(self, prompt: str) -> Dict[str, Any]:
        """Analyze using Anthropic Claude API"""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=config.llm.max_tokens,
                temperature=config.llm.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            content = message.content[0].text.strip()

            # Extract JSON if wrapped in markdown
            if content.startswith("```json"):
                content = content.split("```json")[1].split("```")[0].strip()
            elif content.startswith("```"):
                content = content.split("```")[1].split("```")[0].strip()

            result = json.loads(content)
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return self._create_fallback_result(f"JSON parse error: {e}")
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return self._create_fallback_result(str(e))

    def _create_fallback_result(self, error_msg: str) -> Dict[str, Any]:
        """Create fallback result when LLM fails"""
        return {
            "selector": None,
            "selector_method": None,
            "patch_code": None,
            "explanation": f"LLM analysis failed: {error_msg}",
            "confidence": 0.0,
            "alternative_selectors": [],
            "error": error_msg
        }
"""
Configuration for Playwright Auto-Heal Framework
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

class PlaywrightConfig(BaseModel):
    """Playwright configuration"""
    headless: bool = Field(default_factory=lambda: os.getenv("HEADLESS", "true").lower() == "true")
    slow_mo: int = Field(default_factory=lambda: int(os.getenv("SLOW_MO", "0")))
    timeout: int = Field(default_factory=lambda: int(os.getenv("TIMEOUT", "30000")))
    trace_dir: Path = Field(default=Path("traces"))
    screenshot_dir: Path = Field(default=Path("screenshots"))

class LLMConfig(BaseModel):
    """LLM configuration"""
    provider: str = Field(default_factory=lambda: os.getenv("LLM_PROVIDER", "openai"))
    openai_api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_model: str = Field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    anthropic_api_key: str = Field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    anthropic_model: str = Field(default_factory=lambda: os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229"))
    temperature: float = 0.0
    max_tokens: int = 1000

class AutoHealConfig(BaseModel):
    """Auto-heal configuration"""
    auto_commit: bool = Field(default_factory=lambda: os.getenv("AUTO_COMMIT", "true").lower() == "true")
    auto_pr: bool = Field(default_factory=lambda: os.getenv("AUTO_PR", "false").lower() == "true")
    confidence_threshold: float = Field(default_factory=lambda: float(os.getenv("CONFIDENCE_THRESHOLD", "0.7")))
    max_retries: int = Field(default_factory=lambda: int(os.getenv("MAX_RETRIES", "3")))
    patch_dir: Path = Field(default=Path("patches"))
    backup_dir: Path = Field(default=Path("backups"))

class Config:
    """Main configuration class"""
    def __init__(self):
        self.playwright = PlaywrightConfig()
        self.llm = LLMConfig()
        self.auto_heal = AutoHealConfig()

        # Create necessary directories
        self._create_directories()

    def _create_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            self.playwright.trace_dir,
            self.playwright.screenshot_dir,
            self.auto_heal.patch_dir,
            self.auto_heal.backup_dir,
            Path("logs")
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

# Global config instance
config = Config()

