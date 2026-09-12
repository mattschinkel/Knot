"""Phase 11 properties."""

from __future__ import annotations

from golem.canonical import normalize
from golem.checker import infer_type
from golem.parser import parse_expr
from golem.partial import evaluate
from golem.types import TupleType
from golem.values import TupleVal


def test_par_infer_tuple():
    t = infer_type(parse_expr("PAR[1,2]"))
    assert isinstance(t, TupleType)
    assert len(t.elems) == 2


def test_par_eval_no_raise():
    r = evaluate(parse_expr("PAR[ADD[1,1],ADD[2,2],ADD[3,3]]"))
    assert isinstance(r, TupleVal)
    assert [x.value for x in r.items] == [2, 4, 6]


def test_normalize_idempotent():
    for s in ("PAR[1,2]", "SEQ[1]", "REF[a,1]", "DEREF[REF[a,1]]", "UNSAFE[CAPS[],0]"):
        assert normalize(normalize(s)) == normalize(s)
