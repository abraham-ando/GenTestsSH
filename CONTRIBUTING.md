# Contributing to Playwright Auto-Heal Framework

Thank you for your interest in contributing! 🎉

## Development Setup

1. Fork and clone the repository
```bash
git clone https://github.com/yourusername/GenTestsSH.git
cd GenTestsSH
```

2. Create a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
playwright install chromium
```

4. Copy and configure `.env`
```bash
cp .env.example .env
# Edit .env with your API keys
```

## Code Style

We follow these conventions:

- **Python**: PEP 8 style guide
- **Formatting**: Black (line length 120)
- **Linting**: Flake8
- **Type hints**: MyPy
- **Docstrings**: Google style

Run before committing:
```bash
black sources/tests/playwright/ --line-length 120
flake8 sources/tests/playwright/ --max-line-length=120 --ignore=E203,W503
mypy sources/tests/playwright/ --ignore-missing-imports
```

## Testing

Run tests locally:
```bash
# All tests
pytest sources/tests/playwright/main.py -v

# Specific test
pytest sources/tests/playwright/main.py::TestLoginPage::test_login_success -v

# With coverage
pytest sources/tests/playwright/main.py --cov=sources/tests/playwright
```

## Commit Guidelines

Follow the conventional commits format:

```
[Auto-Heal] <type>: <description>

<body>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style
- `refactor`: Code refactoring
- `test`: Tests
- `chore`: Maintenance

Examples:
```
[Auto-Heal] feat: Add support for custom LLM providers
[Auto-Heal] fix: Correct selector extraction from error messages
[Auto-Heal] docs: Update installation instructions
```

## Pull Request Process

1. Create a feature branch
```bash
git checkout -b feat/amazing-feature
```

2. Make your changes and test thoroughly

3. Update documentation if needed

4. Commit with clear messages

5. Push to your fork
```bash
git push origin feat/amazing-feature
```

6. Open a Pull Request with:
   - Clear description of changes
   - Related issue numbers
   - Screenshots/videos if UI changes
   - Test results

## Areas for Contribution

- 🐛 **Bug fixes**: Check open issues
- ✨ **Features**: Propose new capabilities
- 📚 **Documentation**: Improve guides
- 🧪 **Tests**: Increase coverage
- 🎨 **Examples**: Add use cases
- 🌐 **Localization**: Translate docs

## Questions?

Open an issue for discussion before major changes.

Thank you for contributing! 🚀

