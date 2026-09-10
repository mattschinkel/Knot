from .addressing import *
from .values import *
from . import addressing
from . import values

from knot.types import *
__all__ = [
    'IntType', 'StringType', 'ListType', 'SetType', 'MapType',
    'TupleType', 'OptionType', 'NominalType', 'BaseType',
    'AnyType', 'UnionType', 'IntersectionType',
]

from .types import *
__all__ = [
    'IntType', 'StringType', 'ListType', 'SetType', 'MapType',
    'TupleType', 'OptionType', 'NominalType', 'BaseType',
    'AnyType', 'UnionType', 'IntersectionType',
]

from knot.nodes import DefNode
from knot.types import I32
from knot.env import Env
from knot.checker import infer_def

__all__ = ["DefNode", "I32", "Env", "infer_def"]

import sys

import sys

def __getattr__(name):
    # Import knot modules on demand
    from knot import nodes, types, env, values, addressing
    from knot.checker import *
    from knot.types import *
    from knot.nodes import *
    from knot.env import *
    from knot.values import *
    from knot.addressing import *
    from knot import addressing
    from knot import values
    from knot import env
    from knot import types
    from knot import nodes
    return globals()[name]
