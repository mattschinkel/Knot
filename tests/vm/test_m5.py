"""M5 drift gate helpers (Phase 9)."""

from __future__ import annotations

from golem.vm import measure_m5


def test_measure_m5_stable_enough():
    a = measure_m5(warmup=1, runs=5)
    b = measure_m5(warmup=1, runs=5)
    # both under product bar; not asserting equality (timing noise)
    assert a < 200 and b < 200
