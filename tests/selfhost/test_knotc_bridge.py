"""Tests for knotc_bridge."""

from pathlib import Path

from knot.knotc_bridge import compile_prefer_knotc, compile_with_knotc
from knot.values import ErrorVal
from knot.vm.compiler import ProgramImage
from knot.vm.machine import VM
from knot.values import IntVal

FIXTURES = Path(__file__).resolve().parents[2] / "selfhost" / "fixtures"


def test_compile_with_knotc_square():
    src = (FIXTURES / "square.knot").read_text(encoding="utf-8").strip()
    img = compile_with_knotc(src)
    assert isinstance(img, ProgramImage)
    assert "square" in img.functions
    out = VM(img).call("square", [IntVal(32, 6)])
    assert isinstance(out, IntVal) and out.value == 36


def test_compile_prefer_knotc():
    img = compile_prefer_knotc("ADD[2,3]")
    assert isinstance(img, ProgramImage)
    assert "__main" in img.functions or len(img.functions) >= 1
