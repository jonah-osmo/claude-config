# Tiered Architecture Reference

Complete reference for the Osmo project's Tiered Clean Architecture.

## Tier Dependency Matrix

| From Tier | Can Import T0 | Can Import T1 | Can Import T2 | Can Import T3 |
|-----------|---------------|---------------|---------------|---------------|
| **T0**    | ❌ No         | ❌ No         | ❌ No         | ❌ No         |
| **T1**    | ✅ Yes        | ⚠️  Same tier  | ❌ No         | ❌ No         |
| **T2**    | ✅ Yes        | ✅ Yes        | ⚠️  Same tier  | ❌ No         |
| **T3**    | ✅ Yes        | ✅ Yes        | ✅ Yes        | ⚠️  Same tier  |

**Note**: Same-tier imports should be minimized. Extract shared code to lower tier instead.

## Standard File Names by Tier

### Tier 0 (Core Domain)
- `structs.py` - Data structures, dataclasses, types
- `algorithms.py` - Pure functions, business logic
- `config.py` - Configuration schemas and loaders
- `utils.py` - Small utility functions
- `misc.py` - Miscellaneous helpers

### Tier 1 (Application Services)
- `dataloaders.py` - Data loading (GCS, BigQuery, Drive)
- `plotting.py` - Visualization functions
- `*_api.py` - API interfaces (e.g., `train_api.py`, `infer_api.py`)
- `io.py` - I/O operations
- `preprocessing.py` - Data preprocessing

### Tier 2 (Orchestration)
- `train_fit.py` - Training orchestration
- `inference.py` - Inference orchestration
- `evaluate.py` - Evaluation orchestration
- `workflow.py` - Multi-step workflows

### Tier 3 (External Interfaces)
- `experiment.py` - End-to-end experiment workflows
- `main.py` - CLI entry point
- `etl/` - ETL pipelines (directory)
- `tests/` - Test files (directory)
- `notebooks/` - Analysis notebooks (directory)

## Function Classification Table

| Class | Purpose | Type Hints | Docstring | Tests | Naming | Example |
|-------|---------|------------|-----------|-------|--------|---------|
| **A** | Public External API | ✅ Required | ✅ Detailed | ✅ Required | Clean | `predict_molecules()` |
| **B** | Public Internal | ✅ Required | ✅ Basic | ✅ Required | Descriptive | `predict_molecules_by_consensus()` |
| **C** | Private Module | ⚠️  Optional | ⚠️  Simple | ⚠️  Encouraged | `_function` | `_predict_internal()` |
| **D** | Private Sub-Module | ⚠️  Optional | ❌ Optional | ❌ Optional | `_fn` | `_calc()` |

## Example Module Structure

```
src/example_module/
├── CLAUDE.md                    # Architecture documentation
├── BUILD.bazel                  # Bazel build config
│
├── # Tier 0: Core Domain
├── structs.py                   # Data structures
├── algorithms.py                # Pure functions
├── config.py                    # Config schema
├── utils.py                     # Utilities
│
├── # Tier 1: Application Services
├── dataloaders.py               # Data loading
├── plotting.py                  # Visualization
├── train_api.py                 # Training API
├── infer_api.py                 # Inference API
│
├── # Tier 2: Orchestration
├── train_fit.py                 # Training workflow
├── inference.py                 # Inference workflow
├── evaluate.py                  # Evaluation workflow
│
├── # Tier 3: External Interfaces
├── experiment.py                # End-to-end experiments
├── main.py                      # CLI
├── etl/                         # ETL pipelines
│   ├── CLAUDE.md                # Subdirectory docs
│   └── pipeline.py
├── tests/                       # Tests
│   ├── test_structs.py
│   ├── test_algorithms.py
│   └── ...
└── notebooks/                   # Analysis
    └── exploration.ipynb
```

## Common Patterns

### Data Flow: T0 → T1 → T2 → T3

```python
# structs.py (T0) - Define data
@dataclass
class Molecule:
    smiles: str
    features: np.ndarray

# algorithms.py (T0) - Pure logic
def calculate_similarity(mol1: Molecule, mol2: Molecule) -> float:
    return np.dot(mol1.features, mol2.features)

# dataloaders.py (T1) - Load data
def load_molecules(path: str) -> list[Molecule]:
    df = read_parquet(path)
    return [Molecule(row.smiles, row.features) for row in df.itertuples()]

# train_fit.py (T2) - Orchestrate
def train_model(molecule_path: str) -> Model:
    molecules = load_molecules(molecule_path)  # T1
    similarities = [calculate_similarity(m1, m2) for ...]  # T0
    return train_on_similarities(similarities)

# experiment.py (T3) - End-to-end
def run_experiment(config: Config):
    model = train_model(config.data_path)  # T2
    evaluate_model(model, config.test_path)  # T2
```

### Shared Code: Extract to Lower Tier

**Before** (violation):
```python
# train_fit.py (T2)
def preprocess_data(data):
    ...

# inference.py (T2)
from .train_fit import preprocess_data  # ❌ Same-tier import!
```

**After** (fixed):
```python
# dataloaders.py (T1)
def preprocess_data(data):  # Moved to T1
    ...

# train_fit.py (T2)
from .dataloaders import preprocess_data  # ✅ Valid

# inference.py (T2)
from .dataloaders import preprocess_data  # ✅ Valid
```

## Validation Checklist

For each module:
- [ ] CLAUDE.md exists and documents tiers
- [ ] All T0 files have no internal dependencies
- [ ] All T1 files only import from T0
- [ ] All T2 files only import from T0 and T1
- [ ] T3 can import from any tier
- [ ] No same-tier imports (or justified in CLAUDE.md)
- [ ] Public functions (A/B) have type hints and docstrings
- [ ] Tests exist for Class A and B functions
- [ ] Directories `etl/`, `tests/`, `notebooks/` exist when needed
- [ ] Each subdirectory has its own CLAUDE.md

## CLAUDE.md Template

```markdown
# Module Name

Brief description of module purpose.

## Module Architecture (Tiered Clean Architecture)

### Tier 0: Core Domain (No Dependencies)
- **structs.py**: Data structures and types
- **algorithms.py**: Pure domain logic
- **config.py**: Configuration schema

### Tier 1: Application Services
- **dataloaders.py**: Data loading from GCS/BigQuery
- **plotting.py**: Visualization utilities

### Tier 2: Orchestration
- **train_fit.py**: Training orchestration
- **inference.py**: Inference orchestration

### Tier 3: External Interfaces
- **experiment.py**: End-to-end workflows
- **main.py**: CLI entry point

## Key Data Structures

[Document main dataclasses/types]

## Common Workflows

[Document typical usage patterns]

## Dependencies

### Upstream
[What this module depends on]

### Downstream
[What depends on this module]
```

## References

- Project CLAUDE.md: `/home/jonah/osmo/CLAUDE.md`
- User CLAUDE.md: `/home/jonah/.claude/CLAUDE.md`
- Example modules:
  - `src/research/gcms_library_api/` - Well-structured example
  - `src/sandbox/jonah/iterative_deform/` - Another good example
