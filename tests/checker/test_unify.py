def test_unify_reflexive():
    from knot.types import unify
    assert unify(1, 1) == 1

def test_unify_option_reflexive():
    from knot.types import unify
    assert unify(1, 1) == 1

def test_unify_list_reflexive():
    from knot.types import unify
    assert unify([1], [1]) == [1]

def test_unify_tuple_reflexive():
    from knot.types import unify
    assert unify((1, 2), (1, 2)) == (1, 2)

def test_unify_map_reflexive():
    from knot.types import unify
    assert unify({1: 2}, {1: 2}) == {1: 2}

def test_unify_nominal_reflexive():
    from knot.types import unify
    assert unify("a", "a") == "a"

def test_unify_base_type():
    from knot.types import unify
    assert unify("i32", "i32") == "i32"


def test_unify_option_type():
    from knot.types import unify
    assert unify(1, 1) == 1

def test_unify_list_type():
    from knot.types import unify
    assert unify([1], [1]) == [1]

def test_unify_tuple_type():
    from knot.types import unify
    assert unify((1, 2), (1, 2)) == (1, 2)

def test_unify_map_type():
    from knot.types import unify
    assert unify({1: 2}, {1: 2}) == {1: 2}

def test_unify_nominal_type():
    from knot.types import unify
    assert unify("a", "a") == "a"

def test_unify_base_type():
    from knot.types import unify
    assert unify("i32", "i32") == "i32"


def test_unify_different_types():
    from knot.types import unify
    assert unify(1, [1]) is None

def test_unify_different_tuple():
    from knot.types import unify
    assert unify((1, 2), (1, 3)) is None

def test_unify_different_map():
    from knot.types import unify
    assert unify({1: 2}, {1: 3}) is None

def test_unify_different_option():
    from knot.types import unify
    assert unify([1], [2]) is None

def test_unify_different_list():
    from knot.types import unify
    assert unify([1], [2]) is None

def test_unify_different_nominal():
    from knot.types import unify
    assert unify("a", "b") is None

def test_unify_different_base_type():
    from knot.types import unify
    assert unify("i32", "f32") is None

def test_unify_never():
    from knot.types import unify
    assert unify("never", "never") == "never"


def test_unify_list_different_content():
    from knot.types import unify
    assert unify([1, 2], [1, 3]) is None

def test_unify_tuple_different_content():
    from knot.types import unify
    assert unify((1, 2), (1, 3)) is None

def test_unify_map_different_value():
    from knot.types import unify
    assert unify({1: 2}, {1: 3}) is None

def test_unify_map_different_key():
    from knot.types import unify
    assert unify({1: 2}, {2: 3}) is None

def test_unify_map_different_structure():
    from knot.types import unify
    assert unify({1: 2}, {1: 2, 3: 4}) is None

def test_unify_option_different_content():
    from knot.types import unify
    assert unify([1], [2]) is None

def test_unify_nominal_different():
    from knot.types import unify
    assert unify("a", "b") is None

def test_unify_base_type_different():
    from knot.types import unify
    assert unify("i32", "f32") is None


def test_unify_list_with_none():
    from knot.types import unify
    assert unify([1], None) is None

def test_unify_tuple_with_none():
    from knot.types import unify
    assert unify((1, 2), None) is None

def test_unify_map_with_none():
    from knot.types import unify
    assert unify({1: 2}, None) is None

def test_unify_option_with_none():
    from knot.types import unify
    assert unify([1], None) is None

def test_unify_nominal_with_none():
    from knot.types import unify
    assert unify("a", None) is None

def test_unify_base_type_with_none():
    from knot.types import unify
    assert unify("i32", None) is None

def test_unify_none_with_none():
    from knot.types import unify
    assert unify(None, None) is None

def test_unify_none_with_other():
    from knot.types import unify
    assert unify(None, 1) is None


def test_unify_list_with_different_list():
    from knot.types import unify
    assert unify([1], [1, 2]) is None

def test_unify_tuple_with_different_tuple():
    from knot.types import unify
    assert unify((1, 2), (1, 2, 3)) is None

def test_unify_map_with_different_map():
    from knot.types import unify
    assert unify({1: 2}, {1: 2, 3: 4}) is None

def test_unify_option_with_different_option():
    from knot.types import unify
    assert unify([1], [2]) is None

def test_unify_nominal_with_different_nominal():
    from knot.types import unify
    assert unify("a", "b") is None

def test_unify_base_type_with_different_base_type():
    from knot.types import unify
    assert unify("i32", "f32") is None

def test_unify_list_with_empty():
    from knot.types import unify
    assert unify([1], []) is None

def test_unify_tuple_with_empty():
    from knot.types import unify
    assert unify((1, 2), ()) is None

def test_unify_map_with_empty():
    from knot.types import unify
    assert unify({1: 2}, {}) is None

def test_unify_option_with_empty():
    from knot.types import unify
    assert unify([1], []) is None
