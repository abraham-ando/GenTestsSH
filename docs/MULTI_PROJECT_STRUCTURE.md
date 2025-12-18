# Multi-Project Structure Guide

## Overview

The GenTestsSH workspace is a **Monorepo** hosting:

1.  **Apps**: Backend (FastAPI/DDD) and Frontend (Microsoft Dev UI).
2.  **Sources**: The Test Framework (`gen-tests-self-healing`) and independent Test Projects.

## Docker Services

The stack is managed via `docker-compose.yml`:

- **Backend** (`http://localhost:8000`): Exposes API and mounts the Dev UI backend logic.
- **Frontend** (`http://localhost:5173`): Microsoft Agent Framework Dev UI.
- **Worker**: Celery worker for executing async self-healing tasks.
- **Redis**: Message broker and state store.

## Directory Structure

```
GenTestsSH/
│
├── apps/                           # Applications (Monorepo)
│   ├── backend/                    # Backend FastAPI + Celery
│   │   ├── src/
│   │   │   ├── domain/             # Entities & Ports (DDD)
│   │   │   ├── application/        # Use Cases & Services
│   │   │   ├── infrastructure/     # Adapters (Celery, Redis, Config)
│   │   │   └── interfaces/         # API Routers
│   │   └── Dockerfile
│   │
│   └── frontend/                   # Microsoft Agent Framework Dev UI
│       ├── src/
│       └── Dockerfile
│
├── sources/
│   ├── gen-tests-self-healing/     # Framework Core (Python package)
│   │
│   ├── src/                        # Test Projects
│   │   ├── project-sample-1/
│   │   └── ...
│   │
│   └── tests/                      # Global tests
│
├── docs/                           # Documentation
├── docker-compose.yml              # Service Orchestration
└── README.md
```

## Creating a New Project

### Method 1: Using CLI (Recommended)

```bash
# From project root
auto-heal create-project my-project-name

# This creates:
# sources/src/my-project-name/
# ├── src/
# ├── tests/playwright/
# ├── docs/
# ├── requirements.txt
# ├── pytest.ini
# ├── .gitignore
# └── README.md
```

### Method 2: Manual Creation

1. **Create project directory:**

   ```bash
   mkdir sources/src/my-project
   cd sources/src/my-project
   ```

2. **Create required directories:**

   ```bash
   mkdir src tests tests/playwright docs
   ```

3. **Create `requirements.txt`:**

   ```txt
   # Gen-Tests-Self-Healing Framework
   # Install from: pip install -e ../../gen-tests-self-healing/

   pytest>=8.0.0
   pytest-playwright>=0.4.0
   playwright>=1.40.0
   ```

4. **Create `pytest.ini`:**

   ```ini
   [pytest]
   testpaths = tests
   python_files = test_*.py
   addopts = -v --tb=short
   asyncio_mode = auto
   ```

5. **Create `.gitignore`:**
   ```
   __pycache__/
   test-results/
   logs/
   patches/
   backups/
   ```

## Project Independence Rules

### ✅ Each Project MUST Have:

1. **Own `src/` directory** - Source files (HTML, JS, CSS, etc.)
2. **Own `tests/` directory** - All test files
3. **Own `requirements.txt`** - Project-specific dependencies
4. **Own `pytest.ini`** - Test configuration
5. **Own `.gitignore`** - Ignore rules
6. **Own `README.md`** - Project documentation

### ✅ Each Project SHOULD Have:

1. **Own `docs/` directory** - Additional documentation
2. **Own test data** - Fixtures, mock data, etc.
3. **Independent build** - Can build/test without other projects

### ❌ Projects SHOULD NOT:

1. **Share source files** - Each project is independent
2. **Cross-reference tests** - Tests stay within project
3. **Have circular dependencies** - Keep projects isolated

## Working with Projects

### Install Framework (Once)

```bash
# From project root
cd sources/gen-tests-self-healing
pip install -e .
playwright install
```

### Setup a Project

```bash
# Navigate to project
cd sources/src/my-project

# Install project dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v
```

### Run Tests for a Specific Project

```bash
# Option 1: Using CLI
auto-heal test-project sources/src/my-project

# Option 2: Direct pytest
cd sources/src/my-project
pytest tests/ -v

# Option 3: Specific test file
pytest tests/playwright/test_feature.py -v
```

### Run Tests for All Projects

```bash
# From project root
for project in sources/src/*/; do
    echo "Testing $project"
    auto-heal test-project "$project"
done
```

## Framework CLI Commands

```bash
# Create new project
auto-heal create-project <name>

# Test specific project
auto-heal test-project <path>

# Run single test file
auto-heal run <test-file>

# Check framework status
auto-heal status

# Check configuration
auto-heal config-check

# Restore from backup
auto-heal restore <backup-file> <target-file>
```

## Best Practices

### 1. **Keep Projects Autonomous**

- Each project should build and test independently
- Don't create dependencies between projects
- Use the framework as the only shared dependency

### 2. **Consistent Structure**

- Follow the standard project template
- Use the same directory names across projects
- Keep configuration files consistent

### 3. **Version Control**

- Each project can have its own git repo if needed
- Or use git submodules for project separation
- Always commit project-specific changes to project directories

### 4. **Testing Strategy**

- Write tests specific to each project
- Use global tests (in `sources/tests/`) for integration only
- Keep test data within project directories

### 5. **Documentation**

- Maintain project-specific README
- Document project-specific setup in project docs
- Link to framework docs for general information

## Example Workflow

### Starting a New Project

```bash
# 1. Create project structure
auto-heal create-project my-app

# 2. Add source files
cd sources/src/my-app/src
# Add your HTML, CSS, JS files here

# 3. Write tests
cd ../tests/playwright
# Create test_my_app.py

# 4. Run tests
cd ../..
pytest tests/ -v

# 5. Use auto-heal if tests fail
auto-heal test-project .
```

### Maintaining Multiple Projects

```bash
# Check all projects
for project in sources/src/*/; do
    echo "=== Testing $(basename $project) ==="
    auto-heal test-project "$project"
done

# Update framework for all projects
cd sources/gen-tests-self-healing
git pull
pip install -e . --upgrade

# Each project will automatically use updated framework
```

## Troubleshooting

### Project Tests Not Found

```bash
# Ensure pytest.ini points to correct directory
# Check that test files start with test_
# Verify Python path includes framework
```

### Import Errors

```bash
# Make sure framework is installed
pip list | grep gen-tests-self-healing

# If not found, install it
cd sources/gen-tests-self-healing
pip install -e .
```

### Project Build Issues

```bash
# Each project should have its own requirements.txt
cd sources/src/my-project
pip install -r requirements.txt

# Verify pytest configuration
pytest --collect-only
```

## Migration Guide

### Moving Existing Tests to Project Structure

1. **Create project structure:**

   ```bash
   auto-heal create-project existing-project
   ```

2. **Move source files:**

   ```bash
   mv old-src/* sources/src/existing-project/src/
   ```

3. **Move test files:**

   ```bash
   mv old-tests/* sources/src/existing-project/tests/playwright/
   ```

4. **Update imports in tests:**

   - Change absolute paths to relative
   - Update framework imports to use installed package

5. **Test the migration:**
   ```bash
   auto-heal test-project sources/src/existing-project
   ```

## Summary

- ✅ Framework is shared (in `sources/gen-tests-self-healing/`)
- ✅ CLI is in the framework (`framework/cli.py`)
- ✅ Each project is autonomous (in `sources/src/project-name/`)
- ✅ Each project has own tests, config, and dependencies
- ✅ Projects can be built and tested independently
- ✅ Use `auto-heal create-project` to scaffold new projects
- ✅ Use `auto-heal test-project` to test specific projects

# Project Sample 1 - Test Documentation

## Test Structure

This project contains automated Playwright tests with self-healing capabilities.

## Test Files

### `test_project_sample_1.py`

Main test file containing:

#### TestLoginPage

- `test_login_success()` - Tests successful login flow
- `test_login_failure()` - Tests failed login with wrong credentials
- `test_form_validation()` - Tests HTML5 form validation

#### TestDashboard

- `test_dashboard_loads()` - Tests dashboard page loads correctly
- `test_logout_button()` - Tests logout functionality

## Running Tests

### Run all tests

```bash
cd sources/src/project-sample-1
pytest tests/ -v
```

### Run specific test class

```bash
pytest tests/playwright/test_project_sample_1.py::TestLoginPage -v
```

### Run specific test

```bash
pytest tests/playwright/test_project_sample_1.py::TestLoginPage::test_login_success -v
```

### Run with auto-heal

```bash
auto-heal test-project .
```

## Test Reports

Test results, screenshots, and traces are saved in:

- `test-results/` - Test execution results
- `screenshots/` - Failure screenshots
- `traces/` - Playwright traces
- `patches/` - Auto-heal patches
- `backups/` - Test file backups

## Adding New Tests

1. Create a new test file in `tests/playwright/test_*.py`
2. Import the framework: `from framework.core.test_runner import AutoHealTestRunner`
3. Use async test functions with the runner fixture
4. Run tests to verify

Example:

```python
async def test_my_feature(runner: AutoHealTestRunner):
    async def test_func(page: Page):
        await page.goto(f"{BASE_URL}/my-page.html")
        # Your test code here

    result = await runner.run_test_with_healing(test_func)
    assert result["status"] == "passed"
```
