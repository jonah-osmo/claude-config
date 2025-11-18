---
name: python-module-refactoring
description: Safely split large Python files into focused modules while preserving all functionality. Automatically handles import dependencies, BUILD.bazel updates, test imports, and static analysis verification. Use when refactoring monolithic Python files, splitting modules, or reorganizing Python packages.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# Python Module Refactoring Skill

Safely refactor large Python files into smaller, focused modules while ensuring no functionality is broken.

## Core Capabilities

1. **Dependency Analysis**: Scan each function/class to identify all required imports
2. **Smart Import Extraction**: Copy necessary imports to new module files
3. **BUILD.bazel Sync**: Update Bazel targets and dependencies automatically
4. **Test Migration**: Update test imports to use new package structure
5. **Backward Compatibility**: Generate __init__.py with re-exports
6. **Verification**: Run static analysis and import checks

## When to Use This Skill

Activate this skill when:
- Splitting a large Python file (>1000 lines) into smaller modules
- Refactoring a monolithic module into a package structure
- Reorganizing Python code while maintaining backward compatibility
- User mentions "refactor", "split module", "reorganize", or "extract to separate file"

## Refactoring Workflow

### Phase 1: Analysis

1. **Read the target file** to understand structure
2. **Identify logical groupings** of functions/classes:
   - Group by functionality (e.g., parsing, display, commands)
   - Group by domain concepts (e.g., state, library, query)
   - Consider dependencies between groups
3. **Map import usage** for each group:
   - Scan function bodies for all module/function references
   - Note standard library imports (os, sys, typing, etc.)
   - Note third-party imports (pandas, numpy, rich, etc.)
   - Note internal project imports
4. **Check BUILD.bazel** to understand current dependencies

### Phase 2: Plan

Create a refactoring plan that includes:
- New module names and their purpose
- Functions/classes assigned to each module
- Required imports for each module
- BUILD.bazel target structure
- __init__.py re-export strategy

**Present this plan to the user for approval before proceeding.**

### Phase 3: Execution

For each new module:

1. **Create module file** with proper header:
   ```python
   """
   Module purpose and description.

   Key functions:
   - function1: Description
   - function2: Description
   """
   ```

2. **Add ALL required imports**:
   - Standard library imports first
   - Third-party imports second (alphabetically)
   - Internal project imports third (alphabetically)
   - **CRITICAL**: Scan the extracted code for ALL module references
   - Include imports even if they seem indirect (e.g., `box` used in table creation)

3. **Copy functions/classes** with exact indentation and formatting

4. **Create __init__.py** that re-exports the public API:
   ```python
   """Package description."""

   from .module1 import func1, func2
   from .module2 import func3, func4

   __all__ = ["func1", "func2", "func3", "func4"]
   ```

### Phase 4: BUILD.bazel Updates

1. **Create granular library targets** for each new module:
   ```python
   py_library(
       name = "module_name",
       srcs = ["package/module_name.py"],
       visibility = ["//visibility:public"],
       deps = [
           # Internal deps
           ":other_module",
           "//src/path/to:dependency",
           # External deps
           requirement("pandas"),
           requirement("numpy"),
       ],
   )
   ```

2. **Update main package target** to depend on submodules:
   ```python
   py_library(
       name = "package",
       srcs = ["package/__init__.py"],
       visibility = ["//visibility:public"],
       deps = [
           ":module1",
           ":module2",
           # ... all submodules
       ],
   )
   ```

3. **Update any test targets** that reference the old module:
   - Change imports to use new package structure
   - Add dependencies on new submodule targets

### Phase 5: Test Updates

For each test file that imports from the refactored module:

1. **Replace old imports**:
   ```python
   # OLD
   from module import func1, func2

   # NEW
   from package import func1, func2
   # OR
   from package.module1 import func1
   ```

2. **Update mock/patch targets**:
   ```python
   # OLD
   @patch.object(old_module, 'console')

   # NEW
   @patch.object(new_package.submodule, 'console')
   ```

3. **Update module references** for patching:
   ```python
   import package.submodule as submodule

   @patch.object(submodule, 'function')
   ```

### Phase 6: Verification

Run comprehensive verification:

1. **Static analysis** on all new modules:
   ```bash
   python -m py_compile /path/to/package/module1.py
   python -m py_compile /path/to/package/module2.py
   python -m py_compile /path/to/package/__init__.py
   ```

2. **Import verification**:
   ```bash
   python -c "from package import func1, func2; print('Success')"
   ```

3. **Test execution** (if applicable):
   ```bash
   bazelisk test //path/to:test_target
   ```

4. **Check for missing imports**:
   - Read test output for ImportError or NameError
   - Common culprits: `box`, `webbrowser`, `filesystem as fs`
   - Add any missing imports immediately

## Common Import Pitfalls

### Rich Console Components
When refactoring code using the `rich` library:
```python
from rich import box  # For table styling
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
```

### Filesystem Operations
```python
from src.common.io import filesystem as fs  # Often aliased
```

### Web Operations
```python
import webbrowser  # For opening URLs
```

### Standard Library Utilities
```python
import os
import sys
import tempfile
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass
```

## BUILD.bazel Patterns

### Python Library Target Template
```python
py_library(
    name = "target_name",
    srcs = ["path/to/file.py"],
    visibility = ["//visibility:public"],  # or restrict as needed
    deps = [
        # Internal dependencies (alphabetically)
        ":other_local_target",
        "//src/common/io:filesystem",
        "//src/common/utils:helpers",
        # External dependencies (alphabetically)
        requirement("loguru"),
        requirement("pandas"),
        requirement("rich"),
    ],
)
```

### Test Target Updates
```python
pytest_test(
    name = "test_name",
    srcs = ["tests/test_file.py"],
    deps = [
        ":package",  # Main package target
        ":submodule1",  # If directly testing submodule
        ":submodule2",
        requirement("pytest"),
    ],
)
```

## Error Recovery

If verification fails:

1. **Read error messages carefully** - they usually indicate missing imports
2. **Search the new module** for the symbol that caused the error
3. **Trace back to original file** to find where it was imported
4. **Add the missing import** to the new module file
5. **Re-run verification**

Common error patterns:
- `NameError: name 'X' is not defined` → Missing import for X
- `ModuleNotFoundError: No module named 'X'` → Missing BUILD.bazel dependency
- `ImportError: cannot import name 'X'` → Function not in __init__.py or wrong module

## Best Practices

1. **Always read the entire original file** before planning the refactor
2. **Grep for symbol usage** when unsure about dependencies
3. **Maintain alphabetical import ordering** for consistency
4. **Keep related functionality together** in the same module
5. **Minimize circular dependencies** between new modules
6. **Test incrementally** - verify each module as it's created
7. **Document module purposes** in docstrings
8. **Preserve git history** by using `git mv` when appropriate (though not always possible for splits)

## Example Refactoring

**Original**: `interactivity.py` (2,359 lines)

**New Structure**:
```
interactivity/
├── __init__.py (re-exports public API)
├── input_parsing.py (115 lines) - Parse user input, format names
├── display_utils.py (412 lines) - Rich console utilities
├── inspection_commands.py (685 lines) - Material/structure inspection
├── iteration_display.py (700 lines) - State display, visualizations
└── command_parser.py (540 lines) - Main command loop
```

**Key Lessons from Real Refactoring**:
- Initially missed `from rich import box` → caused table formatting to fail
- Initially missed `import webbrowser` → caused plot auto-open to fail
- Initially missed `from src.common.io import filesystem as fs` → caused EXIT commands to fail

## Troubleshooting

### "The module works but tests fail"
- Check if tests are patching the correct module path
- Update `@patch.object(old_module, ...)` to `@patch.object(new_package.submodule, ...)`

### "Static analysis passes but runtime fails"
- Some imports are only used at runtime (dynamic imports, type checking)
- Run the actual code, not just static checks

### "Circular import detected"
- Refactor to move shared code to a separate module
- Use TYPE_CHECKING guards for type hints
- Consider lazy imports inside functions

## Version History

- v1.0 (2025-11-18): Initial skill creation based on interactivity.py refactoring experience
