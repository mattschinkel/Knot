from knot.addressing import generate_path
def test_generate_path_absolute():
    path = generate_path(1, 1, 2, 3)
    assert path.id == 1
    assert path.path == [1, 2, 3]


def test_generate_path_root():
    path = generate_path(0, 1, 2)
    assert path.id == 0
    assert path.path == [1, 2]


def test_generate_path_tilde():
    path = generate_path(2, 1, 2)
    assert path.id == 2
    assert path.path == [1, 2]


def test_generate_path_with_label():
    path = generate_path(1, 1, 2, label="test_label")
    assert path.id == 1
    assert path.path == [1, 2]
    assert path.label == "test_label"


def test_generate_path_empty_path():
    path = generate_path(1)
    assert path.id == 1
    assert path.path == []


def test_generate_path_multiple_parts():
    path = generate_path(1, 1, 2, 3, 4)
    assert path.id == 1
    assert path.path == [1, 2, 3, 4]


def test_generate_path_absolute():
    path = generate_path(1, 1, 2, 3)
    assert path.id == 1
    assert path.path == [1, 2, 3]


def test_generate_path_root():
    path = generate_path(0, 1, 2)
    assert path.id == 0
    assert path.path == [1, 2]


def test_generate_path_home():
    path = generate_path(2, 1, 2)
    assert path.id == 2
    assert path.path == [1, 2]


def test_generate_path_with_empty_parts():
    path = generate_path(1)
    assert path.id == 1
    assert path.path == []


def test_generate_path_multiple_parts():
    path = generate_path(1, 1, 2, 3, 4)
    assert path.id == 1
    assert path.path == [1, 2, 3, 4]
