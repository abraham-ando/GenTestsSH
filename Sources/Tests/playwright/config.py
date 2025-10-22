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
    openai_base_url: str = Field(default_factory=lambda: os.getenv("OPENAI_BASE_URL", ""))  # Support LM Studio
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

