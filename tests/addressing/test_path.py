from knot.addressing import generate_path


def test_generate_path_empty():
    assert generate_path() == ()


def test_generate_path_empty_string():
    assert generate_path("") == ()


def test_generate_path_dotted_ints():
    assert generate_path("1.2.3") == (1, 2, 3)


def test_generate_path_tuple():
    assert generate_path((1, 2, 3)) == (1, 2, 3)


def test_generate_path_args():
    assert generate_path(1, 2, 3) == (1, 2, 3)


def test_generate_path_invalid_string():
    assert generate_path("!!!") == ()
