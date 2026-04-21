import json
from dataclasses import asdict, is_dataclass
from enum import Enum
from typing import Any


def jsonify_objects(
    input_data: Any,
    serialize_objects: bool = False,
) -> dict[str, Any]:
    """Convert any data with to a dict"""

    def _to_str(val: Any) -> str:  # noqa: PLR0911 (too many returns)
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

    def _recurse(  # noqa: PLR0912 (too many branches)
        current: Any,
        from_dataclass: bool = False,
    ) -> Any:
        if current is None:
            return None
        if is_dataclass(current):
            # AIDEV-NOTE: asdict flattens nested dataclasses; from_dataclass
            # ensures numeric fields keep their native JSON types downstream
            current = asdict(current)
            from_dataclass = True
        if isinstance(current, dict):
            result = {}
            for k, v in current.items():
                if v is None:
                    result[k] = None
                elif isinstance(v, dict):
                    result[k] = _recurse(v, from_dataclass)
                elif isinstance(v, list):
                    result[k] = [_recurse(item, from_dataclass) for item in v]
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
                    # recurse directly so is_dataclass check fires if needed;
                    # True preserves numeric types from expanded object fields
                    result[k] = _recurse(v, True)
                elif from_dataclass and isinstance(v, (int, float, bool)):
                    result[k] = v
                else:
                    result[k] = _to_str(v)
            return result
        elif isinstance(current, list):
            return [_recurse(item, from_dataclass) for item in current]
        elif serialize_objects and not isinstance(
            current,
            (str, int, float, bool, Enum, type(None)),
        ):
            try:
                return _recurse(_to_dict(current), True)
            except TypeError:
                return _to_str(current)
        else:
            return _to_str(current)

    return _recurse(input_data)


def dumps(
    input_data: Any,
    serialize_objects: bool = False,
    indent: int = 2,
):
    return json.dumps(
        jsonify_objects(
            input_data,
            serialize_objects=serialize_objects,
        ),
        indent=indent,
    )
