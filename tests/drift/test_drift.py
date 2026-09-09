def test_check_phase_only():
    from knot.drift import check
    report = check("phase1")
    assert report.phase == "phase1"
    assert report.baseline is None


def test_check_phase_with_baseline():
    from knot.drift import check
    report = check("phase2", baseline=100)
    assert report.phase == "phase2"
    assert report.baseline == 100


def test_check_returns_drift_report():
    from knot.drift import check
    report = check("phase3")
    assert isinstance(report, DriftReport)


def test_check_phase_with_negative_baseline():
    from knot.drift import check
    report = check("phase4", baseline=-50)
    assert report.phase == "phase4"
    assert report.baseline == -50


def test_check_phase_only():
    from knot.drift import check
    report = check("phase1")
    assert report.phase == "phase1"


def test_check_with_baseline():
    from knot.drift import check
    report = check("phase2", baseline=100)
    assert report.phase == "phase2"
    assert report.baseline == 100


def test_check_returns_drift_report():
    from knot.drift import check
    report = check("phase3")
    assert hasattr(report, "phase")
    assert hasattr(report, "baseline")
    assert hasattr(report, "drift")


def test_check_with_drift_calculation():
    from knot.drift import check
    report = check("phase6", baseline=100)
    assert report.phase == "phase6"
    assert report.baseline == 100
    assert report.drift == 0.0
== 0.0
