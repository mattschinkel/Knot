from typing import Any, Tuple

from knot.values import TypeErrorVal

def type_error(message: str, path: tuple) -> TypeErrorVal:
    return TypeErrorVal(message, path)

class TypeErrorVal:
    """A value representing a type error with a message and path."""
    def __init__(self, msg: str, path: Tuple[Any, ...]):
        self.msg = msg
        self.path = path
    def __repr__(self):
        return f"TypeErrorVal({self.msg!r}, {self.path!r})"
    def __str__(self):
        return f"TypeError: {self.msg} at {self.path!r}"
