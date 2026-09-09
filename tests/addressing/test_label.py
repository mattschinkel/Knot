from knot.addressing import assign_label, lookup_label


def test_assign_label_returns_label():
    assert assign_label("guard") == "guard"


def test_assign_label_roundtrip():
    node = object()
    assert assign_label("body", node) == "body"
    assert lookup_label("body") is node
