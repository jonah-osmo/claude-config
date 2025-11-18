# Configuration Refactoring Examples

Real examples from the osmo codebase showing configuration refactoring.

## Example 1: gcms_library_api - From Rigid to Flexible

### Before: Config-Only Parameters

**Problem**: Critical parameters locked in config.yaml, requiring code edits to change.

```yaml
# config.yaml
col_polarity_filter: 'nonpolar'  # ← Can't override!
machine_filter:  # ← Can't override!
  - '7890B_5977B_02'
  - '8890A_5977C_03'

clustering:  # ← Can't override!
  k: 32
  cos_threshold: 0.95
```

**Impact**:
- Need different polarity? Edit config.yaml
- Test with different machines? Edit config.yaml
- Try different clustering params? Edit config.yaml
- No way to override at runtime
- Can't A/B test configurations

### After: Multi-Level Override System

**Solution**: Implemented hierarchy - CLI > config file > defaults

```bash
# Now can override everything!
./python main.py \
  --col-polarity-filter "polar" \
  --machine-filter "8890A_5977C_03" \
  --clustering-k 64 \
  --clustering-cos-threshold 0.98
```

**Implementation**:

```python
# config_loader_click.py
def load_library_config(
    config: Optional[str | frozendict] = None,
    override_config: Optional[Dict[str, Any]] = None
) -> frozendict:
    """Load configuration with override support."""

    # 1. Load default config
    default_config = load_yaml(DEFAULT_CONFIG_PATH)

    # 2. Apply CLI overrides (highest priority)
    if override_config:
        default_config.update(override_config)

    # 3. Make immutable
    return frozendict(default_config)
```

**Results**:
- ~40 parameters → ~100+ parameters available via CLI
- Eliminated need for config file edits
- Enabled A/B testing of configurations
- Zero breaking changes (backwards compatible)

## Example 2: iterative_deform - Hardcoded to Dynamic

### Before: Hardcoded Polarity Check

**Problem**: Code assumed nonpolar columns only.

```python
# dataloaders.py - BEFORE
def load_query_gcms(gcms_run_id: str):
    gcms_molecules = _load_gcms_molecules(gcms_run_id)

    # HARDCODED validation!
    column_polarity = gcms_molecules.gcms.metadata.column_polarity
    if column_polarity != "nonpolar":
        raise ValueError(
            "This workflow only supports nonpolar columns!"
        )
    # ... rest of function
```

**Impact**:
- Polar column queries rejected
- Can't use with polar libraries
- Requires code changes to support polar columns

### After: Library-Aware Validation

**Solution**: Extract polarity from library config, validate match.

```python
# dataloaders.py - AFTER
def load_query_gcms(
    gcms_run_id: str,
    gcms_config: str,
    library_experiment_id: str  # NEW: Get library info
):
    gcms_molecules = _load_gcms_molecules(gcms_run_id)

    # Load library config to get expected polarity
    library_config = load_library_config(library_experiment_id)
    library_polarity = library_config.get('col_polarity_filter', 'nonpolar')
    normalized_library_polarity = _normalize_column_polarity(library_polarity)

    # Validate query polarity matches library polarity
    column_polarity = gcms_molecules.gcms.metadata.column_polarity
    normalized_query_polarity = _normalize_column_polarity(column_polarity)

    if normalized_query_polarity != normalized_library_polarity:
        raise ValueError(
            f"Query polarity '{column_polarity}' doesn't match "
            f"library polarity '{library_polarity}'. "
            f"They must match!"
        )
    # ... rest of function
```

**Benefits**:
- Works with both polar and nonpolar
- Dynamic validation based on library
- Clear error messages
- No hardcoded assumptions

## Example 3: Adding Config Validation

### Before: No Validation

```python
# BAD: No validation
config = yaml.load(open("config.yaml"))
k = config["clustering"]["k"]  # Could fail!
```

### After: Schema Validation

```python
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class ClusteringConfig:
    """Clustering configuration with validation."""
    k: int = 32
    cos_threshold: float = 0.95
    delta_ri_max: float = 2.0

    def __post_init__(self):
        """Validate after initialization."""
        if self.k < 1:
            raise ValueError("k must be >= 1")
        if not (0 <= self.cos_threshold <= 1):
            raise ValueError("cos_threshold must be in [0, 1]")
        if self.delta_ri_max <= 0:
            raise ValueError("delta_ri_max must be > 0")

@dataclass
class LibraryConfig:
    """Main library configuration."""
    mode: str
    col_polarity_filter: str = "nonpolar"
    machine_filter: List[str] = field(default_factory=list)
    clustering: ClusteringConfig = field(default_factory=ClusteringConfig)

    def __post_init__(self):
        """Validate config."""
        if self.mode not in ["prod", "dev", "debug"]:
            raise ValueError(f"Invalid mode: {self.mode}")

        # Validate polarity
        valid_polarities = ["nonpolar", "polar", "db5", "dbwax"]
        if self.col_polarity_filter not in valid_polarities:
            raise ValueError(f"Invalid polarity: {self.col_polarity_filter}")


# Usage
try:
    config = LibraryConfig(**yaml_dict)
except (TypeError, ValueError) as e:
    print(f"Invalid configuration: {e}")
    sys.exit(1)
```

**Benefits**:
- Type safety
- Clear validation errors
- IDE autocomplete support
- Self-documenting

## Example 4: Config Override Precedence

Implementing proper override hierarchy:

```python
def load_config_with_overrides(
    config_path: str = "config.yaml",
    cli_overrides: Optional[Dict] = None,
    env_prefix: str = "OSMO_"
) -> Config:
    """
    Load config with override precedence:
    1. CLI arguments (highest)
    2. Environment variables
    3. Config file
    4. Hardcoded defaults (lowest)
    """
    # 1. Start with hardcoded defaults
    config = {
        "mode": "dev",
        "col_polarity_filter": "nonpolar",
        "machine_filter": [],
    }

    # 2. Overlay config file (if exists)
    if os.path.exists(config_path):
        file_config = load_yaml(config_path)
        config.update(file_config)

    # 3. Overlay environment variables
    for key in config.keys():
        env_key = f"{env_prefix}{key.upper()}"
        if env_key in os.environ:
            env_value = os.environ[env_key]

            # Type conversion
            if isinstance(config[key], list):
                config[key] = env_value.split(",")
            elif isinstance(config[key], int):
                config[key] = int(env_value)
            elif isinstance(config[key], float):
                config[key] = float(env_value)
            elif isinstance(config[key], bool):
                config[key] = env_value.lower() in ["true", "1", "yes"]
            else:
                config[key] = env_value

    # 4. Overlay CLI overrides (highest priority)
    if cli_overrides:
        config.update(cli_overrides)

    return Config(**config)


# Usage examples:

# Default from config file
config = load_config_with_overrides()

# Environment variable override
# export OSMO_MODE=prod
config = load_config_with_overrides()

# CLI override (highest priority)
cli_args = {"mode": "debug", "machine_filter": ["8890A_5977C_03"]}
config = load_config_with_overrides(cli_overrides=cli_args)
```

## Example 5: Config Documentation Generation

Auto-generate documentation from schema:

```python
from dataclasses import fields, MISSING
from typing import get_type_hints

def generate_config_docs(config_class: type) -> str:
    """Generate Markdown docs from dataclass."""
    docs = ["# Configuration Reference\n"]
    docs.append(f"Configuration for {config_class.__name__}\n")

    for field in fields(config_class):
        # Field name and type
        docs.append(f"## `{field.name}`")
        type_hint = get_type_hints(config_class)[field.name]
        docs.append(f"**Type**: `{type_hint}`\n")

        # Default value
        if field.default != MISSING:
            docs.append(f"**Default**: `{field.default}`\n")
        elif field.default_factory != MISSING:
            docs.append(f"**Default**: `{field.default_factory()}`\n")
        else:
            docs.append("**Required**: Yes\n")

        # CLI override
        cli_name = field.name.replace("_", "-")
        docs.append(f"**CLI Override**: `--{cli_name}`\n")

        # Environment variable
        env_name = f"OSMO_{field.name.upper()}"
        docs.append(f"**Environment Variable**: `{env_name}`\n")

        docs.append("")

    return "\n".join(docs)

# Generate docs
docs = generate_config_docs(LibraryConfig)
with open("CONFIG.md", "w") as f:
    f.write(docs)
```

**Output**:
```markdown
# Configuration Reference

Configuration for LibraryConfig

## `mode`
**Type**: `str`

**Required**: Yes

**CLI Override**: `--mode`

**Environment Variable**: `OSMO_MODE`

## `col_polarity_filter`
**Type**: `str`

**Default**: `nonpolar`

**CLI Override**: `--col-polarity-filter`

**Environment Variable**: `OSMO_COL_POLARITY_FILTER`

...
```

## Key Takeaways

1. **Flexibility matters** - CLI overrides eliminate config file edits
2. **Validation saves time** - Catch errors early with schema validation
3. **Override hierarchy** - CLI > env vars > config file > defaults
4. **Type safety** - Use dataclasses or Pydantic for config schemas
5. **Documentation** - Auto-generate from schema for accuracy
6. **Backwards compatibility** - Support multiple override methods
7. **Testing** - Comprehensive tests for all override sources
