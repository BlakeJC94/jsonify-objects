import json
from dataclasses import asdict, is_dataclass
from enum import Enum
from typing import Any


def jsonify_objects(
    input_data: Any,
    serialize_objects: bool = False,
) -> str:
    """Convert any data with non-serializable objects to a formatted JSON
    string.
    """

    def _to_str(val: Any) -> str:
        if isinstance(val, Enum):
            return str(val.value)
        elif isinstance(val, bool):
            return str(val).lower()
        elif isinstance(val, (int, float)):
            return str(val)
        elif isinstance(val, str):
            return val
        else:
            try:
                return repr(val)
            except Exception:
                try:
                    return str(val)
                except Exception:
                    return type(val).__name__

    def _to_dict(obj: Any) -> dict:
        if hasattr(obj, "__dict__"):
            result = vars(obj)
            if result:  # Only return if there are actual attributes
                return result
        raise TypeError(f"Cannot convert {type(obj)} to dict")

    def _recurse(current: Any) -> Any:
        if current is None:
            return None
        if is_dataclass(current):
            current = asdict(current)
        if isinstance(current, dict):
            result = {}
            for k, v in current.items():
                if v is None:
                    result[k] = None
                elif isinstance(v, dict):
                    result[k] = _recurse(v)
                elif isinstance(v, list):
                    result[k] = [_recurse(item) for item in v]
                elif serialize_objects and not isinstance(
                    v,
                    (
                        str,
                        int,
                        float,
                        bool,
                        list,
                        tuple,
                        dict,
                        Enum,
                        type(None),
                    ),
                ):
                    try:
                        result[k] = _recurse(_to_dict(v))
                    except TypeError:
                        result[k] = _to_str(v)
                else:
                    result[k] = _to_str(v)
            return result
        elif isinstance(current, list):
            return [_recurse(item) for item in current]
        else:
            return _to_str(current)

    return _recurse(input_data)


def dumps(
    input_data: Any,
    serialize_objects: bool = False,
    indent: int = 2,
):
    return json.dumps(
        jsonify_objects(input_data),
        indent=indent,
    )


# Tests
class Color(Enum):
    RED = "red"
    BLUE = "blue"


class User:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    def __repr__(self):
        return f"User({self.name!r}, {self.age})"


class Address:
    def __init__(self, city: str):
        self.city = city


class Person:
    def __init__(self, name: str, address: Address):
        self.name = name
        self.address = address


# Primitives
assert dumps(42) == '"42"'
assert dumps(3.14) == '"3.14"'
assert dumps("hello") == '"hello"'
assert dumps(True) == '"true"'
assert dumps(False) == '"false"'
assert dumps(None) == "null"

# Empty containers
assert dumps({}) == "{}"
assert dumps([]) == "[]"

# Simple dict
result = dumps({"a": 1, "b": 2})
assert '"a": "1"' in result
assert '"b": "2"' in result

# Nested dict
result = dumps({"outer": {"inner": 1}})
assert '"outer": {' in result
assert '"inner": "1"' in result

# List of dicts
result = dumps([{"a": 1}, {"b": 2}])
assert '"a": "1"' in result
assert '"b": "2"' in result

# List of primitives
result = dumps([1, 2, 3])
assert '"1"' in result
assert '"2"' in result
assert '"3"' in result

# Mixed nested
result = dumps({"list": [1, {"x": 2}], "y": 3})
assert '"list":' in result
assert '"x": "2"' in result

# None in dict
result = dumps({"a": None})
assert '"a": null' in result

# None in list
result = dumps([None, 1, 2])
assert "null" in result

# Enum
result = dumps({"color": Color.RED})
assert '"color": "red"' in result

# Object fallback to repr
result = dumps({"user": User("Alice", 30)})
assert "User('Alice', 30)" in result

# serialize_objects=True with nested object
result = dumps(
    {"person": Person("Bob", Address("NYC"))}, serialize_objects=True
)
assert '"name": "Bob"' in result
assert '"city": "NYC"' in result


# serialize_objects=True with object that has no __dict__
class NoDict:
    pass


result = dumps({"weird": NoDict()}, serialize_objects=True)
print(result)
assert "NoDict" in result

# Tuple (converted to list by json.dumps)
result = dumps((1, 2, 3))
assert "1" in result

# Deeply nested
result = dumps({"a": {"b": {"c": {"d": 1}}}})
assert '"d": "1"' in result

# Special characters in string
result = dumps({"text": "hello\nworld"})
assert "hello\\nworld" in result

# Empty string
result = dumps({"empty": ""})
assert '"empty": ""' in result

# Negative numbers
assert dumps(-42) == '"-42"'

# Scientific notation
assert dumps(1e10) == '"10000000000.0"'

# Custom indent
result = dumps({"a": 1}, indent=4)
assert "    " in result

from dataclasses import dataclass


@dataclass
class User:
    name: str
    age: int


@dataclass
class Person:
    name: str
    address: "Address"


@dataclass
class Address:
    city: str
    zip_code: int


# Dataclass without serialize_objects (falls back to repr)
result = dumps({"user": User("Alice", 30)})
print(result)

# Dataclass with serialize_objects=True
result = dumps(
    {"user": User("Alice", 30)},
    serialize_objects=True,
)
print(result)

# Nested dataclasses
result = dumps(
    {"person": Person("Bob", Address("NYC", "10001"))},
    serialize_objects=True,
)
print(result)

# List of dataclasses
result = dumps(
    {"users": [User("A", 1), User("B", 2)]},
    serialize_objects=True,
)
print(result)

print("All tests passed!")
