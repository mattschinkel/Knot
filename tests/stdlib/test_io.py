"""FS_READ / FS_WRITE / PRINT with capabilities."""

from __future__ import annotations

from pathlib import Path

from knot.effects import Capability, CapabilitySet
from knot.parser import parse_expr
from knot.partial import evaluate
from knot.values import BytesVal, ErrorVal, StringVal, UnitVal


def test_fs_read_denied():
    r = evaluate(parse_expr("FS_READ['/tmp/x']"), granted_caps=CapabilitySet())
    assert isinstance(r, ErrorVal)
    assert r.err.kind == "capability"


def test_fs_write_read_roundtrip(tmp_path):
    p = tmp_path / "t.txt"
    path = str(p)
    caps = CapabilitySet([Capability.FS_READ, Capability.FS_WRITE])
    # write via AIR — need string path lit
    w = evaluate(
        parse_expr("FS_WRITE['" + path.replace("\\", "/") + "','hello']"),
        granted_caps=caps,
    )
    assert isinstance(w, UnitVal)
    r = evaluate(
        parse_expr("FS_READ['" + path.replace("\\", "/") + "']"),
        granted_caps=caps,
    )
    assert isinstance(r, BytesVal)
    assert r.value == b"hello"


def test_print_needs_cap():
    r = evaluate(parse_expr("PRINT[1]"), granted_caps=CapabilitySet())
    assert isinstance(r, ErrorVal)
    r2 = evaluate(
        parse_expr("PRINT['ok']"),
        granted_caps=CapabilitySet([Capability.IO_STDOUT]),
    )
    assert isinstance(r2, UnitVal)
