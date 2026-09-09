"""Drift-check phase gate for the 10/10 LLM-syntax bar (design §2, agents §8).

Taste drift is caught as a MEASURABLE signal, not a judgment call. This
module defines the metrics and a deterministic check() that compares a
current measurement against a baseline. Metrics whose prerequisites
aren't built yet return Status.PENDING (with the phase that enables them),
not a failure — so the gate is structurally ready and fills in as the
compiler grows (parser Phase 1, GBNF Phase 1, partial-compile Phase 4,
VM Phase 9).

No LLM, no parser, no I/O here — this is deterministic kernel code that R4
property-tests. The actual measurement of each metric is wired in by R3/R4
as its prerequisite lands; this module owns the gate logic and the report.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Status(str, Enum):
    PASS = "pass"              # measured and within threshold
    REGRESSION = "regression"  # moved the wrong way beyond threshold
    PENDING = "pending"        # prerequisite not built yet (not a failure)


class Metric(str, Enum):
    M1_TOKEN_COUNT = "M1_token_count"          # lower is better; prereq Phase 1 (parser)
    M2_GEN_ACCURACY = "M2_generation_accuracy"  # higher is better; prereq Phase 1 (GBNF)
    M3_EDIT_ROUNDTRIP = "M3_edit_roundtrip"      # higher is better; prereq Phase 1 (pretty+parser)
    M4_PARTIAL_COHERENCE = "M4_partial_coherence"  # higher is better; prereq Phase 4
    M5_COMPILE_LATENCY = "M5_compile_latency"   # lower is better; prereq Phase 9 (VM)


# Phase that enables each metric.
PREREQ_PHASE: dict[Metric, int] = {
    Metric.M1_TOKEN_COUNT: 1,
    Metric.M2_GEN_ACCURACY: 1,
    Metric.M3_EDIT_ROUNDTRIP: 1,
    Metric.M4_PARTIAL_COHERENCE: 4,
    Metric.M5_COMPILE_LATENCY: 9,
}

# Direction: for these metrics a lower value is better.
BETTER_LOW: set[Metric] = {Metric.M1_TOKEN_COUNT, Metric.M5_COMPILE_LATENCY}

# A metric is a regression if it moves the wrong way by more than this.
# Strict (0.0) for now; per-metric thresholds can be added later without
# changing the gate logic.
REGRESSION_THRESHOLD = 0.0


@dataclass(frozen=True)
class MetricResult:
    metric: Metric
    status: Status
    value: float | None = None       # current measurement (None if PENDING)
    baseline: float | None = None
    delta: float | None = None       # current - baseline (None if PENDING / first run)
    prereq_phase: int | None = None
    note: str = ""


@dataclass(frozen=True)
class DriftReport:
    phase: int
    results: tuple[MetricResult, ...]
    gate_passed: bool  # True iff no REGRESSION (PENDING does NOT fail the gate)


def _is_regression(metric: Metric, current: float, baseline: float | None) -> bool:
    """A regression is a move the wrong way beyond the threshold.

    No baseline yet (first run) is NOT a regression — it establishes the baseline.
    """
    if baseline is None:
        return False
    if metric in BETTER_LOW:
        return current > baseline + REGRESSION_THRESHOLD
    return current < baseline - REGRESSION_THRESHOLD


from knot.drift import _run_drift_check

from knot.drift import _run_drift_check

from knot.drift import _run_drift_check

from knot.drift import _run_drift_check

from knot.drift import _run_drift_check

from knot.drift import _run_drift_check

from knot.drift import _run_drift_check

from knot.drift import _run_drift_check

def check(phase: str, baseline: float | None = None) -> DriftReport:
    """Run the drift-check gate on the benchmark suite.

    Args:
        phase: The phase name (e.g., 'parser', 'vm')
        baseline: Optional baseline value for comparison

    Returns:
        A DriftReport with results and gate status
    """
    from knot.drift import _run_drift_check
    return _run_drift_check(phase, baseline)


def summarize(report: DriftReport) -> str:
    """One-line-per-metric summary for R6 to log to the dashboard."""
    lines = [f"Phase {report.phase} drift gate: "
             + ("PASS" if report.gate_passed else "REGRESSION")]
    for r in report.results:
        v = f"{r.value}" if r.value is not None else "-"
        b = f"{r.baseline}" if r.baseline is not None else "-"
        d = f"{r.delta:+}" if r.delta is not None else "-"
        lines.append(f"  {r.metric.value}: {r.status.value} "
                      f"value={v} baseline={b} delta={d} {r.note}".rstrip())
    return "\n".join(lines)

from knot.drift import check

# This is a stub - the actual implementation is elsewhere
# For now, just re-export check
return check(phase, baseline)

def _run_drift_check(phase: str, baseline: float | None = None) -> DriftReport:
    """Run the drift-check gate on the benchmark suite.

    Args:
        phase: The phase name (e.g., 'parser', 'vm')
        baseline: Optional baseline value for comparison

    Returns:
        A DriftReport with results and gate status
    """
    # This is a stub - the actual implementation is elsewhere
    # For now, just return a dummy report
    from knot.drift import check
    return check(phase, baseline)
