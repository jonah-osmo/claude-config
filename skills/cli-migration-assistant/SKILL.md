---
name: cli-migration-assistant
description: Migrate argparse CLI to Click framework with support for complex types (lists, nested dicts). Use when user says "migrate to click", "convert argparse to click", "CLI refactor", "add list support to CLI", or "nested dict arguments". Handles comma-separated lists, dot notation for nested dicts, type inference, and maintains backwards compatibility.
---

# CLI Migration Assistant

Migrate existing argparse command-line interfaces to Click framework with advanced type support.

## Instructions

When migrating argparse to Click:

### 1. Analyze Current Implementation

Review the existing argparse code to identify:
- All command-line arguments and their types
- Default values and help text
- Argument groups or subcommands
- Custom types or validation logic
- How arguments are consumed in the code

### 2. Identify Complex Parameter Types

Categorize parameters into:

**Simple Types** (direct migration):
- Strings, integers, floats, booleans
- Choices/enums

**List Parameters** (need CommaList):
- Lists of strings, ints, or floats
- Currently handled via `action='append'` or custom parsing

**Nested Dictionaries** (need dot notation):
- Configuration objects with multiple nested keys
- Currently loaded from config files only

### 3. Create Click Command Structure

```python
import click
from typing import Any, Dict, List

# Define custom types
class CommaList(click.ParamType):
    """Parse comma-separated lists with type inference."""
    name = "commalist"

    def __init__(self, value_type=str):
        self.value_type = value_type

    def convert(self, value, param, ctx):
        if value is None:
            return None
        if value == "":
            return []

        items = [item.strip() for item in value.split(",")]
        items = [item for item in items if item]

        if self.value_type != str:
            try:
                items = [self.value_type(item) for item in items]
            except (ValueError, TypeError) as e:
                self.fail(f"Could not convert to {self.value_type.__name__}: {e}", param, ctx)

        return items

# Define Click command
@click.command()
@click.option('--simple-arg', type=str, help="Simple string argument")
@click.option('--list-arg', type=CommaList(value_type=int), help="Comma-separated list")
@click.option('--nested-param', type=int, help="Nested dict parameter")
def main(simple_arg, list_arg, nested_param, **kwargs):
    """Main command."""
    pass
```

### 4. Handle Nested Dictionaries with Dot Notation

For nested config parameters like `clustering.k`, `clustering.threshold`:

```python
def _flatten_dict(nested_dict: Dict[str, Any], sep: str = ".") -> Dict[str, Any]:
    """Flatten nested dict to dot notation."""
    items = []
    for key, value in nested_dict.items():
        if isinstance(value, dict):
            items.extend(_flatten_dict(value, key, sep).items())
        else:
            items.append((key, value))
    return dict(items)

def _unflatten_dict(flat_dict: Dict[str, Any], sep: str = ".") -> Dict[str, Any]:
    """Unflatten dot notation back to nested dict."""
    result = {}
    for key, value in flat_dict.items():
        parts = key.split(sep)
        current = result
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value
    return result

# Dynamically add options for nested params
default_config = load_config()
flat_config = _flatten_dict(default_config)

for key, value in flat_config.items():
    cli_key = key.replace("_", "-").replace(".", "-")
    option_type = type(value)  # Infer type from config

    # Add Click option
    click.option(f'--{cli_key}', type=option_type)
```

### 5. Maintain Backwards Compatibility

Support both hyphenated and underscored versions:

```python
@click.option('--foo-bar', '--foo_bar', type=str)
```

This allows users to use either `--foo-bar` or `--foo_bar`.

### 6. Update Main Entry Point

```python
def main():
    """Command-line interface."""
    import click
    import sys

    # Create Click command with dynamic options
    cmd, config_keys = create_click_command()

    try:
        # Parse arguments
        ctx = cmd.make_context('command_name', sys.argv[1:])

        # Build config overrides from context
        config_overrides = populate_config_overrides(ctx, config_keys)

        # Continue with application logic
        run_application(config_overrides)

    except click.ClickException as e:
        e.show()
        sys.exit(e.exit_code)
```

### 7. Update BUILD.bazel

Add Click dependency:

```python
py_library(
    name = "config_loader_click",
    srcs = ["config_loader_click.py"],
    deps = [
        requirement("click"),
        # ... other deps
    ],
)

py_binary(
    name = "main",
    srcs = ["main.py"],
    deps = [
        ":config_loader_click",
        requirement("click"),
    ],
)
```

## Migration Checklist

- [ ] Identify all argparse arguments
- [ ] Categorize arguments by type (simple/list/nested)
- [ ] Create CommaList custom type for lists
- [ ] Implement flatten/unflatten for nested dicts
- [ ] Add Click options (both hyphen and underscore versions)
- [ ] Update main() to use Click
- [ ] Test with existing command-line usage
- [ ] Update BUILD.bazel with Click dependency
- [ ] Write comprehensive tests (60+ tests)
- [ ] Update documentation

## Type Inference Rules

From config schema:
- `int` values → `type=int`
- `float` values → `type=float`
- `bool` values → `type=bool`
- `list[int]` → `type=CommaList(value_type=int)`
- `list[str]` → `type=CommaList(value_type=str)`
- `dict` → Flatten to dot notation, add option per key

## Common Patterns

**Empty list to clear**:
```bash
--machine-filter ""  # Clears list
```

**Nested dict override**:
```bash
--clustering-k 64 --clustering-threshold 0.98
```

**Multiple items**:
```bash
--machine-filter "a,b,c"
```

## When to Use This Skill

- Migrating argparse CLI to Click
- Adding list parameter support to CLI
- Adding nested dict parameter support
- Making config-only parameters available via CLI
- Improving CLI user experience with better help and validation
