def test_contract_init():
    from knot.contracts import Contract
    c = Contract()
    assert c is not None


def test_contract_repr():
    from knot.contracts import Contract
    c = Contract()
    assert repr(c) != ""
