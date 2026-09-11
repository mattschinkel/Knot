from typing import Any, Callable, Dict, Optional

class ContractAnnotation:
    def __init__(self, pre=None, post=None, ensures=None, guarantees=None):
        self.pre = pre
        self.post = post
        self.ensures = ensures
        self.guarantees = guarantees or {}

class Contract:
    def __init__(self, pre=None, post=None, ensures=None):
        self.pre = pre
        self.post = post
        self.ensures = ensures

    def __repr__(self):
        return f"Contract(pre={self.pre}, post={self.post}, ensures={self.ensures})"

    def __eq__(self, other):
        if not isinstance(other, Contract):
            return False
        return (self.pre == other.pre and 
                self.post == other.post and 
                self.ensures == other.ensures)

    def __hash__(self):
        return hash((self.pre, self.post, self.ensures))

ContractPre = Callable[[Any], bool]
ContractPost = Callable[[Any], bool]
ContractEnsures = Callable[[Any], bool]
ContractGuarantees = Dict[str, Callable[[Any], bool]]
ContractAnnotation = ContractAnnotation
Contract = Contract
