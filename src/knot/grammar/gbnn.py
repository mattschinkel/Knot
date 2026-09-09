from knot.values import Value, IntVal, StrVal

class Program:
    def __init__(self, rules):
        self.rules = rules

    def __repr__(self):
        return f"Program(rules={self.rules})"
