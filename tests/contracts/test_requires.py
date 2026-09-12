"""check_requires against Env bindings (Phase 3 T6)."""

from __future__ import annotations

from golem.contracts import Contract, check_requires
from golem.env import Env
from golem.types import F64, I32, STRING


def test_check_requires_empty():
    env = Env()
    assert check_requires(Contract(), env) is True


def test_check_requires_bound_ok():
    env = Env()
    env.bind("x", F64)
    c = Contract(requires={"x": F64})
    assert check_requires(c, env) is True


def test_check_requires_missing():
    env = Env()
    env.bind("x", F64)
    c = Contract(requires={"y": F64})
    assert check_requires(c, env) is False


def test_check_requires_type_mismatch():
    env = Env()
    env.bind("x", I32)
    c = Contract(requires={"x": STRING})
    assert check_requires(c, env) is False


def test_check_requires_multiple():
    env = Env()
    env.bind("x", F64)
    env.bind("y", I32)
    c = Contract(requires={"x": F64, "y": I32})
    assert check_requires(c, env) is True


def test_check_requires_partial_missing():
    env = Env()
    env.bind("x", F64)
    c = Contract(requires={"x": F64, "y": I32})
    assert check_requires(c, env) is False
