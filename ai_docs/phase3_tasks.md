# Phase 3 Tasks (normalized for phase_crew.parse_tasks)

## Overview
Fragment-sized tasks for effects, capabilities, and contracts.
Do NOT recreate Phase 0 units/types already in `units.py` / `types.py`.
Final task is the drift-check gate.

---

## Tasks

| ID | Goal | File | Function/Class | Test |
|---|------|------|----------------|------|
| T1 | Define EffectCategory enum and EffectSet frozenset wrapper | `src/knot/effects.py` | `EffectSet` | `tests/effects/test_effects.py` |
| T2 | Define Capability and CapabilitySet | `src/knot/effects.py` | `CapabilitySet` | `tests/effects/test_capabilities.py` |
| T3 | EffectSet union intersection subset helpers | `src/knot/effects.py` | `compose_effects` | `tests/effects/test_compose.py` |
| T4 | Capability constraint check (needed subset of granted) | `src/knot/effects.py` | `check_capabilities` | `tests/effects/test_cap_check.py` |
| T5 | ContractAnnotation and Contract (requires guarantees ensures) | `src/knot/contracts.py` | `Contract` | `tests/contracts/test_contract.py` |
| T6 | check_requires on Contract against Env bindings | `src/knot/contracts.py` | `check_requires` | `tests/contracts/test_requires.py` |
| T7 | check_guarantees on result type | `src/knot/contracts.py` | `check_guarantees` | `tests/contracts/test_guarantees.py` |
| T8 | FnType carry optional effects and caps | `src/knot/types.py` | `FnType` | `tests/types/test_fn_effects.py` |
| T9 | Infer DEF/FN effect annotations when present on AST | `src/knot/checker.py` | `infer_fn` | `tests/checker/test_infer_fn_effects.py` |
| T10 | validate_effects at call sites vs FnType | `src/knot/effects.py` | `validate_call_effects` | `tests/effects/test_validate.py` |
| T11 | Property tests effects never raise and pure subset | `tests/effects/` | `test_no_raise`, `test_pure_ok` | `tests/effects/test_effects_prop.py` |
| T12 | Run drift-check gate vs docs/drift_baseline.json | `src/knot/drift.py` | `check()` | `tests/drift/test_drift.py` |

---

## Final Task: Drift-Check Gate (T12)
- **Owner:** R3 + R4
- **File:** `src/knot/drift.py`
- **Action:** Run `check()` for Phase 3; PENDING metrics do not fail; any REGRESSION fails the gate.
