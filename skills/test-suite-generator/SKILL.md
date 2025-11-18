---
name: test-suite-generator
description: Auto-generate comprehensive pytest test suites for Python modules. Use when user says "generate tests", "write test suite", "create comprehensive tests", "add test coverage", or "test this code". Creates 50+ tests covering happy path, edge cases, error handling, type variations, and real-world scenarios. Follows project patterns with fixtures, parametrize, and mocking.
---

# Test Suite Generator

Generate comprehensive pytest test suites that follow project conventions and achieve high code coverage.

## Instructions

When generating test suites:

### 1. Analyze the Target Code

- Read the module/function to understand functionality
- Identify all code paths, edge cases, and error conditions
- Note parameter types, return values, and side effects
- Check for existing tests to understand patterns

### 2. Organize Test Structure

Create test classes by functionality:

```python
class TestBasicFunctionality:
    """Test core happy path scenarios."""
    pass

class TestEdgeCases:
    """Test boundary conditions and special inputs."""
    pass

class TestErrorHandling:
    """Test error conditions and exceptions."""
    pass

class TestIntegration:
    """Test interactions with other components."""
    pass
```

### 3. Generate Comprehensive Test Cases

For EACH function/method, create tests for:

**Happy Path (3-5 tests)**:
- Simple valid input
- Multiple valid inputs
- Real-world usage examples

**Edge Cases (5-10 tests)**:
- Empty inputs (empty string, empty list, None)
- Single item vs multiple items
- Boundary values (0, -1, max int)
- Special characters, whitespace
- Type variations (int vs float, list vs tuple)

**Error Handling (3-5 tests)**:
- Invalid types
- Invalid values
- Missing required parameters
- Exceptions and error messages

**Real-World Scenarios (5-10 tests)**:
- Actual use cases from the codebase
- Integration with other modules
- Complex workflows

### 4. Follow Project Patterns

**Fixtures** (if needed):
```python
@pytest.fixture
def sample_data():
    """Common test data."""
    return {...}
```

**Parametrize** for similar tests:
```python
@pytest.mark.parametrize("input,expected", [
    ("", []),
    ("a", ["a"]),
    ("a,b,c", ["a", "b", "c"]),
])
def test_comma_list_variants(input, expected):
    result = parse_comma_list(input)
    assert result == expected
```

**Mocking** for external dependencies:
```python
@patch("module.external_function")
def test_with_mock(mock_external):
    mock_external.return_value = "mocked"
    # ... test code
```

### 5. Test Naming Convention

Use descriptive names that explain what is being tested:
- `test_function_name_with_valid_input()`
- `test_function_name_with_empty_string()`
- `test_function_name_raises_error_on_invalid_type()`

### 6. Coverage Goals

Aim for:
- **60+ tests** for new modules
- **>90% code coverage** for critical paths
- **All error paths** tested
- **All edge cases** covered

### 7. BUILD.bazel Integration

Add test target to `BUILD.bazel`:

```python
pytest_test(
    name = "test_module_name",
    size = "small",  # or "medium", "large"
    srcs = ["test_module_name.py"],
    deps = [
        "//path/to:module",
        requirement("pytest"),
        # ... other deps
    ],
)
```

## Example Output Structure

```python
"""
Comprehensive tests for module_name.

Tests cover:
- Basic functionality (20 tests)
- Edge cases (15 tests)
- Error handling (10 tests)
- Integration (15 tests)

Total: 60+ tests
"""

import pytest
from unittest.mock import Mock, patch

# Fixtures
@pytest.fixture
def sample_data():
    return {...}

# Test Classes
class TestBasicFunctionality:
    def test_simple_case(self):
        ...

    def test_multiple_values(self):
        ...

class TestEdgeCases:
    def test_empty_input(self):
        ...

    @pytest.mark.parametrize("input,expected", [...])
    def test_variants(self, input, expected):
        ...

class TestErrorHandling:
    def test_invalid_type_raises_error(self):
        with pytest.raises(TypeError):
            ...

class TestIntegration:
    @patch("module.dependency")
    def test_with_mocked_dependency(self, mock_dep):
        ...
```

## When to Use This Skill

- User requests "write tests" for a module
- New code needs test coverage
- Refactoring requires regression tests
- Improving code quality with comprehensive testing
- CI/CD requires higher test coverage

## Project-Specific Notes

- Use `@pip//:requirements.bzl` (not `@pip_deps`) in BUILD files
- Follow `pytest_test` convention from `//tools/pytest:defs.bzl`
- Test files should be `test_*.py` co-located with source
- Use `requirement("pytest")` for pytest dependency (already auto-included)
