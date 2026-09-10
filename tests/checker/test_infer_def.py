def test_infer_def_simple():
    from knot.checker import infer_def
    from knot.nodes import DefNode
    from knot.types import I32
    from knot.env import Env

    env = Env()
    node = DefNode('x', I32(), 1)
    result = infer_def(node, env)
    assert result is None
