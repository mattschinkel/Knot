from typing import Union

__all__ = ["IntVal", "BoolVal"]

class IntVal:
    def __init__(self, value: int):
        self.value = value

    def __repr__(self):
        return f"IntVal({self.value})"

class BoolVal:
    def __init__(self, value: bool):
        self.value = value

    def __repr__(self):
        return f"BoolVal({self.value})"
