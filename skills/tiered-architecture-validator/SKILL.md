---
name: tiered-architecture-validator
description: Validate Tiered Clean Architecture compliance for Python modules. Use when user says "check architecture", "validate tiers", "verify dependencies", "check tier violations", or when implementing new modules. Ensures unidirectional dependencies (higher tiers → lower tiers only), validates function classification (A/B/C/D types), and checks CLAUDE.md compliance.
---

# Tiered Architecture Validator

Validate that code follows the project's Tiered Clean Architecture with proper dependency flow and function classification.

## Instructions

When validating architecture:

### 1. Understand Tier System

**Tier 0 (T0)** - Core Domain:
- **Files**: `structs.py`, `algorithms.py`, `config.py`, `utils.py`
- **Purpose**: Pure domain logic, no dependencies
- **Rules**: NO internal dependencies, only standard library + external packages
- **Examples**: Data structures, pure algorithms, config schemas

**Tier 1 (T1)** - Application Services:
- **Files**: `dataloaders.py`, `plotting.py`, `*_api.py`
- **Purpose**: Application services using T0
- **Rules**: Can depend on T0 only (not other T1 or higher)
- **Examples**: Data loading, visualization, API interfaces

**Tier 2 (T2)** - Orchestration:
- **Files**: `train_fit.py`, `inference.py`, `evaluate.py`
- **Purpose**: Orchestration combining T0+T1
- **Rules**: Can depend on T0 and T1 (not other T2 or T3)
- **Examples**: Training workflows, inference pipelines, evaluation

**Tier 3 (T3)** - External Interfaces:
- **Files**: `experiment.py`, `main.py`, `etl/`, `tests/`, `notebooks/`
- **Purpose**: External interfaces, highest level
- **Rules**: Can depend on any tier
- **Examples**: End-to-end workflows, CLI, ETL, tests, notebooks

### 2. Check Import Dependencies

For each file, verify:

```python
# VALID: T1 imports from T0
from src.module.structs import DataClass  # T0
from src.module.dataloaders import load  # T1 (same tier - OK within module)

# INVALID: T0 imports from T1
from src.module.dataloaders import load  # VIOLATION!

# INVALID: T1 imports from T2
from src.module.train_fit import train  # VIOLATION!

# VALID: T3 imports from any tier
from src.module.structs import DataClass  # T0
from src.module.dataloaders import load  # T1
from src.module.train_fit import train  # T2
```

### 3. Validate Function Classification

Each function must be classified (A/B/C/D):

| Class | Purpose | Typing | Docstring | Tests | Naming |
|-------|---------|--------|-----------|-------|--------|
| **A: Public External** | Called from outside module | Full | Detailed | Required | Clean, e.g. `predict_molecules` |
| **B: Public Internal** | Called within module | Full | Basic | Required | Descriptive, e.g. `predict_molecules_by_consensus` |
| **C: Private Module** | Internal helpers | Optional | Simple | Encouraged | Underscore prefix, e.g. `_predict_internal` |
| **D: Private Sub-Module** | Sub-module helpers | Optional | Optional | Optional | Underscore prefix, short, e.g. `_calc` |

**Validation checks**:
- Class A/B: Must have type hints and docstrings
- Class A: Must have tests
- Class C/D: Should have underscore prefix

### 4. Check File Organization

Per CLAUDE.md guidelines:

```
src/module/
  structs.py           # T0: Dataclasses, types
  algorithms.py        # T0: Pure functions
  config.py            # T0: Config schema + loader
  utils.py             # T0: Small helpers
  dataloaders.py       # T1: GCS/BQ I/O
  plotting.py          # T1: Visualizations
  *_api.py             # T1: API interfaces
  train_fit.py         # T2: Training orchestration
  inference.py         # T2: Inference orchestration
  evaluate.py          # T2: Evaluation orchestration
  experiment.py        # T3: End-to-end workflows
  main.py              # T3: CLI entry point
  etl/                 # T3: Data pipelines (subdirectory)
  tests/               # T3: Tests (subdirectory)
  notebooks/           # T3: Analysis (subdirectory)
  CLAUDE.md            # Architecture documentation
```

**Rules**:
- Prefer files over directories (unless >3000 lines)
- Always make `etl/`, `tests/`, `notebooks/` directories
- Each subdirectory gets its own CLAUDE.md

### 5. Validate CLAUDE.md

Check that CLAUDE.md exists and contains:

```markdown
# Module Name

Brief description of purpose.

## Module Architecture (Tiered Clean Architecture)

### Tier 0: Core Domain (No Dependencies)
- **structs.py**: Purpose
- **algorithms.py**: Purpose
...

### Tier 1: Application Services
- **dataloaders.py**: Purpose
...

[Rest of documentation]
```

### 6. Report Violations

Generate a report like:

```
❌ TIER VIOLATIONS
- train_fit.py (T2) imports from inference.py (T2) - same tier import!
- structs.py (T0) imports from dataloaders.py (T1) - upward dependency!

❌ FUNCTION CLASSIFICATION ISSUES
- predict_molecules() (Class A): Missing docstring
- _helper_func() (Class C): Missing underscore prefix
- process_data() (Class B): Missing type hints

❌ FILE ORGANIZATION
- Missing CLAUDE.md in src/module/
- tests/ directory should exist (currently missing)
- config_loader.py belongs in T0, not T1

✅ VALID
- All T3 files correctly import from lower tiers
- Docstring coverage: 95%
- Type hint coverage: 90%
```

### 7. Suggest Fixes

For each violation, suggest:

```markdown
### Fix tier violation in train_fit.py

**Problem**: Imports from same tier (inference.py)

**Solution**: Extract shared code to T0 or T1:

```python
# NEW: structs.py (T0)
@dataclass
class SharedConfig:
    param1: int
    param2: float

# train_fit.py (T2)
from src.module.structs import SharedConfig  # ✅ Valid

# inference.py (T2)
from src.module.structs import SharedConfig  # ✅ Valid
```

## Validation Workflow

1. **Read CLAUDE.md** - Understand module's intended architecture
2. **Scan files** - Identify tier for each file
3. **Check imports** - Verify dependencies follow tier rules
4. **Validate functions** - Check classification and documentation
5. **Report issues** - Generate violation report
6. **Suggest fixes** - Provide concrete refactoring suggestions

## When to Use This Skill

- Implementing new modules (before writing code)
- Reviewing pull requests
- Refactoring existing code
- User asks to "check architecture" or "validate tiers"
- After significant code changes
- When imports feel "wrong" or circular

## Common Violations and Fixes

**Violation**: T0 importing from T1
```python
# WRONG: structs.py importing from dataloaders
from src.module.dataloaders import load_data
```
**Fix**: Move shared code to T0 or pass data as parameter

**Violation**: T1 importing from T2
```python
# WRONG: dataloaders.py importing from train_fit
from src.module.train_fit import preprocess
```
**Fix**: Move preprocessing to T1 (`dataloaders.py` or new `preprocessing.py`)

**Violation**: Same-tier import
```python
# WRONG: train_fit.py importing from inference.py (both T2)
from src.module.inference import predict
```
**Fix**: Extract shared logic to T0 or T1

## Project-Specific Rules

- Absolute imports only (no relative imports)
- Tiered Architecture is mandatory for all `src/` code
- sandbox/ code can be more flexible but should document deviations
- CLAUDE.md is required for each module
- Every subdirectory needs its own CLAUDE.md
