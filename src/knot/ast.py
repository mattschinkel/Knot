from typing import List, Optional, Any

class AstProp:
    def __init__(self, name: str, value: Any):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"AstProp({self.name!r}, {self.value!r})"


class AstNode:
    def __init__(self, label: str, children: List[Any] = None):
        self.label = label
        self.children = children or []

    def to_prop(self) -> List[AstProp]:
        return [AstProp("prop", child) for child in self.children]

    def __repr__(self):
        return f"AstNode({self.label!r}, {self.children!r})"

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        if not isinstance(other, AstNode):
            return False
        return (self.label == other.label and
                self.children == other.children)

    def __hash__(self):
        return hash((self.label, tuple(self.children)))

    def __lt__(self, other):
        return (self.label, self.children) < (other.label, other.children)
