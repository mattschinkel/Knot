from knot.addressing import generate_id, reset_ids


def test_generate_id_increments():
    reset_ids()
    assert generate_id() == 0
    assert generate_id() == 1
    assert generate_id() == 2


def test_generate_id_is_int():
    reset_ids()
    assert isinstance(generate_id(), int)
