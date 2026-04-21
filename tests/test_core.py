from dataclasses import dataclass
from enum import Enum

import pytest
from jsonify_objects import dumps


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


class NoDict:
    pass


@dataclass
class UserDataclass:
    name: str
    age: int


@dataclass
class AddressDataclass:
    city: str
    zip_code: str


@dataclass
class PersonDataclass:
    name: str
    address: AddressDataclass


# Primitives
@pytest.mark.parametrize(
    "input_data, expected",
    [
        (42, '"42"'),
        (3.14, '"3.14"'),
        ("hello", '"hello"'),
        (True, '"true"'),
        (False, '"false"'),
        (None, "null"),
        ({}, "{}"),
        ([], "[]"),
        (-42, '"-42"'),
        (1e10, '"10000000000.0"'),
    ],
)
def test_primitives(input_data, expected):
    assert dumps(input_data) == expected


def test_simple_dict():
    result = dumps({"a": 1, "b": 2})
    assert '"a": "1"' in result
    assert '"b": "2"' in result


def test_nested_dict():
    result = dumps({"outer": {"inner": 1}})
    assert '"outer": {' in result
    assert '"inner": "1"' in result


def test_list_of_dicts():
    result = dumps([{"a": 1}, {"b": 2}])
    assert '"a": "1"' in result
    assert '"b": "2"' in result


def test_list_of_primitives():
    result = dumps([1, 2, 3])
    assert '"1"' in result
    assert '"2"' in result
    assert '"3"' in result


def test_mixed_nested():
    result = dumps({"list": [1, {"x": 2}], "y": 3})
    assert '"list":' in result
    assert '"x": "2"' in result


def test_none_in_dict():
    result = dumps({"a": None})
    assert '"a": null' in result


def test_none_in_list():
    result = dumps([None, 1, 2])
    assert "null" in result


def test_tuple_converted_to_list():
    result = dumps((1, 2, 3))
    assert "1" in result


def test_deeply_nested():
    result = dumps({"a": {"b": {"c": {"d": 1}}}})
    assert '"d": "1"' in result


def test_enum():
    result = dumps({"color": Color.RED})
    assert '"color": "red"' in result


# Object fallback to repr
def test_no_serialize_repr_fallback():
    result = dumps({"user": User("Alice", 30)})
    assert "User('Alice', 30)" in result


def test_serialize_nested_object():
    result = dumps(
        {"person": Person("Bob", Address("NYC"))}, serialize_objects=True
    )
    assert '"name": "Bob"' in result
    assert '"city": "NYC"' in result


def test_serialize_no_dict_attr():
    result = dumps({"weird": NoDict()}, serialize_objects=True)
    assert "NoDict" in result


def test_string_special_chars():
    result = dumps({"text": "hello\nworld"})
    assert "hello\\nworld" in result


def test_string_empty():
    result = dumps({"empty": ""})
    assert '"empty": ""' in result


def test_custom_indent():
    result = dumps({"a": 1}, indent=4)
    assert "    " in result


def test_dataclass_no_serialize():
    result = dumps({"user": UserDataclass("Alice", 30)})
    assert "UserDataclass(name='Alice', age=30)" in result


def test_dataclass_serialize():
    result = dumps(
        {"user": UserDataclass("Alice", 30)},
        serialize_objects=True,
    )
    assert '"name": "Alice"' in result
    assert '"age": 30' in result


def test_dataclass_serialize_nested():
    result = dumps(
        {"person": PersonDataclass("Bob", AddressDataclass("NYC", "10001"))},
        serialize_objects=True,
    )
    assert '"name": "Bob"' in result
    assert '"city": "NYC"' in result
    assert '"zip_code": "10001"' in result


def test_dataclass_serialize_list():
    result = dumps(
        {"users": [UserDataclass("A", 1), User("B", 2)]},
        serialize_objects=True,
    )
    assert '"name": "A"' in result
    assert '"age": 1' in result
    assert '"name": "B"' in result
    assert '"age": 2' in result
