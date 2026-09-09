from abc import ABC, abstractmethod

class Value(ABC):
    """Abstract base class for all values."""
    pass

from dataclasses import dataclass

def __init__(self, values):
    self.values = values

def __repr__(self):
    return f"Program({self.values})"

def __len__(self):
    return len(self.values)

def __getitem__(self, index):
    return self.values[index]

from dataclasses import dataclass

def __init__(self, label, children=None):
    self.label = label
    self.children = children or []

def __repr__(self):
    return f"Value({self.label})"

def __len__(self):
    return len(self.children)

def __getitem__(self, index):
    return self.children[index]

from dataclasses import dataclass

def __init__(self, label, children=None):
    self.label = label
    self.children = children or []

def __repr__(self):
    return f"Bracketed({self.label})"

def __len__(self):
    return len(self.children)

def __getitem__(self, index):
    return self.children[index]

from dataclasses import dataclass

def __init__(self, label, children=None):
    self.label = label
    self.children = children or []

def __repr__(self):
    return f"BracketedValue({self.label})"

def __len__(self):
    return len(self.children)

def __getitem__(self, index):
    return self.children[index]

@dataclass
class Program:
    values: list[Value]

@dataclass
class Bracketed:
    label: str
    children: list[Value]

@dataclass
class BracketedValue:
    label: str
    children: list[Value]

@dataclass
class Value:
    label: str
    children: list[Value]
