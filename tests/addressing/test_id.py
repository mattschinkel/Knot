def test_generate_id_increments_sequentially():
    from knot.addressing import generate_id
    assert generate_id() == "node_0"
    assert generate_id() == "node_1"
    assert generate_id() == "node_2"


def test_generate_id_returns_node_prefix():
    from knot.addressing import generate_id
    assert generate_id() == "node_0"
