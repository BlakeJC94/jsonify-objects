import json
from dataclasses import asdict, is_dataclass
from enum import Enum
from typing import Any


def jsonify_objects(
    input_data: Any,
    serialize_objects: bool = False,
) -> dict[str, Any]:
    """Convert any data with to a dict"""

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
