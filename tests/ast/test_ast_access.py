from golem.ast import FieldAccess
def test_fieldaccess_id():
    node = FieldAccess(id=1)
    assert node.id == 1


def test_fieldaccess_path():
    node = FieldAccess(path=[1, 2, 3])
    assert node.path == [1, 2, 3]


def test_fieldaccess_label():
    node = FieldAccess(label="field_label")
    assert node.label == "field_label"


def test_fieldaccess_field_name():
    node = FieldAccess(field_name="some_field")
    assert node.field_name == "some_field"


def test_fieldaccess_children():
    node = FieldAccess(id=1)
    assert node.children == ()


def test_fieldaccess_id():
    node = FieldAccess(id=1)
    assert node.id == 1


def test_fieldaccess_path():
    node = FieldAccess(id=1, path=[1, 2, 3])
    assert node.path == [1, 2, 3]


def test_fieldaccess_label():
    node = FieldAccess(id=1, label="field_label")
    assert node.label == "field_label"


def test_fieldaccess_field_name():
    node = FieldAccess(id=1, field_name="some_field")
    assert node.field_name == "some_field"


def test_fieldaccess_children():
    node = FieldAccess(id=1)
    assert node.children == ()
