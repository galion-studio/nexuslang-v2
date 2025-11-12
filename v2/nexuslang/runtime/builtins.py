"""Built-in functions for NexusLang"""

import sys
from typing import Any, Dict, Callable


def builtin_print(*args):
    """Print values to stdout"""
    print(*args)


def builtin_len(obj):
    """Get length of object"""
    return len(obj)


def builtin_range(start, end=None, step=1):
    """Create a range"""
    if end is None:
        return list(range(start))
    return list(range(start, end, step))


def builtin_type(obj):
    """Get type of object"""
    return type(obj).__name__


def builtin_str(obj):
    """Convert to string"""
    return str(obj)


def builtin_int(obj):
    """Convert to integer"""
    return int(obj)


def builtin_float(obj):
    """Convert to float"""
    return float(obj)


def builtin_bool(obj):
    """Convert to boolean"""
    return bool(obj)


def builtin_input(prompt=""):
    """Read input from user"""
    return input(prompt)


def builtin_abs(x):
    """Absolute value"""
    return abs(x)


def builtin_min(*args):
    """Get minimum value"""
    return min(args)


def builtin_max(*args):
    """Get maximum value"""
    return max(args)


def builtin_sum(iterable):
    """Sum of values"""
    return sum(iterable)


def builtin_sqrt(x):
    """Square root"""
    import math
    return math.sqrt(x)


def builtin_pow(base, exp):
    """Power"""
    return base ** exp


def builtin_exit(code=0):
    """Exit the program"""
    sys.exit(code)


def get_builtins() -> Dict[str, Callable]:
    """Get all built-in functions"""
    return {
        "print": builtin_print,
        "len": builtin_len,
        "range": builtin_range,
        "type": builtin_type,
        "str": builtin_str,
        "int": builtin_int,
        "float": builtin_float,
        "bool": builtin_bool,
        "input": builtin_input,
        "abs": builtin_abs,
        "min": builtin_min,
        "max": builtin_max,
        "sum": builtin_sum,
        "sqrt": builtin_sqrt,
        "pow": builtin_pow,
        "exit": builtin_exit,
    }

