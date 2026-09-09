"""Phase-gate drift check tests (T30)."""
from knot.drift import Metric, Status, check, summarize


def test_check_all_pending_passes():
    report = check(1, {m: None for m in Metric})
    assert report.phase == 1
    assert report.gate_passed is True
    assert all(r.status == Status.PENDING for r in report.results)


def test_check_no_regression_passes():
    measurements = {
        Metric.M1_TOKEN_COUNT: 100.0,
        Metric.M2_GEN_ACCURACY: 0.9,
        Metric.M3_EDIT_ROUNDTRIP: 0.95,
        Metric.M4_PARTIAL_COHERENCE: None,
        Metric.M5_COMPILE_LATENCY: None,
    }
    baseline = {
        Metric.M1_TOKEN_COUNT: 110.0,
        Metric.M2_GEN_ACCURACY: 0.85,
        Metric.M3_EDIT_ROUNDTRIP: 0.9,
    }
    report = check(1, measurements, baseline)
    assert report.gate_passed is True
    assert any(r.status == Status.PASS for r in report.results)


def test_check_regression_fails_gate():
    measurements = {Metric.M1_TOKEN_COUNT: 200.0}  # higher token count = worse
    baseline = {Metric.M1_TOKEN_COUNT: 100.0}
    # Other metrics omitted -> PENDING
    full = {m: measurements.get(m) for m in Metric}
    report = check(1, full, baseline)
    assert report.gate_passed is False
    assert any(r.status == Status.REGRESSION for r in report.results)


def test_summarize_mentions_phase():
    report = check(1, {m: None for m in Metric})
    text = summarize(report)
    assert "Phase 1" in text
    assert "PASS" in text
