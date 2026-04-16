# jsonify-objects

Recursively convert almost any Python object to a JSON-serializable structure.

## Installation

```
pip install jsonify-objects
```

## Usage

### `dumps`

Drop-in wrapper around `json.dumps` that handles non-serializable types.

```python
from jsonify_objects import dumps

dumps({"a": 1, "b": True})
# '{\n  "a": "1",\n  "b": "true"\n}'
```

### `jsonify_objects`

Returns the converted structure without serializing to a string.

```python
from jsonify_objects import jsonify_objects

jsonify_objects({"a": 1, "b": True})
# {"a": "1", "b": "true"}
```

## Behavior

### Primitives

Primitive values inside plain dicts and lists are converted to strings.

| Type | Output |
|------|--------|
| `int`, `float` | `str(value)` |
| `bool` | `"true"` / `"false"` |
| `str` | unchanged |
| `None` | `null` |
| `Enum` | `str(value.value)` |

```python
dumps({"x": 42, "flag": True, "color": Color.RED})
# {"x": "42", "flag": "true", "color": "red"}
```

### Dataclasses and objects

By default, non-serializable objects fall back to `repr`.

```python
dumps({"user": UserDataclass("Alice", 30)})
# {"user": "UserDataclass(name='Alice', age=30)"}
```

Pass `serialize_objects=True` to expand objects and dataclasses into dicts.
Numeric fields on expanded objects preserve their native JSON types.

```python
dumps({"user": UserDataclass("Alice", 30)}, serialize_objects=True)
# {"user": {"name": "Alice", "age": 30}}
```

Nested objects are expanded recursively.

```python
dumps({"person": Person("Bob", Address("NYC"))}, serialize_objects=True)
# {"person": {"name": "Bob", "address": {"city": "NYC"}}}
```

Objects without a `__dict__` (e.g. slots-only classes) fall back to `repr`.

### `indent`

`dumps` accepts an `indent` parameter (default `2`) passed through to `json.dumps`.

```python
dumps({"a": 1}, indent=4)
```
