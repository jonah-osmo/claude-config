# Test Suite Generator Examples

Real examples from the osmo codebase demonstrating comprehensive test generation.

## Example 1: CommaList Type (from config_loader_click.py)

**Target Code**:
```python
class CommaList(click.ParamType):
    """Parse comma-separated lists."""

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
                self.fail(f"Could not convert items to {self.value_type.__name__}: {e}", param, ctx)

        return items
```

**Generated Test Suite** (20 tests):

```python
class TestCommaListType:
    """Test suite for CommaList Click parameter type."""

    # --- Empty and single values (3 tests) ---

    def test_comma_list_empty(self):
        """Empty string should return empty list."""
        comma_list = CommaList()
        result = comma_list.convert("", None, None)
        assert result == []

    def test_comma_list_single(self):
        """Single item without comma should return single-item list."""
        comma_list = CommaList()
        result = comma_list.convert("item", None, None)
        assert result == ["item"]

    def test_comma_list_single_with_trailing_comma(self):
        """Single item with trailing comma should return single-item list."""
        comma_list = CommaList()
        result = comma_list.convert("item,", None, None)
        assert result == ["item"]

    # --- Multiple values (2 tests) ---

    def test_comma_list_two_items(self):
        """Two comma-separated items should return two-item list."""
        comma_list = CommaList()
        result = comma_list.convert("a,b", None, None)
        assert result == ["a", "b"]

    def test_comma_list_many_items(self):
        """Many comma-separated items should all be parsed."""
        comma_list = CommaList()
        result = comma_list.convert("a,b,c,d,e", None, None)
        assert result == ["a", "b", "c", "d", "e"]

    # --- Whitespace handling (3 tests) ---

    def test_comma_list_with_spaces(self):
        """Spaces after commas should be stripped."""
        comma_list = CommaList()
        result = comma_list.convert("a, b, c", None, None)
        assert result == ["a", "b", "c"]

    def test_comma_list_trailing_spaces(self):
        """Leading/trailing spaces should be stripped."""
        comma_list = CommaList()
        result = comma_list.convert(" a , b ", None, None)
        assert result == ["a", "b"]

    def test_comma_list_preserve_internal_spaces(self):
        """Internal spaces in items should be preserved."""
        comma_list = CommaList()
        result = comma_list.convert("foo bar,baz qux", None, None)
        assert result == ["foo bar", "baz qux"]

    # --- Type inference (3 tests) ---

    def test_comma_list_integers(self):
        """Integer list type should convert strings to ints."""
        comma_list = CommaList(value_type=int)
        result = comma_list.convert("1,2,3", None, None)
        assert result == [1, 2, 3]
        assert all(isinstance(x, int) for x in result)

    def test_comma_list_floats(self):
        """Float list type should convert strings to floats."""
        comma_list = CommaList(value_type=float)
        result = comma_list.convert("1.5,2.3,3.7", None, None)
        assert result == [1.5, 2.3, 3.7]
        assert all(isinstance(x, float) for x in result)

    def test_comma_list_mixed_numbers(self):
        """Mixed int/float strings should convert to target type."""
        comma_list = CommaList(value_type=float)
        result = comma_list.convert("1,2.5,3", None, None)
        assert result == [1.0, 2.5, 3.0]
        assert all(isinstance(x, float) for x in result)

    # --- Real-world cases (3 tests) ---

    def test_comma_list_machine_filter(self):
        """Machine filter real-world example."""
        comma_list = CommaList(value_type=str)
        result = comma_list.convert("8890A_5977C_03,7890B_5977B_02", None, None)
        assert result == ["8890A_5977C_03", "7890B_5977B_02"]

    def test_comma_list_solvent_ids(self):
        """Solvent material IDs real-world example."""
        comma_list = CommaList(value_type=int)
        result = comma_list.convert("10,82,3497,5765", None, None)
        assert result == [10, 82, 3497, 5765]
        assert all(isinstance(x, int) for x in result)

    def test_comma_list_folder_paths(self):
        """GCMS run folder filter real-world example."""
        comma_list = CommaList(value_type=str)
        result = comma_list.convert("OsmoLibrary,OsmoLibrary/Pilot,OsmoLibrary/Pilot/DBWax", None, None)
        assert result == ["OsmoLibrary", "OsmoLibrary/Pilot", "OsmoLibrary/Pilot/DBWax"]

    # --- Edge cases (3 tests) ---

    def test_comma_list_special_chars_underscores(self):
        """Items with underscores should be preserved."""
        comma_list = CommaList()
        result = comma_list.convert("foo_bar,baz_qux", None, None)
        assert result == ["foo_bar", "baz_qux"]

    def test_comma_list_special_chars_hyphens(self):
        """Items with hyphens should be preserved."""
        comma_list = CommaList()
        result = comma_list.convert("foo-bar,baz-qux", None, None)
        assert result == ["foo-bar", "baz-qux"]

    def test_comma_list_special_chars_slashes(self):
        """Items with slashes (paths) should be preserved."""
        comma_list = CommaList()
        result = comma_list.convert("path/to/file,another/path", None, None)
        assert result == ["path/to/file", "another/path"]

    # --- Error handling (3 tests) ---

    def test_comma_list_invalid_int_conversion(self):
        """Invalid int conversion should raise error."""
        comma_list = CommaList(value_type=int)
        with pytest.raises(Exception):  # Click will wrap in its own error
            comma_list.convert("1,not_a_number,3", None, Mock())

    def test_comma_list_invalid_float_conversion(self):
        """Invalid float conversion should raise error."""
        comma_list = CommaList(value_type=float)
        with pytest.raises(Exception):
            comma_list.convert("1.5,invalid,3.7", None, Mock())

    def test_comma_list_none_value(self):
        """None value should return None."""
        comma_list = CommaList()
        result = comma_list.convert(None, None, None)
        assert result is None
```

## Example 2: Dot Notation Helpers (from config_loader_click.py)

**Target Code**:
```python
def _flatten_dict(nested_dict: Dict[str, Any], parent_key: str = "", sep: str = ".") -> Dict[str, Any]:
    """Flatten a nested dictionary using dot notation."""
    items = []
    for key, value in nested_dict.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            items.extend(_flatten_dict(value, new_key, sep).items())
        else:
            items.append((new_key, value))
    return dict(items)

def _unflatten_dict(flat_dict: Dict[str, Any], sep: str = ".") -> Dict[str, Any]:
    """Unflatten a dictionary with dot-notation keys."""
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
```

**Generated Test Suite** (15 tests):

```python
class TestDotNotationHelpers:
    """Test suite for flatten/unflatten dict helpers."""

    # --- Basic flattening (3 tests) ---

    def test_flatten_simple_dict(self):
        """Simple dict should remain unchanged."""
        input_dict = {"a": 1, "b": 2}
        result = _flatten_dict(input_dict)
        assert result == {"a": 1, "b": 2}

    def test_flatten_nested_dict_two_levels(self):
        """Two-level nested dict should flatten with dots."""
        input_dict = {"clustering": {"k": 32, "mutual": True}}
        result = _flatten_dict(input_dict)
        assert result == {"clustering.k": 32, "clustering.mutual": True}

    def test_flatten_nested_dict_deep(self):
        """Deep nesting should flatten correctly."""
        input_dict = {"a": {"b": {"c": {"d": 42}}}}
        result = _flatten_dict(input_dict)
        assert result == {"a.b.c.d": 42}

    # --- Preserve non-dict types (2 tests) ---

    def test_flatten_preserves_lists(self):
        """Lists should not be flattened."""
        input_dict = {"machine_filter": ["a", "b"], "nested": {"list": [1, 2, 3]}}
        result = _flatten_dict(input_dict)
        assert result == {"machine_filter": ["a", "b"], "nested.list": [1, 2, 3]}
        assert isinstance(result["machine_filter"], list)

    def test_flatten_preserves_scalars(self):
        """Scalar values should be preserved."""
        input_dict = {"int": 42, "float": 3.14, "bool": True, "str": "value", "none": None}
        result = _flatten_dict(input_dict)
        assert result == input_dict

    # ... (10 more tests for unflattening, round-trips, etc.)
```

## Example 3: BUILD.bazel Test Target

After generating tests, add to `BUILD.bazel`:

```python
pytest_test(
    name = "test_config_loader_click",
    size = "small",
    srcs = ["test_config_loader_click.py"],
    deps = [
        "//src/research/gcms_library_api:config_loader_click",
        requirement("click"),
        requirement("frozendict"),
    ],
)
```

## Coverage Achieved

From `config_loader_click.py` example:
- **60+ tests** generated
- **All functions** tested
- **>95% code coverage**
- Tests passed on first run
- Identified edge cases not considered in original implementation
