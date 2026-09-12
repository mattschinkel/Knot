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
    """Historical Phase 2 numbers still pass against current baseline values."""
    import json
    from pathlib import Path

    raw = json.loads(Path("docs/drift_baseline.json").read_text(encoding="utf-8"))
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


def test_phase3_gate_vs_baseline():
    """Phase 3 numbers still pass against current baseline values."""
    import json
    from pathlib import Path

    raw = json.loads(Path("docs/drift_baseline.json").read_text(encoding="utf-8"))
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
    report = check(3, measurements, base)
    assert report.gate_passed is True
    assert "Phase 3" in summarize(report)


def test_phase4_gate_vs_baseline():
    """Phase 4 numbers still pass; M4 measured from PARTIAL_SUITE."""
    import json
    from pathlib import Path

    from tests.partial.test_partial_prop import PARTIAL_SUITE
    from knot.partial import CompileStatus, compile_check

    raw = json.loads(Path("docs/drift_baseline.json").read_text(encoding="utf-8"))
    ok = sum(
        1 for n in PARTIAL_SUITE if compile_check(n).status is CompileStatus.PARTIAL
    )
    m4 = ok / len(PARTIAL_SUITE)
    base = {
        Metric.M1_TOKEN_COUNT: raw["metrics"]["M1_token_count"],
        Metric.M2_GEN_ACCURACY: raw["metrics"]["M2_generation_accuracy"],
        Metric.M3_EDIT_ROUNDTRIP: raw["metrics"]["M3_edit_roundtrip"],
        Metric.M4_PARTIAL_COHERENCE: raw["metrics"]["M4_partial_coherence"],
    }
    measurements = {
        Metric.M1_TOKEN_COUNT: 21.0,
        Metric.M2_GEN_ACCURACY: 1.0,
        Metric.M3_EDIT_ROUNDTRIP: 1.0,
        Metric.M4_PARTIAL_COHERENCE: m4,
        Metric.M5_COMPILE_LATENCY: None,
    }
    report = check(4, measurements, base)
    assert report.gate_passed is True
    assert m4 == 1.0
    assert "Phase 4" in summarize(report)


def test_phase5_gate_vs_baseline():
    """Phase 5 numbers still pass against current baseline values."""
    import json
    from pathlib import Path

    from tests.partial.test_partial_prop import PARTIAL_SUITE
    from knot.partial import CompileStatus, compile_check

    raw = json.loads(Path("docs/drift_baseline.json").read_text(encoding="utf-8"))
    ok = sum(
        1 for n in PARTIAL_SUITE if compile_check(n).status is CompileStatus.PARTIAL
    )
    m4 = ok / len(PARTIAL_SUITE)
    base = {
        Metric.M1_TOKEN_COUNT: raw["metrics"]["M1_token_count"],
        Metric.M2_GEN_ACCURACY: raw["metrics"]["M2_generation_accuracy"],
        Metric.M3_EDIT_ROUNDTRIP: raw["metrics"]["M3_edit_roundtrip"],
        Metric.M4_PARTIAL_COHERENCE: raw["metrics"]["M4_partial_coherence"],
    }
    measurements = {
        Metric.M1_TOKEN_COUNT: 21.0,
        Metric.M2_GEN_ACCURACY: 1.0,
        Metric.M3_EDIT_ROUNDTRIP: 1.0,
        Metric.M4_PARTIAL_COHERENCE: m4,
        Metric.M5_COMPILE_LATENCY: None,
    }
    report = check(5, measurements, base)
    assert report.gate_passed is True
    assert "Phase 5" in summarize(report)


def test_phase6_gate_vs_baseline():
    """Phase 6 numbers still pass against current baseline values."""
    import json
    from pathlib import Path

    from tests.partial.test_partial_prop import PARTIAL_SUITE
    from knot.partial import CompileStatus, compile_check

    raw = json.loads(Path("docs/drift_baseline.json").read_text(encoding="utf-8"))
    ok = sum(
        1 for n in PARTIAL_SUITE if compile_check(n).status is CompileStatus.PARTIAL
    )
    m4 = ok / len(PARTIAL_SUITE)
    base = {
        Metric.M1_TOKEN_COUNT: raw["metrics"]["M1_token_count"],
        Metric.M2_GEN_ACCURACY: raw["metrics"]["M2_generation_accuracy"],
        Metric.M3_EDIT_ROUNDTRIP: raw["metrics"]["M3_edit_roundtrip"],
        Metric.M4_PARTIAL_COHERENCE: raw["metrics"]["M4_partial_coherence"],
    }
    measurements = {
        Metric.M1_TOKEN_COUNT: 21.0,
        Metric.M2_GEN_ACCURACY: 1.0,
        Metric.M3_EDIT_ROUNDTRIP: 1.0,
        Metric.M4_PARTIAL_COHERENCE: m4,
        Metric.M5_COMPILE_LATENCY: None,
    }
    report = check(6, measurements, base)
    assert report.gate_passed is True
    assert "Phase 6" in summarize(report)


def test_phase7_gate_vs_baseline():
    """Phase 7 numbers still pass against current baseline values."""
    import json
    from pathlib import Path

    from tests.partial.test_partial_prop import PARTIAL_SUITE
    from knot.partial import CompileStatus, compile_check

    raw = json.loads(Path("docs/drift_baseline.json").read_text(encoding="utf-8"))
    ok = sum(
        1 for n in PARTIAL_SUITE if compile_check(n).status is CompileStatus.PARTIAL
    )
    m4 = ok / len(PARTIAL_SUITE)
    base = {
        Metric.M1_TOKEN_COUNT: raw["metrics"]["M1_token_count"],
        Metric.M2_GEN_ACCURACY: raw["metrics"]["M2_generation_accuracy"],
        Metric.M3_EDIT_ROUNDTRIP: raw["metrics"]["M3_edit_roundtrip"],
        Metric.M4_PARTIAL_COHERENCE: raw["metrics"]["M4_partial_coherence"],
    }
    measurements = {
        Metric.M1_TOKEN_COUNT: 21.0,
        Metric.M2_GEN_ACCURACY: 1.0,
        Metric.M3_EDIT_ROUNDTRIP: 1.0,
        Metric.M4_PARTIAL_COHERENCE: m4,
        Metric.M5_COMPILE_LATENCY: None,
    }
    report = check(7, measurements, base)
    assert report.gate_passed is True
    assert "Phase 7" in summarize(report)


def test_phase8_gate_vs_baseline():
    """Phase 8 numbers still pass against current baseline values."""
    import json
    from pathlib import Path

    from tests.partial.test_partial_prop import PARTIAL_SUITE
    from knot.partial import CompileStatus, compile_check

    raw = json.loads(Path("docs/drift_baseline.json").read_text(encoding="utf-8"))
    ok = sum(
        1 for n in PARTIAL_SUITE if compile_check(n).status is CompileStatus.PARTIAL
    )
    m4 = ok / len(PARTIAL_SUITE)
    base = {
        Metric.M1_TOKEN_COUNT: raw["metrics"]["M1_token_count"],
        Metric.M2_GEN_ACCURACY: raw["metrics"]["M2_generation_accuracy"],
        Metric.M3_EDIT_ROUNDTRIP: raw["metrics"]["M3_edit_roundtrip"],
        Metric.M4_PARTIAL_COHERENCE: raw["metrics"]["M4_partial_coherence"],
    }
    measurements = {
        Metric.M1_TOKEN_COUNT: 21.0,
        Metric.M2_GEN_ACCURACY: 1.0,
        Metric.M3_EDIT_ROUNDTRIP: 1.0,
        Metric.M4_PARTIAL_COHERENCE: m4,
        Metric.M5_COMPILE_LATENCY: None,
    }
    report = check(8, measurements, base)
    assert report.gate_passed is True
    assert "Phase 8" in summarize(report)


def test_phase9_gate_vs_baseline():
    """Phase 9 numbers still pass (M5 included)."""
    import json
    from pathlib import Path

    from tests.partial.test_partial_prop import PARTIAL_SUITE
    from knot.partial import CompileStatus, compile_check
    from knot.vm import measure_m5

    raw = json.loads(Path("docs/drift_baseline.json").read_text(encoding="utf-8"))
    ok = sum(
        1 for n in PARTIAL_SUITE if compile_check(n).status is CompileStatus.PARTIAL
    )
    m4 = ok / len(PARTIAL_SUITE)
    m5 = measure_m5()
    base = {
        Metric.M1_TOKEN_COUNT: raw["metrics"]["M1_token_count"],
        Metric.M2_GEN_ACCURACY: raw["metrics"]["M2_generation_accuracy"],
        Metric.M3_EDIT_ROUNDTRIP: raw["metrics"]["M3_edit_roundtrip"],
        Metric.M4_PARTIAL_COHERENCE: raw["metrics"]["M4_partial_coherence"],
        Metric.M5_COMPILE_LATENCY: raw["metrics"]["M5_compile_latency"],
    }
    measurements = {
        Metric.M1_TOKEN_COUNT: 21.0,
        Metric.M2_GEN_ACCURACY: 1.0,
        Metric.M3_EDIT_ROUNDTRIP: 1.0,
        Metric.M4_PARTIAL_COHERENCE: m4,
        Metric.M5_COMPILE_LATENCY: m5,
    }
    report = check(9, measurements, base)
    assert report.gate_passed is True
    assert m5 < 200.0
    assert "Phase 9" in summarize(report)


def test_phase10_gate_vs_baseline():
    """Phase 10 numbers still pass (M1–M5)."""
    import json
    from pathlib import Path

    from tests.partial.test_partial_prop import PARTIAL_SUITE
    from knot.partial import CompileStatus, compile_check
    from knot.vm import measure_m5

    raw = json.loads(Path("docs/drift_baseline.json").read_text(encoding="utf-8"))
    ok = sum(
        1 for n in PARTIAL_SUITE if compile_check(n).status is CompileStatus.PARTIAL
    )
    m4 = ok / len(PARTIAL_SUITE)
    m5 = measure_m5()
    base = {
        Metric.M1_TOKEN_COUNT: raw["metrics"]["M1_token_count"],
        Metric.M2_GEN_ACCURACY: raw["metrics"]["M2_generation_accuracy"],
        Metric.M3_EDIT_ROUNDTRIP: raw["metrics"]["M3_edit_roundtrip"],
        Metric.M4_PARTIAL_COHERENCE: raw["metrics"]["M4_partial_coherence"],
        Metric.M5_COMPILE_LATENCY: raw["metrics"]["M5_compile_latency"],
    }
    measurements = {
        Metric.M1_TOKEN_COUNT: 21.0,
        Metric.M2_GEN_ACCURACY: 1.0,
        Metric.M3_EDIT_ROUNDTRIP: 1.0,
        Metric.M4_PARTIAL_COHERENCE: m4,
        Metric.M5_COMPILE_LATENCY: m5,
    }
    report = check(10, measurements, base)
    assert report.gate_passed is True
    assert "Phase 10" in summarize(report)


def test_phase11_gate_vs_baseline():
    """Phase 11 numbers still pass (M1–M5)."""
    import json
    from pathlib import Path

    from tests.partial.test_partial_prop import PARTIAL_SUITE
    from knot.partial import CompileStatus, compile_check
    from knot.vm import measure_m5

    raw = json.loads(Path("docs/drift_baseline.json").read_text(encoding="utf-8"))
    ok = sum(
        1 for n in PARTIAL_SUITE if compile_check(n).status is CompileStatus.PARTIAL
    )
    m4 = ok / len(PARTIAL_SUITE)
    m5 = measure_m5()
    base = {
        Metric.M1_TOKEN_COUNT: raw["metrics"]["M1_token_count"],
        Metric.M2_GEN_ACCURACY: raw["metrics"]["M2_generation_accuracy"],
        Metric.M3_EDIT_ROUNDTRIP: raw["metrics"]["M3_edit_roundtrip"],
        Metric.M4_PARTIAL_COHERENCE: raw["metrics"]["M4_partial_coherence"],
        Metric.M5_COMPILE_LATENCY: raw["metrics"]["M5_compile_latency"],
    }
    measurements = {
        Metric.M1_TOKEN_COUNT: 21.0,
        Metric.M2_GEN_ACCURACY: 1.0,
        Metric.M3_EDIT_ROUNDTRIP: 1.0,
        Metric.M4_PARTIAL_COHERENCE: m4,
        Metric.M5_COMPILE_LATENCY: m5,
    }
    report = check(11, measurements, base)
    assert report.gate_passed is True
    assert "Phase 11" in summarize(report)


def test_phase12_gate_vs_baseline():
    """T5: Phase 12 drift gate (M1–M5 unchanged)."""
    import json
    from pathlib import Path

    from tests.partial.test_partial_prop import PARTIAL_SUITE
    from knot.partial import CompileStatus, compile_check
    from knot.vm import measure_m5

    raw = json.loads(Path("docs/drift_baseline.json").read_text(encoding="utf-8"))
    assert raw["phase"] == 12
    ok = sum(
        1 for n in PARTIAL_SUITE if compile_check(n).status is CompileStatus.PARTIAL
    )
    m4 = ok / len(PARTIAL_SUITE)
    m5 = measure_m5()
    base = {
        Metric.M1_TOKEN_COUNT: raw["metrics"]["M1_token_count"],
        Metric.M2_GEN_ACCURACY: raw["metrics"]["M2_generation_accuracy"],
        Metric.M3_EDIT_ROUNDTRIP: raw["metrics"]["M3_edit_roundtrip"],
        Metric.M4_PARTIAL_COHERENCE: raw["metrics"]["M4_partial_coherence"],
        Metric.M5_COMPILE_LATENCY: raw["metrics"]["M5_compile_latency"],
    }
    measurements = {
        Metric.M1_TOKEN_COUNT: 21.0,
        Metric.M2_GEN_ACCURACY: 1.0,
        Metric.M3_EDIT_ROUNDTRIP: 1.0,
        Metric.M4_PARTIAL_COHERENCE: m4,
        Metric.M5_COMPILE_LATENCY: m5,
    }
    report = check(12, measurements, base)
    assert report.gate_passed is True
    assert "Phase 12" in summarize(report)
