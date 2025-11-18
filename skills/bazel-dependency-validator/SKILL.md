---
name: bazel-dependency-validator
description: Validate that BUILD.bazel dependencies match actual Python imports. Identifies missing requirement() declarations and internal //path/to:target deps. Use when BUILD.bazel tests fail with import errors, after refactoring Python modules, or when user mentions "bazel dependencies", "BUILD.bazel", or import/dependency issues.
allowed-tools: Read, Grep, Glob, Bash
---

# Bazel Dependency Validator Skill

Ensure BUILD.bazel files correctly declare all dependencies used by Python source files.

## Core Capabilities

1. **Import Scanning**: Extract all imports from Python source files
2. **Dependency Mapping**: Map imports to Bazel requirement() and internal targets
3. **Missing Detection**: Identify undeclared dependencies in BUILD.bazel
4. **Fix Suggestions**: Provide exact BUILD.bazel syntax for missing deps
5. **Validation**: Verify fixes with bazelisk query/build

## When to Use This Skill

Activate when:
- Bazel tests fail with `ModuleNotFoundError` or `ImportError`
- After refactoring Python modules or packages
- Creating new BUILD.bazel files
- User mentions "missing dependency", "BUILD.bazel", "bazel test fails", or "import error"

## Validation Workflow

### Phase 1: Identify Scope

Determine what to validate:
- Single Python file → Check its py_library target
- Python package → Check all py_library targets in directory
- Test failures → Focus on failing test's deps
- Whole project → Validate all BUILD.bazel files (use sparingly)

### Phase 2: Extract Imports

For each Python file:

1. **Read the file** to get all import statements
2. **Categorize imports**:
   - **Standard library**: `import os`, `from typing import List`
   - **Third-party**: `import pandas`, `from rich.console import Console`
   - **Internal project**: `from src.common.io import filesystem`
   - **Relative imports**: `from .submodule import func`

3. **Normalize import names**:
   - `import pandas as pd` → `pandas`
   - `from rich.console import Console` → `rich`
   - `from src.common.io import filesystem` → `src.common.io.filesystem`

### Phase 3: Map to Bazel Dependencies

For each import category:

**Third-party packages** → `requirement("package_name")`
```python
import pandas → requirement("pandas")
import numpy → requirement("numpy")
from rich.console import Console → requirement("rich")
import plotly.graph_objects → requirement("plotly")
from loguru import logger → requirement("loguru")
```

**Internal project imports** → `"//src/path/to:target_name"`
```python
from src.common.io import filesystem → "//src/common/io:filesystem"
from src.sandbox.jonah.utils import gcs_utils → "//src/sandbox/jonah/utils:gcs_utils"
from src.research.gcms_api import algorithms → "//src/research/gcms_api:algorithms"
```

**Local package imports** → `:target_name`
```python
from .structs import Action → ":structs"
from . import config_loader → ":config_loader"
```

### Phase 4: Read BUILD.bazel

1. **Find BUILD.bazel** in the same directory as the Python file
2. **Extract the relevant target**:
   ```python
   py_library(
       name = "target_name",
       srcs = ["file.py"],
       deps = [
           # List of dependencies
       ],
   )
   ```
3. **Parse existing deps** into a set for comparison

### Phase 5: Compare and Report

For each required dependency:

1. **Check if declared** in BUILD.bazel deps list
2. **If missing**:
   - Add to missing_deps list
   - Generate fix suggestion with exact syntax
   - Note the import source (file:line)

Generate report:
```
Missing Dependencies for //src/path/to:target_name

File: src/path/to/file.py

Missing third-party dependencies:
  - requirement("plotly")  # from: import plotly.graph_objects (line 36)
  - requirement("loguru")  # from: from loguru import logger (line 38)

Missing internal dependencies:
  - "//src/sandbox/jonah/utils:gcs_utils"  # from: from src.sandbox.jonah.utils import gcs_utils (line 46)
  - "//src/research/gcms_api:algorithms"  # from: from src.research.gcms_api import algorithms (line 105)

Suggested fix for BUILD.bazel:
[Show complete deps block with additions]
```

### Phase 6: Apply Fixes

If user approves:

1. **Edit BUILD.bazel** to add missing dependencies
2. **Maintain alphabetical ordering**:
   - Internal deps first (alphabetically)
   - External deps second (alphabetically)
3. **Preserve formatting** and comments

### Phase 7: Verification

Verify fixes work:

```bash
# Build the target
bazelisk build //src/path/to:target_name

# Or run tests
bazelisk test //src/path/to:test_target

# Query dependencies
bazelisk query 'deps(//src/path/to:target_name)'
```

## Import → Bazel Mapping Reference

### Common Third-Party Packages

| Python Import | Bazel Requirement |
|---------------|-------------------|
| `import pandas` | `requirement("pandas")` |
| `import numpy` | `requirement("numpy")` |
| `from rich.console import Console` | `requirement("rich")` |
| `import plotly.graph_objects` | `requirement("plotly")` |
| `from loguru import logger` | `requirement("loguru")` |
| `import matplotlib.pyplot` | `requirement("matplotlib")` |
| `import torch` | `requirement("torch")` |
| `from frozendict import frozendict` | `requirement("frozendict")` |
| `import cvxpy` | `requirement("cvxpy")` |
| `from sklearn import ...` | `requirement("scikit-learn")` |

### Internal Project Patterns

| Python Import Pattern | Bazel Dependency Pattern |
|-----------------------|--------------------------|
| `from src.common.io import filesystem` | `"//src/common/io:filesystem"` |
| `from src.common.io.filesystem import ...` | `"//src/common/io:filesystem"` |
| `from src.research.gcms_api import ...` | `"//src/research/gcms_api:MODULE_NAME"` |
| `from .submodule import func` | `":submodule"` |

**Note**: For internal imports, the target name is usually the module name, but check the actual BUILD.bazel in that directory.

### Standard Library (No Dependency Needed)

These imports don't require BUILD.bazel deps:
- `import os`, `import sys`, `import typing`, `import json`, `import re`
- `import tempfile`, `import datetime`, `import pathlib`
- `from typing import List, Dict, Optional, Tuple`
- `from dataclasses import dataclass`
- `from collections import defaultdict`
- `import unittest`, `from unittest.mock import Mock`

## Common Issues

### Missing BUILD.bazel File

If no BUILD.bazel exists in the directory:

1. **Check parent directories** - maybe it's in a parent package
2. **Create BUILD.bazel** if this is a new package
3. **Use standard template**:

```python
load("@aspect_rules_py//py:defs.bzl", "py_library", "py_binary")
load("@pip//:requirements.bzl", "requirement")
load("//tools/pytest:defs.bzl", "pytest_test")

py_library(
    name = "module_name",
    srcs = ["module_name.py"],
    visibility = ["//visibility:public"],
    deps = [
        # Dependencies will be added here
    ],
)
```

### Ambiguous Internal Imports

When `from src.package import something` could be a module or class:

1. **Read the source** to determine what `something` is
2. **Check BUILD.bazel** in `src/package/` to see available targets
3. **Use Bazel query** to find targets:
   ```bash
   bazelisk query //src/package/...
   ```

### Transitive Dependencies

If code works without declaring a dep (because another dep provides it):

1. **Still declare it explicitly** - don't rely on transitive deps
2. **Bazel may break** if the intermediate dep removes it
3. **Better to be explicit** for maintenance

## Real-World Examples

### Example 1: viz_action.py Missing plotly

**Scan results**:
```python
# viz_action.py line 36
import plotly.graph_objects as go
```

**BUILD.bazel check**:
```python
py_library(
    name = "viz_action",
    srcs = ["viz_action.py"],
    deps = [
        ":structs",
        ":viz_utils",
        requirement("pandas"),
        requirement("matplotlib"),
        # Missing: requirement("plotly")
    ],
)
```

**Fix**:
```python
py_library(
    name = "viz_action",
    srcs = ["viz_action.py"],
    deps = [
        ":structs",
        ":viz_utils",
        requirement("pandas"),
        requirement("matplotlib"),
        requirement("plotly"),  # ADDED
    ],
)
```

### Example 2: test_forced_ilp_constraints Missing Module Dep

**Scan results**:
```python
# test_forced_ilp_constraints.py line 19
from src.sandbox.jonah.iterative_deform.sls_ilp_match import solve_ilp_assignments_df
```

**BUILD.bazel check**:
```python
pytest_test(
    name = "test_forced_ilp_constraints",
    srcs = ["tests/test_forced_ilp_constraints.py"],
    deps = [
        ":structs",
        requirement("pandas"),
        # Missing: ":sls_ilp_match"
    ],
)
```

**Fix**:
```python
pytest_test(
    name = "test_forced_ilp_constraints",
    srcs = ["tests/test_forced_ilp_constraints.py"],
    deps = [
        ":sls_ilp_match",  # ADDED
        ":structs",
        requirement("pandas"),
    ],
)
```

## Automation Script Template

For large-scale validation, generate a script:

```bash
#!/bin/bash
# validate_bazel_deps.sh

# Find all Python files
PYTHON_FILES=$(find src -name "*.py" -type f)

for file in $PYTHON_FILES; do
    # Extract imports
    imports=$(grep -E "^import |^from " "$file" | sort -u)

    # Find corresponding BUILD.bazel
    dir=$(dirname "$file")
    build_file="$dir/BUILD.bazel"

    if [ -f "$build_file" ]; then
        # Check each import against BUILD deps
        # (This is a simplified template - actual implementation would be more complex)
        echo "Checking $file..."
    fi
done
```

## Best Practices

1. **Run validation after refactoring** - catches missing deps immediately
2. **Check both py_library and pytest_test targets** - tests need deps too
3. **Use Bazel's own error messages** - they often tell you the missing dep
4. **Keep deps alphabetically sorted** - easier to spot duplicates and gaps
5. **Document why unusual deps are needed** - use comments in BUILD.bazel
6. **Validate before committing** - prevent CI failures

## Troubleshooting

### "Bazel says the dep doesn't exist"

Check if the target is actually defined:
```bash
bazelisk query //src/path/to:target_name
```

If it doesn't exist, you may need to:
- Create a BUILD.bazel in that directory
- Use a different target name (check the BUILD.bazel there)

### "Dep is declared but import still fails"

Possible causes:
- Wrong target name (check the actual BUILD.bazel)
- Circular dependency (Bazel will error about this)
- Target visibility restrictions (make it `//visibility:public`)

### "Too many false positives"

Some imports are conditional or guarded:
```python
if TYPE_CHECKING:
    from typing import Protocol  # Don't need runtime dep
```

For these, you can skip adding deps or use comments:
```python
deps = [
    # Note: typing.Protocol used only for type checking
]
```

## Version History

- v1.0 (2025-11-18): Initial skill creation based on BUILD.bazel dependency issues
