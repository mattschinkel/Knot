from knot.values import Value, IntVal, StrVal

class Program:
    def __init__(self, rules, id=1, path=None, label=None, children=None):
        self.rules = rules
        self.id = id
        self.path = path or [id]
        self.label = label
        self.children = children or []

    def __repr__(self):
        return f"Program(rules={self.rules}, id={self.id}, path={self.path}, label={self.label}, children={self.children})"

    def __eq__(self, other):
        if not isinstance(other, Program):
            return False
        return (self.rules == other.rules and
                self.id == other.id and
                self.path == other.path and
                self.label == other.label and
                self.children == other.children)

    def __hash__(self):
        return hash((self.rules, self.id, self.path, self.label, tuple(self.children)))

    def __str__(self):
        return self.__repr__()
