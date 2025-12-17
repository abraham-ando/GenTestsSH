# Setup pour Gen-Tests-Self-Healing Framework

from setuptools import setup, find_packages
from pathlib import Path

# Lire le README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="gen-tests-self-healing",
    version="1.0.0",
    author="Auto-Heal Framework Team",
    author_email="your.email@example.com",
    description="Self-healing test automation framework with Playwright and LLM",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/GenTestsSH",
    packages=find_packages(),
    package_dir={},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.10",
    install_requires=[
        "playwright>=1.40.0",
        "pytest>=8.0.0",
        "pytest-playwright>=0.4.0",
        "pytest-asyncio>=0.23.0",
        "openai>=1.12.0",
        "anthropic>=0.18.0",
        "click>=8.1.0",
        "rich>=13.7.0",
        "loguru>=0.7.0",
        "structlog>=24.1.0",
        "GitPython>=3.1.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.6.0",
        "agent-framework>=0.1.0",  # Microsoft Agent Framework
        "fastapi>=0.109.0",
        "uvicorn>=0.27.0",
        "websockets>=12.0",
        "opentelemetry-api>=1.20.0",
        "opentelemetry-sdk>=1.20.0",
        "opentelemetry-exporter-otlp>=1.20.0",
    ],
    extras_require={
        "dev": [
            "black>=24.1.0",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
            "pytest-cov>=4.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "auto-heal=framework.cli:cli",
        ],
    },
    include_package_data=True,
)

