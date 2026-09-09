from knot.checker import type_error
def test_type_error_creation():
    err = type_error("Type mismatch", (1, 2, 3))
    assert err.message == "Type mismatch"
    assert err.path == (1, 2, 3)
    assert isinstance(err, TypeErrorVal)


def test_type_error_repr():
    err = type_error("Type mismatch", (1, 2, 3))
    assert repr(err) == "TypeErrorVal(message='Type mismatch', path=(1, 2, 3))"


def test_type_error_str():
    err = type_error("Type mismatch", (1, 2, 3))
    assert str(err) == "Type mismatch"


def test_type_error_path_tuple():
    err = type_error("Type mismatch", (1, 2, 3))
    assert isinstance(err.path, tuple)
    assert err.path == (1, 2, 3)


def test_type_error_message_str():
    err = type_error("Type mismatch", (1, 2, 3))
    assert isinstance(err.message, str)
    assert err.message == "Type mismatch"


def test_type_error_instance_type():
    err = type_error("Type mismatch", (1, 2, 3))
    assert isinstance(err, TypeErrorVal)


def test_type_error_creation_with_empty_path():
    err = type_error("Type mismatch", ())
    assert err.message == "Type mismatch"
    assert err.path == ()
    assert isinstance(err, TypeErrorVal)


def test_type_error_repr_empty_path():
    err = type_error("Type mismatch", ())
    assert repr(err) == "TypeErrorVal(message='Type mismatch', path=())"

def test_type_error_str_empty_path():
    err = type_error("Type mismatch", ())
    assert str(err) == "Type mismatch"

def test_type_error_path_tuple_empty():
    err = type_error("Type mismatch", ())
    assert isinstance(err.path, tuple)
    assert err.path == ()

def test_type_error_message_str_empty():
    err = type_error("Type mismatch", ())
    assert isinstance(err.message, str)
    assert err.message == "Type mismatch"

def test_type_error_instance_type_empty():
    err = type_error("Type mismatch", ())
    assert isinstance(err, TypeErrorVal)


def test_type_error_creation():
    err = type_error("Type mismatch", (1, 2, 3))
    assert err.message == "Type mismatch"
    assert err.path == (1, 2, 3)
    assert isinstance(err, TypeErrorVal)


def test_type_error_repr():
    err = type_error("Type mismatch", (1, 2, 3))
    assert repr(err) == "TypeErrorVal(message='Type mismatch', path=(1, 2, 3))"

def test_type_error_str():
    err = type_error("Type mismatch", (1, 2, 3))
    assert str(err) == "Type mismatch"

def test_type_error_path_tuple():
    err = type_error("Type mismatch", (1, 2, 3))
    assert isinstance(err.path, tuple)
    assert err.path == (1, 2, 3)

def test_type_error_message_str():
    err = type_error("Type mismatch", (1, 2, 3))
    assert isinstance(err.message, str)
    assert err.message == "Type mismatch"

def test_type_error_instance_type():
    err = type_error("Type mismatch", (1, 2, 3))
    assert isinstance(err, TypeErrorVal)
