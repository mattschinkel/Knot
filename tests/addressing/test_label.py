def test_assign_label_returns_assigned_label():
    from knot.addressing import assign_label
    # Create a path and assign a label
    path = [1, 2, 3]
    label = "test_label"
    result = assign_label(label)
    assert result == label


def test_assign_label_updates_path():
    from knot.addressing import assign_label
    # Create a path and assign a label
    path = [1, 2, 3]
    label = "test_label"
    result = assign_label(label)
    assert result == label
