# Tests Directory

This directory contains all test files, demo scripts, and examples for QReviewer.

## Structure

```
tests/
├── test_*.py                     # Unit and integration tests
├── demo_*.py                     # Demonstration scripts
├── demo_*.json                   # Demo data files
├── README.md                     # This file
└── fixtures/                     # Test fixtures (if needed)
```

## Test Files

### Core Tests
- **`test_basic.py`** - Basic functionality tests
- **`test_api_comprehensive.py`** - Complete API endpoint testing
- **`test_api_demo.py`** - API demonstration tests
- **`test_inline_comments.py`** - GitHub inline comment functionality
- **`test_standards_demo.py`** - Standards management testing

### AI Learning Tests
- **`test_ai_learning.py`** - Basic AI learning functionality
- **`test_ai_learning_real.py`** - Real repository learning tests
- **`test_module_learning.py`** - Module-focused learning tests

## Demo Files

### Scripts
- **`demo.py`** - Basic demonstration
- **`demo_ai_learning_workflow.py`** - Complete AI learning workflow demo

### Data Files
- **`demo-findings.json`** - Example findings data
- **`demo-pr-diff.json`** - Example PR diff data
- **`demo_real_pr_response.json`** - Real PR response example

## Running Tests

```bash
# Run all tests from project root
pytest tests/

# Run specific test file
pytest tests/test_api_comprehensive.py

# Run with coverage
pytest tests/ --cov=qrev

# Run specific test
pytest tests/test_api_comprehensive.py::TestReviewEndpoint::test_review_endpoint_success
```

## Running Demos

```bash
# Run AI learning workflow demo
python tests/demo_ai_learning_workflow.py

# Run basic demo
python tests/demo.py

# Run module learning test
python tests/test_module_learning.py
```

## Adding New Tests

1. **Follow naming convention**: `test_*.py` for tests, `demo_*.py` for demos
2. **Use descriptive names**: Make test names clear about what they test
3. **Include docstrings**: Document what each test/demo does
4. **Add to appropriate category**: Group related tests together

## Test Data

- **Fixtures**: Use `tests/fixtures/` for reusable test data
- **Demo files**: Keep demo data files in this directory
- **Cleanup**: Tests should clean up after themselves
- **Isolation**: Tests should not depend on each other

## Best Practices

1. **Test isolation**: Each test should be independent
2. **Meaningful assertions**: Test specific behaviors, not implementation details
3. **Clear naming**: Test names should describe the scenario being tested
4. **Documentation**: Include docstrings explaining test purpose
5. **Coverage**: Aim for comprehensive test coverage of new features
