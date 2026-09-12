"""Tests for golemc_bridge."""

from pathlib import Path

from golem.golemc_bridge import compile_prefer_golemc, compile_with_golemc
from golem.values import ErrorVal
from golem.vm.compiler import ProgramImage
from golem.vm.machine import VM
from golem.values import IntVal

FIXTURES = Path(__file__).resolve().parents[2] / "selfhost" / "fixtures"


def test_compile_with_golemc_square():
    src = (FIXTURES / "square.gol").read_text(encoding="utf-8").strip()
    img = compile_with_golemc(src)
    assert isinstance(img, ProgramImage)
    assert "square" in img.functions
    out = VM(img).call("square", [IntVal(32, 6)])
    assert isinstance(out, IntVal) and out.value == 36


def test_compile_prefer_golemc():
    img = compile_prefer_golemc("ADD[2,3]")
    assert isinstance(img, ProgramImage)
    assert "__main" in img.functions or len(img.functions) >= 1
