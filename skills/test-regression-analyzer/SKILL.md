---
name: test-regression-analyzer
description: Compare test results before and after code changes to identify newly failing tests, newly passing tests, and unchanged tests. Provides root cause analysis for new failures with log excerpts. Use when validating refactoring, investigating test failures, or when user mentions "test regression", "which tests broke", or "compare test results".
allowed-tools: Read, Bash, Grep, Glob
---

# Test Regression Analyzer Skill

Compare test results before and after changes to identify regressions and improvements.

## Core Capabilities

1. **Baseline Capture**: Record test results before changes
2. **Post-Change Testing**: Run tests after changes
3. **Diff Analysis**: Categorize test result changes
4. **Root Cause Analysis**: Investigate newly failing tests
5. **Report Generation**: Create comprehensive comparison report

## When to Use This Skill

Activate when:
- Validating refactoring didn't break tests
- Investigating which tests failed after changes
- User provides baseline test results for comparison
- User mentions "test regression", "which tests broke", "compare tests", or "test diff"

## Workflow

### Phase 1: Understand the Baseline

If user provides baseline results:

1. **Parse provided results** into structured data:
   ```
   Passing: [test1, test2, test3]
   Failing: {
       test4: "error_type",
       test5: "error_type"
   }
   ```

If no baseline provided:

1. **Run tests on baseline commit**:
   ```bash
   git stash  # Save current changes
   bazelisk test //path/to/...
   # Record results
   git stash pop  # Restore changes
   ```

2. **Parse test output** to extract:
   - Test names
   - Pass/fail status
   - Error types for failures
   - Test counts

### Phase 2: Run Current Tests

1. **Execute test suite**:
   ```bash
   bazelisk test //path/to/... --test_output=summary
   ```

2. **Capture results**:
   - Test names
   - Pass/fail status
   - Error messages/types
   - Log file paths

3. **Parse output** into structured format

### Phase 3: Categorize Changes

Compare baseline vs current and categorize each test:

1. **Newly Failing** (REGRESSION):
   - Passed in baseline, failing now
   - **High priority** - likely caused by recent changes

2. **Newly Passing** (IMPROVEMENT):
   - Failed in baseline, passing now
   - Good news - changes fixed something

3. **Still Failing** (PRE-EXISTING):
   - Failed in baseline, still failing
   - Not caused by recent changes
   - May be unrelated issues

4. **Still Passing** (STABLE):
   - Passed in baseline, still passing
   - Changes didn't break these

### Phase 4: Root Cause Analysis (Newly Failing Only)

For each newly failing test:

1. **Read test log file**:
   ```bash
   cat /path/to/test.log
   ```

2. **Extract error information**:
   - Error type (ImportError, AssertionError, etc.)
   - Error message
   - Stack trace
   - Relevant code lines

3. **Identify failure pattern**:
   - **Import errors**: Missing dependencies, renamed modules
   - **Assertion errors**: Behavior changes, incorrect mocks
   - **AttributeErrors**: Missing attributes, API changes
   - **NameErrors**: Missing imports, scoping issues

4. **Link to recent changes**:
   - Did a refactoring move/rename this module?
   - Were imports changed?
   - Was BUILD.bazel modified?

5. **Suggest fix** based on pattern

### Phase 5: Generate Report

Create comprehensive report:

```markdown
# Test Regression Analysis

## Summary
- Total tests: X
- Newly failing: Y (REGRESSIONS)
- Newly passing: Z (IMPROVEMENTS)
- Still failing: A (PRE-EXISTING)
- Still passing: B (STABLE)

## Status: [PASS/FAIL/MIXED]

## Detailed Results

### Newly Failing Tests (REGRESSIONS) ⚠️
[List each with error summary and suggested fix]

### Newly Passing Tests (IMPROVEMENTS) ✅
[List each]

### Still Failing Tests (PRE-EXISTING) 📋
[List each with note that these existed before changes]

### Still Passing Tests (STABLE) ✓
[List or count only if relevant]

## Root Cause Analysis

[For each regression, provide:
- Test name
- Error type
- Log excerpt (key lines)
- Likely cause
- Suggested fix
- Relevant file references]

## Recommendations

[Action items prioritized by severity]
```

## Test Output Parsing Patterns

### Bazel Test Summary Format

```
INFO: Build completed, X tests FAILED, Y total actions
//path/to:test1                                   PASSED in 2.3s
//path/to:test2                                   FAILED in 1.5s
  /path/to/logs/test2/test.log
//path/to:test3                                   PASSED in 0.8s
```

Parse this to extract:
- Test target: `//path/to:test1`
- Status: `PASSED` or `FAILED`
- Duration: `2.3s`
- Log path: `/path/to/logs/test2/test.log` (for failures)

### Pytest Output Format

```
============================= test session starts ==============================
collected 42 items

tests/test_example.py::test_func1 PASSED                                [ 50%]
tests/test_example.py::test_func2 FAILED                                [100%]

=================================== FAILURES ===================================
...
```

Parse this to extract:
- Test name: `test_func1`, `test_func2`
- Status: `PASSED`, `FAILED`
- Total collected: `42 items`

## Common Error Patterns and Diagnosis

### ImportError / ModuleNotFoundError

**Pattern**: `ModuleNotFoundError: No module named 'X'`

**Likely causes**:
- Missing BUILD.bazel dependency
- Module was renamed/moved
- Python path issue

**Diagnosis**:
1. Check if module exists: `find . -name "X.py"`
2. Check BUILD.bazel deps list
3. Check import statement in test file

**Fix suggestion**: Add missing dep or update import path

### AttributeError

**Pattern**: `AttributeError: 'X' object has no attribute 'Y'`

**Likely causes**:
- Function/attribute was renamed
- Module structure changed
- Mock configuration outdated

**Diagnosis**:
1. Check if attribute exists in current code
2. Check git diff for renames
3. Check test mocking setup

**Fix suggestion**: Update attribute name or mock configuration

### NameError

**Pattern**: `NameError: name 'X' is not defined`

**Likely causes**:
- Missing import in refactored module
- Variable scoping changed
- Removed global definition

**Diagnosis**:
1. Search for where 'X' should be defined
2. Check if import was lost in refactoring
3. Check module-level definitions

**Fix suggestion**: Add missing import or restore definition

### AssertionError

**Pattern**: `AssertionError: expected X but got Y`

**Likely causes**:
- Actual behavior changed (intended or bug)
- Test expectations outdated
- Mock return values incorrect

**Diagnosis**:
1. Check if change was intentional
2. Review what the code actually does now
3. Verify test expectations are still valid

**Fix suggestion**: Update test expectations or fix code behavior

## Real-World Example

### Scenario: Refactoring interactivity.py

**Baseline** (before refactoring):
```
Passing: 7 tests
- test_active_peak_sorting
- test_assignment_score_integration
- test_composite_score_with_assignments
- test_forced_assignments
- test_ocp_bonus
- test_rewind
- test_solvent_detection

Failing: 5 tests
- test_forced_ilp_constraints (1/26 failed)
- test_id_command_deferred (import error)
- test_interactivity (26/51 failed)
- test_interactivity_cluster_assignment (3/37 failed)
- test_structure_introspection (7/16 failed)
```

**After refactoring**:
```
Passing: 7 tests (same as baseline)
Failing: 5 tests (same as baseline)
```

**Analysis**:
```markdown
# Test Regression Analysis

## Summary
- Total tests: 12
- Newly failing: 0 ✅
- Newly passing: 0
- Still failing: 5 (PRE-EXISTING)
- Still passing: 7 ✅

## Status: PASS (No regressions introduced)

## Conclusion
The refactoring successfully maintained all passing tests.
All failing tests were already failing before the changes.
No new failures were introduced.
```

## Advanced Features

### Comparison Across Commits

Compare test results across multiple commits:

```bash
# Test commit A
git checkout commit_a
bazelisk test //path/to/...
# Record results

# Test commit B
git checkout commit_b
bazelisk test //path/to/...
# Record results

# Compare A vs B
```

### Failure Rate Tracking

Track how often tests fail over time:

```python
test_history = {
    "test_example": {
        "2025-11-15": "FAILED",
        "2025-11-16": "PASSED",
        "2025-11-17": "FAILED",
        "2025-11-18": "PASSED",
    }
}

flakiness_score = failures / total_runs
```

### Log Excerpt Intelligence

Extract the most relevant lines from test logs:

1. **Find the actual error** (last traceback)
2. **Include context** (5 lines before/after)
3. **Highlight key information**:
   - Module names
   - Function names
   - Error messages
   - File paths with line numbers

Example output:
```
test_example.py:42 in test_function
    from module import function
E   ModuleNotFoundError: No module named 'module'

Relevant context:
  Line 40:     # Setup test
  Line 41:     state = create_state()
→ Line 42:     from module import function
  Line 43:     result = function(state)
```

## Integration with CI/CD

### GitHub Actions Integration

```yaml
- name: Run tests and analyze
  run: |
    # Get baseline from main branch
    git fetch origin main
    git checkout origin/main
    bazelisk test //... > baseline.log

    # Test current branch
    git checkout -
    bazelisk test //... > current.log

    # Compare (would invoke this skill)
    python analyze_test_diff.py baseline.log current.log
```

### Automated Regression Detection

Set up to automatically:
1. Run tests on PR
2. Compare against main branch
3. Fail PR if regressions detected
4. Post detailed report as PR comment

## Best Practices

1. **Always establish baseline** - can't detect regression without it
2. **Re-run flaky tests** - ensure failures are consistent
3. **Investigate new failures immediately** - easier to debug fresh changes
4. **Document pre-existing failures** - don't let them accumulate
5. **Track test stability over time** - identify chronically flaky tests
6. **Use structured output** - easier to parse and compare

## Troubleshooting

### "Can't determine which tests are new failures"

- Ensure baseline and current test runs use same test targets
- Check test names match exactly (case-sensitive)
- Verify both runs completed (not interrupted)

### "Too many pre-existing failures to analyze"

- Focus on newly failing tests first
- Consider fixing pre-existing failures separately
- Use filters to analyze only relevant test suites

### "Flaky tests showing as regressions"

- Run tests multiple times to confirm
- Mark known flaky tests in documentation
- Consider quarantining flaky tests

## Version History

- v1.0 (2025-11-18): Initial skill creation based on refactoring validation experience
