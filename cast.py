"""This module contains some functions for casting."""
from math import isnan


def to_bool(val):
    """Convert a value to a bool."""
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.lower() not in ("", "0", "false")
    return bool(val)


def to_number(val):
    """Convert a value to a number."""
    if isinstance(val, (int, float)):
        return 0 if isnan(val) else val
    try:
        casted = float(val)
        return 0 if isnan(casted) else casted
    except ValueError:
        return 0


def to_string(val):
    """Convert a value to a string."""
    return str(val)
