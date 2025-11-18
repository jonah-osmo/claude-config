---
name: configuration-refactoring-expert
description: Make configuration systems more flexible with CLI overrides, environment variables, and validation. Use when user says "make config flexible", "add CLI overrides", "refactor configuration", "config too rigid", or "enable runtime overrides". Identifies hardcoded values, suggests override mechanisms, and adds type safety.
---

# Configuration Refactoring Expert

Transform rigid configuration systems into flexible, validated, and override-capable systems.

## Instructions

When refactoring configuration systems:

### 1. Identify Current Configuration Issues

Scan code for:

**Hardcoded Values**:
```python
# BAD: Hardcoded polarity
column_polarity = "nonpolar"  # Can't change without code edit!

# BAD: Hardcoded list
machine_filter = ["8890A_5977C_03", "7890B_5977B_02"]
```

**Config-Only Parameters**:
```yaml
# config.yaml - No way to override at runtime
machine_filter:
  - '7890B_5977B_02'
  - '8890A_5977C_03'
```

**Missing Validation**:
```python
# BAD: No type checking or validation
config = yaml.load(file)  # Could be anything!
value = config["key"]  # Might not exist, might be wrong type
```

### 2. Design Configuration Hierarchy

Implement override precedence:

```
1. CLI arguments (highest priority)
2. Environment variables
3. Config file overrides
4. Default config file
5. Hardcoded defaults (lowest priority)
```

### 3. Create Config Schema with Type Safety

Use dataclasses or Pydantic for validation:

```python
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Config:
    """Configuration schema with types."""
    # Required fields
    mode: str

    # Optional with defaults
    machine_filter: List[str] = None
    col_polarity_filter: str = "nonpolar"

    # Nested config
    clustering: ClusteringConfig = None

    def __post_init__(self):
        """Validate after initialization."""
        if self.mode not in ["prod", "dev", "debug"]:
            raise ValueError(f"Invalid mode: {self.mode}")

        if self.machine_filter is None:
            self.machine_filter = []
```

### 4. Implement Config Loader with Overrides

```python
def load_config(
    config_path: Optional[str] = None,
    override_config: Optional[Dict] = None,
    env_prefix: str = "APP_"
) -> Config:
    """
    Load configuration with multiple override sources.

    Precedence: CLI overrides > env vars > config file > defaults

    Args:
        config_path: Path to YAML config file
        override_config: Dictionary of CLI overrides
        env_prefix: Prefix for environment variables

    Returns:
        Validated Config object
    """
    # 1. Load default config
    default_config = load_yaml(config_path or "config.yaml")

    # 2. Apply environment variable overrides
    env_overrides = {}
    for key in default_config.keys():
        env_key = f"{env_prefix}{key.upper()}"
        if env_key in os.environ:
            env_overrides[key] = os.environ[env_key]

    # 3. Apply CLI overrides (highest priority)
    if override_config:
        default_config.update(override_config)

    # 4. Apply env overrides
    if env_overrides:
        default_config.update(env_overrides)

    # 5. Validate and return
    try:
        return Config(**default_config)
    except TypeError as e:
        raise ValueError(f"Invalid configuration: {e}")
```

### 5. Add CLI Override Support

Enable all config parameters via CLI:

```python
def create_cli_parser(default_config: Dict) -> argparse.ArgumentParser:
    """Dynamically create CLI parser from config."""
    parser = argparse.ArgumentParser()

    for key, value in default_config.items():
        # Handle different types
        if isinstance(value, bool):
            parser.add_argument(
                f"--{key}",
                type=lambda x: x.lower() in ["true", "1", "yes"],
                help=f"Override {key} (default: {value})"
            )
        elif isinstance(value, list):
            parser.add_argument(
                f"--{key}",
                type=str,  # Parse as comma-separated
                help=f"Override {key} as comma-separated list"
            )
        elif isinstance(value, dict):
            # Flatten nested dicts to dot notation
            for nested_key, nested_value in value.items():
                parser.add_argument(
                    f"--{key}-{nested_key}",
                    type=type(nested_value),
                    help=f"Override {key}.{nested_key}"
                )
        else:
            parser.add_argument(
                f"--{key}",
                type=type(value),
                help=f"Override {key} (default: {value})"
            )

    return parser
```

### 6. Add Environment Variable Support

```python
def get_env_override(key: str, default: Any, prefix: str = "APP_") -> Any:
    """Get value from environment variable with type conversion."""
    env_key = f"{prefix}{key.upper()}"
    env_value = os.environ.get(env_key)

    if env_value is None:
        return default

    # Type conversion based on default
    if isinstance(default, bool):
        return env_value.lower() in ["true", "1", "yes"]
    elif isinstance(default, int):
        return int(env_value)
    elif isinstance(default, float):
        return float(env_value)
    elif isinstance(default, list):
        return env_value.split(",")
    else:
        return env_value
```

### 7. Add Validation Layer

```python
def validate_config(config: Config) -> List[str]:
    """
    Validate configuration and return list of errors.

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    # Validate required fields
    if not config.mode:
        errors.append("mode is required")

    # Validate enums
    if config.mode not in ["prod", "dev", "debug"]:
        errors.append(f"Invalid mode: {config.mode}")

    # Validate ranges
    if config.clustering and config.clustering.k < 1:
        errors.append("clustering.k must be >= 1")

    # Validate dependencies
    if config.use_clustering and not config.clustering:
        errors.append("clustering config required when use_clustering=true")

    return errors
```

### 8. Add Config Documentation

Generate documentation from schema:

```python
def document_config(config_class: type) -> str:
    """Generate Markdown documentation from config dataclass."""
    docs = []
    docs.append("# Configuration Reference\n")

    for field in fields(config_class):
        docs.append(f"## `{field.name}`")
        docs.append(f"- **Type**: `{field.type}`")
        if field.default != MISSING:
            docs.append(f"- **Default**: `{field.default}`")
        if field.metadata.get("description"):
            docs.append(f"- **Description**: {field.metadata['description']}")
        docs.append("")

    return "\n".join(docs)
```

## Refactoring Workflow

1. **Audit current config** - Identify all configuration sources
2. **Create schema** - Define typed config dataclass
3. **Implement loader** - Support multiple override sources
4. **Add CLI support** - Enable all params via command line
5. **Add env var support** - Enable environment overrides
6. **Add validation** - Validate before use
7. **Document** - Generate config documentation
8. **Test** - Comprehensive tests for all override sources

## Common Patterns

### Pattern 1: Immutable Config with frozendict

```python
from frozendict import frozendict

def load_config() -> frozendict:
    """Load immutable configuration."""
    config_dict = {...}
    return frozendict(config_dict)  # Can't be modified after creation
```

### Pattern 2: Config Sections

```python
@dataclass
class ClusteringConfig:
    k: int = 32
    threshold: float = 0.95

@dataclass
class Config:
    mode: str
    clustering: ClusteringConfig
```

### Pattern 3: Config Migration/Versioning

```python
def migrate_config(config: Dict, from_version: int, to_version: int) -> Dict:
    """Migrate config between versions."""
    if from_version == 1 and to_version == 2:
        # Rename field
        if "old_name" in config:
            config["new_name"] = config.pop("old_name")

    return config
```

## When to Use This Skill

- Config parameters are hardcoded
- User wants CLI overrides for config-only params
- Need environment variable support
- Config lacks validation
- Need to make system more flexible
- Deploying to different environments (dev/prod)
- User says "config is too rigid" or "can't override X"

## Refactoring Checklist

- [ ] Audit all configuration sources
- [ ] Create typed config schema (dataclass/Pydantic)
- [ ] Implement config loader with override hierarchy
- [ ] Add CLI argument support for all params
- [ ] Add environment variable support
- [ ] Add validation with clear error messages
- [ ] Generate config documentation
- [ ] Write tests for:
  - [ ] Default config loading
  - [ ] CLI overrides
  - [ ] Env var overrides
  - [ ] Override precedence
  - [ ] Validation (valid and invalid configs)
- [ ] Update user documentation

## Project-Specific Notes

- Use `frozendict` for immutable configs in this project
- YAML files should use explicit type tags (`!!int`, `!!float`, `!!bool`)
- Config files go in T0 (`config.py`)
- Config loading belongs in T0 or T1 depending on I/O
- Use Click for CLI (not argparse) - better type support
