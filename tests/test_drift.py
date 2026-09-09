"""Property tests for the drift-check phase gate (Phase 0 / design §8)."""

from __future__ import annotations

from knot.drift import (
    Metric, Status, check, summarize, PREREQ_PHASE, BETTER_LOW,
)


def test_all_pending_when_no_prereqs_built():
    # Before Phase 1, every metric's prerequisite is unmet -> all PENDING, gate passes.
    r = check(phase=0, measurements={})
    assert r.gate_passed is True
    assert all(res.status == Status.PENDING for res in r.results)
    assert all(res.value is None for res in r.results)
    # Each PENDING result names the phase that enables it.
    for res in r.results:
        assert res.prereq_phase == PREREQ_PHASE[res.metric]


def test_pending_does_not_fail_gate():
    # A mix of PENDING and PASS still passes (PENDING is not a failure).
    r = check(phase=1, measurements={Metric.M1_TOKEN_COUNT: 120.0})
    m1 = next(res for res in r.results if res.metric == Metric.M1_TOKEN_COUNT)
    assert m1.status == Status.PASS
    assert m1.value == 120.0
    assert r.gate_passed is True


def test_first_run_is_not_a_regression():
    # First measurement (no baseline) establishes the baseline, not a regression.
    r = check(phase=1, measurements={Metric.M1_TOKEN_COUNT: 100.0})
    m1 = next(res for res in r.results if res.metric == Metric.M1_TOKEN_COUNT)
    assert m1.status == Status.PASS
    assert m1.delta is None  # no baseline -> no delta
    assert r.gate_passed is True


def test_regression_lower_is_better():
    # M1 (token count) lower is better. Going UP from baseline is a regression.
    base = {Metric.M1_TOKEN_COUNT: 100.0}
    r = check(phase=1, measurements={Metric.M1_TOKEN_COUNT: 130.0}, baseline=base)
    m1 = next(res for res in r.results if res.metric == Metric.M1_TOKEN_COUNT)
    assert m1.status == Status.REGRESSION
    assert m1.delta == 30.0
    assert r.gate_passed is False


def test_improvement_lower_is_better():
    # M1 going DOWN is an improvement, not a regression.
    base = {Metric.M1_TOKEN_COUNT: 100.0}
    r = check(phase=1, measurements={Metric.M1_TOKEN_COUNT: 90.0}, baseline=base)
    m1 = next(res for res in r.results if res.metric == Metric.M1_TOKEN_COUNT)
    assert m1.status == Status.PASS
    assert r.gate_passed is True


def test_regression_higher_is_better():
    # M2 (generation accuracy) higher is better. Going DOWN is a regression.
    base = {Metric.M2_GEN_ACCURACY: 0.95}
    r = check(phase=1, measurements={Metric.M2_GEN_ACCURACY: 0.80}, baseline=base)
    m2 = next(res for res in r.results if res.metric == Metric.M2_GEN_ACCURACY)
    assert m2.status == Status.REGRESSION
    assert r.gate_passed is False


def test_one_regression_fails_whole_gate():
    base = {Metric.M1_TOKEN_COUNT: 100.0, Metric.M2_GEN_ACCURACY: 0.9}
    r = check(phase=1,
              measurements={Metric.M1_TOKEN_COUNT: 100.0,  # pass
                            Metric.M2_GEN_ACCURACY: 0.5},  # regression
              baseline=base)
    assert r.gate_passed is False
    assert any(res.status == Status.REGRESSION for res in r.results)
    assert any(res.status == Status.PASS for res in r.results)


def test_report_is_frozen_and_hashable():
    r = check(phase=1, measurements={})
    assert hash(r) == hash(check(phase=1, measurements={}))
    import dataclasses
    try:
        r.phase = 2  # type: ignore[misc]
        raise AssertionError("expected frozen")
    except dataclasses.FrozenInstanceError:
        pass


def test_summarize_runs():
    r = check(phase=1, measurements={Metric.M1_TOKEN_COUNT: 100.0})
    s = summarize(r)
    assert "Phase 1 drift gate: PASS" in s
    assert "M1_token_count: pass" in s


def test_better_low_set_consistent():
    # M1 and M5 are lower-is-better; the rest are higher-is-better.
    assert BETTER_LOW == {Metric.M1_TOKEN_COUNT, Metric.M5_COMPILE_LATENCY}
