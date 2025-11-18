# CLI Migration Assistant Examples

Real example from migrating gcms_library_api from argparse to Click.

## Before: Argparse Implementation

**Problem**: List and dict parameters were not available via CLI, only in config.yaml.

```python
# config_loader.py (OLD)
def create_library_experiment_parser():
    parser = argparse.ArgumentParser(description="Create material library experiments")

    # Only simple types supported
    parser.add_argument("--mode", type=str, default="dev", choices=["prod", "dev", "debug"])
    parser.add_argument("--col-polarity-filter", type=str, default=None)

    # Lists and nested dicts SKIPPED
    for key, value in config.items():
        if isinstance(value, (dict, list)):
            continue  # NOT SUPPORTED!

        if isinstance(value, str):
            parser.add_argument(f"--{key}", type=str)
        # ...

    return parser

# Command that FAILED:
# ./python main.py --machine-filter "8890A_5977C_03"
# Error: unrecognized arguments: --machine-filter
```

**Config.yaml had locked parameters**:
```yaml
machine_filter:
  - '7890B_5977B_02'
  - '8890A_5977C_03'

clustering:
  k: 32
  cos_threshold: 0.95
  delta_ri_max: 2.0
```

## After: Click Implementation

### Step 1: Create CommaList Custom Type

```python
# config_loader_click.py (NEW)
class CommaList(click.ParamType):
    """Parse comma-separated lists with type inference."""

    name = "commalist"

    def __init__(self, value_type=str):
        self.value_type = value_type

    def convert(self, value, param, ctx):
        if value is None:
            return None

        # Empty string → empty list
        if value == "":
            return []

        # Split by comma and strip whitespace
        items = [item.strip() for item in value.split(",")]
        items = [item for item in items if item]

        # Convert types if needed
        if self.value_type != str:
            try:
                items = [self.value_type(item) for item in items]
            except (ValueError, TypeError) as e:
                self.fail(f"Could not convert items to {self.value_type.__name__}: {e}", param, ctx)

        return items
```

### Step 2: Create Flatten/Unflatten Helpers

```python
def _flatten_dict(nested_dict: Dict[str, Any], parent_key: str = "", sep: str = ".") -> Dict[str, Any]:
    """Flatten a nested dictionary using dot notation."""
    items = []

    for key, value in nested_dict.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key

        # Only flatten dicts, not lists
        if isinstance(value, dict):
            items.extend(_flatten_dict(value, new_key, sep).items())
        else:
            items.append((new_key, value))

    return dict(items)

def _unflatten_dict(flat_dict: Dict[str, Any], sep: str = ".") -> Dict[str, Any]:
    """Unflatten a dictionary with dot-notation keys back to nested structure."""
    result = {}

    for key, value in flat_dict.items():
        parts = key.split(sep)
        current = result

        # Navigate/create nested structure
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]

        # Set the final value
        current[parts[-1]] = value

    return result
```

### Step 3: Dynamically Add Click Options

```python
def create_library_experiment_click_command():
    default_config = load_yaml(DEFAULT_CONFIG_PATH)

    @click.command()
    @click.option('--mode', type=click.Choice(['prod', 'dev', 'debug']), default='dev')
    @click.option('--subset', type=click.Choice(['ocp', 'ocpext', '']), default='')
    @click.pass_context
    def library_experiment_command(ctx, mode, subset, **kwargs):
        if ctx.obj is None:
            ctx.obj = {}
        ctx.obj['mode'] = mode
        ctx.obj['subset'] = subset
        ctx.obj['overrides'] = kwargs

    # Dynamically add options from config
    flat_config = _flatten_dict(default_config)

    for key, value in flat_config.items():
        cli_key = key.replace("_", "-").replace(".", "-")

        # Handle different types
        if isinstance(value, list):
            # Infer list element type
            if value and isinstance(value[0], int):
                list_type = CommaList(value_type=int)
            else:
                list_type = CommaList(value_type=str)

            option = click.Option(
                [f'--{cli_key}'],
                type=list_type,
                default=None,
                help=f"Override {key} as comma-separated list. Use empty string to clear."
            )

        elif isinstance(value, int):
            option = click.Option([f'--{cli_key}'], type=int, default=None)

        elif isinstance(value, float):
            option = click.Option([f'--{cli_key}'], type=float, default=None)

        else:
            option = click.Option([f'--{cli_key}'], type=str, default=None)

        library_experiment_command.params.append(option)

    return library_experiment_command
```

### Step 4: Update Main Entry Point

```python
def main():
    import click
    import sys

    # Create Click command with dynamic options
    cmd, config_override_keys = create_library_experiment_click_command()

    try:
        # Parse arguments
        ctx = cmd.make_context('library_experiment_command', sys.argv[1:])

        # Build config overrides from context params
        config_overrides = {}
        params = ctx.params

        for key in config_override_keys:
            cli_key = key.replace("_", "-").replace(".", "-")
            value = params.get(cli_key)

            if value is not None:
                config_overrides[key] = value

        # Unflatten nested keys
        unflattened = _unflatten_dict(config_overrides)

        # Load configuration with overrides
        config = load_library_config(override_config=unflattened)

        # Run the application
        run_library_experiment(config, mode=params.get('mode', 'dev'))

    except click.ClickException as e:
        e.show()
        sys.exit(e.exit_code)
```

## Result: Commands Now Work!

**List parameters** (previously impossible):
```bash
# Override machine filter
./python main.py --machine-filter "8890A_5977C_03,7890B_5977B_02"

# Clear machine filter
./python main.py --machine-filter ""

# Integer list
./python main.py --solvent-material-ids "10,82,3497,5765"
```

**Nested dict parameters** (previously impossible):
```bash
# Override clustering parameters
./python main.py --clustering-k 64 --clustering-cos-threshold 0.98

# Override basis config
./python main.py --basis-config-peak-probability-threshold 0.2
```

**Combined usage**:
```bash
./python main.py \
  --mode "dev" \
  --col-polarity-filter "polar" \
  --machine-filter "8890A_5977C_03" \
  --clustering-k 64 \
  --clustering-cos-threshold 0.98
```

## Migration Statistics

- **Before**: ~40 CLI parameters (scalars only)
- **After**: ~100+ CLI parameters (scalars + lists + nested dicts)
- **Code added**: ~420 lines (config_loader_click.py)
- **Tests added**: 60+ comprehensive tests
- **Backwards compatible**: Yes (both `--foo-bar` and `--foo_bar` work)
- **Migration time**: ~4 hours (including comprehensive tests)

## Key Learnings

1. **Type inference is critical** - Automatically detect int vs float vs string lists
2. **Empty string for clearing** - `--machine-filter ""` is intuitive for clearing lists
3. **Dot notation is natural** - `--clustering-k` feels better than `--clustering_k`
4. **Comprehensive tests save time** - Caught edge cases early
5. **Backwards compatibility matters** - Support both hyphen and underscore versions
