"""CLI + rebuild loop for stable golemc workflow."""

from __future__ import annotations

from pathlib import Path

from golem.__main__ import main
from golem.golemc_bridge import rebuild_golemc, run_with_golemc
from golem.values import ErrorVal, IntVal, SumVal

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "selfhost" / "fixtures"
STAGE1 = ROOT / "selfhost" / "stage1"


def test_cli_run_expr(tmp_path, capsys):
    f = tmp_path / "t.gol"
    f.write_text("ADD[2,3]\n", encoding="utf-8")
    assert main(["run", str(f)]) == 0
    out = capsys.readouterr().out
    assert '"ok": true' in out


def test_cli_compile_root(capsys):
    assert main(["compile", "--root", str(FIXTURES), "--root-file", "link_root.gol"]) == 0
    out = capsys.readouterr().out
    assert '"ok": true' in out
    assert "one" in out


def test_run_with_golemc_square():
    src = (FIXTURES / "square.gol").read_text(encoding="utf-8")
    # square.gol is DEF only — call square
    from golem.golemc_bridge import compile_with_golemc
    from golem.vm.machine import VM

    img = compile_with_golemc(src)
    assert not isinstance(img, ErrorVal)
    out = VM(img).call("square", [IntVal(32, 5)])
    assert out == IntVal(32, 25)


def test_rebuild_roundtrip_golem():
    """Golem rebuild_roundtrip: compile_root stage1 then CALL_PROGRAM compile_source."""
    r = rebuild_golemc(STAGE1, probe="ADD[6,1]")
    assert isinstance(r, SumVal) and r.tag == "Ok", r
    prog = r.payload
    assert isinstance(prog, SumVal) and prog.tag == "Program"


def test_cli_rebuild(capsys):
    assert main(["rebuild", str(STAGE1), "--probe", "MUL[3,3]"]) == 0
    out = capsys.readouterr().out
    assert '"ok": true' in out
    assert '"rebuilt": true' in out
