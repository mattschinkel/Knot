from typing import List, Any

class Node:
    def __init__(self, id: int, path: List[int], label: Any = None):
        self.id = id
        self.path = path
        self.label = label
        self.children = []

    def __repr__(self):
        return f"Node(id={self.id}, path={self.path}, label={self.label})"

class Program:
    def __init__(self, body: List[Any]):
        self.body = body

    def __repr__(self):
        return f"Program(body={self.body})"
