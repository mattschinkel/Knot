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


def test_phase2_gate_vs_baseline():
    """T18: Phase 2 drift gate vs docs/drift_baseline.json."""
    import json
    from pathlib import Path

    raw = json.loads(Path("docs/drift_baseline.json").read_text(encoding="utf-8"))
    assert raw["phase"] == 2
    base = {
        Metric.M1_TOKEN_COUNT: raw["metrics"]["M1_token_count"],
        Metric.M2_GEN_ACCURACY: raw["metrics"]["M2_generation_accuracy"],
        Metric.M3_EDIT_ROUNDTRIP: raw["metrics"]["M3_edit_roundtrip"],
    }
    measurements = {
        Metric.M1_TOKEN_COUNT: 21.0,
        Metric.M2_GEN_ACCURACY: 1.0,
        Metric.M3_EDIT_ROUNDTRIP: 1.0,
        Metric.M4_PARTIAL_COHERENCE: None,
        Metric.M5_COMPILE_LATENCY: None,
    }
    report = check(2, measurements, base)
    assert report.gate_passed is True
    assert "Phase 2" in summarize(report)
