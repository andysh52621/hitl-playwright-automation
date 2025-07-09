# HITL Playwright Automation Project Guidelines

This document provides essential information for developers working on the HITL Playwright Automation project.

## Project Overview

This project is a UI and API automation framework for testing the HITL (Human-in-the-Loop) application. It uses Playwright for browser automation, pytest for test execution, and integrates with Azure DevOps (ADO) for test management and reporting.

## Project Structure

```
hitl-playwright-automation/
├── .junie/                  # Junie guidelines
├── ado/                     # Azure DevOps integration
├── allure-2.33.0/           # Allure reporting tool
├── allure-report/           # Generated Allure reports
├── allure-results/          # Allure test results
├── api_config/              # API configuration
├── config/                  # Application configuration
├── dao/                     # Data Access Objects
├── db_engine/               # Database engine configuration
├── db_models/               # Database models
├── domain_models/           # Domain models
├── lib/                     # Library code
├── pages/                   # Page objects for UI testing
│   └── ui_pages/            # UI page objects
├── tests/                   # Test suites
│   ├── api_test_suite/      # API tests
│   ├── core_test_suite/     # Core functionality tests
│   └── ui_test_suite/       # UI tests
├── utils/                   # Utility functions
│   ├── ado/                 # ADO utilities
│   ├── allure/              # Allure reporting utilities
│   └── generic/             # Generic utilities
├── conftest.py              # pytest configuration
├── playwright.config.py     # Playwright configuration
├── pytest.ini               # pytest configuration
└── requirements.txt         # Project dependencies
```

## Build/Configuration Instructions

### Environment Setup

1. **Python Environment**:
   - Python 3.10+ is required
   - Create a virtual environment:
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\activate
     ```

2. **Install Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

3. **Install Playwright Browsers**:
   ```powershell
   playwright install
   ```

4. **Allure Setup**:
   - Allure is included in the project (allure-2.33.0 directory)
   - Java JDK is required for Allure report generation

### Configuration Files

1. **playwright.config.py**: 
   - Contains browser configuration
   - Default browser is Chromium
   - Headless mode is disabled by default for debugging
   - Base URL is set to the test environment

2. **pytest.ini**:
   - Contains pytest configuration
   - Defines test markers
   - Configures logging and reporting

3. **User Configuration**:
   - User credentials are stored in Excel files in the user-config directory
   - Test users are loaded via the `test_user` fixture in conftest.py

## Testing Information

### Test Organization

Tests are organized into three main suites:
- **api_test_suite**: Tests for API functionality
- **core_test_suite**: Tests for core functionality
- **ui_test_suite**: Tests for UI functionality using Playwright

### Test Data

Test data is separated from test logic using YAML files:
- Each test has a corresponding YAML file with the same name
- YAML files contain:
  - ADO metadata (plan_id, suite_id, case_id)
  - Allure reporting metadata (feature, story, title, description)
  - Test-specific data

### Running Tests

#### Basic Test Execution

To run all tests:
```powershell
python -m pytest
```

To run a specific test suite:
```powershell
python -m pytest tests\ui_test_suite
```

To run a specific test:
```powershell
python -m pytest tests\ui_test_suite\test_example.py
```

#### Test Markers

Tests can be filtered by markers defined in pytest.ini:
```powershell
python -m pytest -m regression
python -m pytest -m smoke
python -m pytest -m api
```

#### Parallel Execution

Tests can be run in parallel using pytest-xdist:
```powershell
python -m pytest -n 4  # Run with 4 workers
```

### Creating New Tests

1. **Create Test File**:
   - Create a new Python file in the appropriate test suite directory
   - Use the naming convention `test_*.py`

2. **Create YAML File**:
   - Create a YAML file with the same name as the test file
   - Include ADO metadata, Allure metadata, and test data

3. **Test Structure**:
   - Use the `@pytest.mark.regression` decorator for regression tests
   - Use the `@ado_ui_testcase` decorator for UI tests that integrate with ADO
   - Use page objects for UI interactions
   - Use the step logger for test step reporting

### Example Test

Here's a simple example test:

```python
import pytest
from datetime import datetime
from playwright.sync_api import Page

from utils.ado.ado_decorators import ado_ui_testcase
from utils.ado.ado_step_logger import StepLogger
from dao.test_execution_db_updater_dao import DBReporter

@pytest.mark.regression
@ado_ui_testcase
def test_example_navigation(page: Page, test_user, reporter: DBReporter, ado_runner, request):
    """
    A simple example test that demonstrates navigation to a website.
    """
    # Get test metadata and step logger
    meta = request.node.meta
    steps = request.node.steps

    # Get test data from YAML file
    test_data = meta.get("test_data", {}).get("test", {})
    url = test_data.get("url", "https://www.example.com")
    expected_title = test_data.get("expected_title", "Example")

    # Navigate to a website
    page.goto(url)

    # Log a step
    steps.add_step("Navigation", f"Successfully navigated to {url}")

    # Verify the page title
    title = page.title()
    assert expected_title in title, f"Expected '{expected_title}' in title, but got '{title}'"

    # Log another step
    steps.add_step("Verification", "Successfully verified page title")

    # Take a screenshot
    screenshot_path = f"example_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    page.screenshot(path=screenshot_path)
    steps.add_step("Screenshot", f"Captured screenshot of the page: {screenshot_path}")
```

With a corresponding YAML file:

```yaml
# test case and ado meta-data
description: Example test for demonstration purposes
domain: Example
entity: Example
build_definition_id: 3499
ado_plan_id: 979524
ado_suite_id: 1040029
ado_case_id: 1041621
ado_org_url: https://dev.azure.com/Vizientinc
ado_project: VizTech

# allure reporting meta-data
allure:
  feature: Example Feature
  story: Example Story
  title: Example Test
  description: >
    This is an example test that demonstrates how to create a basic UI test with Playwright.
    It navigates to example.com and verifies the page title.
  severity: normal
  owner: example.user
  tags:
    - example
    - ui
    - documentation

# testcase specific testdata
test_data:
  test:
    url: "https://www.example.com"
    expected_title: "Example"
```

## Reporting

### Allure Reporting

Allure reports are generated automatically after test execution:
- Results are stored in the `allure-results` directory
- Reports are generated in the `allure-report` directory
- To view the report, open `allure-report/index.html` in a browser

### HTML Reporting

HTML reports are also generated:
- `pytest_basic_html_report.html`: Basic HTML report
- `pytest_html_report.html`: Detailed HTML report

### Azure DevOps Integration

Test results are automatically reported to Azure DevOps:
- Test cases are linked via the `ado_case_id` in the YAML file
- Test steps are reported via the `StepLogger`
- Screenshots are attached to failed tests

## Additional Development Information

### Code Style

- Follow PEP 8 guidelines for Python code
- Use descriptive variable and function names
- Add docstrings to classes and methods
- Use type hints where appropriate

### Page Object Pattern

The project follows the Page Object pattern for UI testing:
- Each page or component has a corresponding page object class
- Page objects encapsulate the page structure and behavior
- Tests interact with the application through page objects

### Logging

- Use the `HitlLogger` for application logging
- Use the `StepLogger` for test step logging
- Log messages should be descriptive and include relevant information

### Error Handling

- Use try/except blocks to handle expected exceptions
- Use the `handle_exception` utility for consistent exception handling
- Use assertions for test validations

### Database Access

- Use the DAO (Data Access Object) pattern for database access
- Use SQLAlchemy for database operations
- Use the `get_engine()` function to get a database connection

### Test Data Management

- Separate test data from test logic using YAML files
- Use the `test_data` section in YAML files for test-specific data
- Use the `meta.get("test_data")` pattern to access test data in tests
