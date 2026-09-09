from knot.ast import IfExpr
def test_ifexpr_path():
    node = IfExpr(1, None, None)
    assert node.path == [1]


def test_ifexpr_children():
    then_branch = ExprNode(2, None, None)
    else_branch = ExprNode(3, None, None)
    node = IfExpr(1, then_branch, else_branch)
    assert node.children == (then_branch, else_branch)


from knot.ast import IfExpr, ExprNode

def test_ifexpr_id():
    node = IfExpr(1, None, None)
    assert node.id == 1

def test_ifexpr_path():
    node = IfExpr(1, None, None)
    assert node.path == [1]

def test_ifexpr_children():
    then_branch = ExprNode(2, None, None)
    else_branch = ExprNode(3, None, None)
    node = IfExpr(1, then_branch, else_branch)
    assert node.children == (then_branch, else_branch)


from knot.ast import IfExpr, ExprNode

def test_ifexpr_id():
    node = IfExpr(1, None, None)
    assert node.id == 1

def test_ifexpr_path():
    node = IfExpr(1, None, None)
    assert node.path == [1]

def test_ifexpr_children():
    then_branch = ExprNode(2, None, None)
    else_branch = ExprNode(3, None, None)
    node = IfExpr(1, then_branch, else_branch)
    assert node.children == (then_branch, else_branch)


from knot.ast import IfExpr, ExprNode

def test_ifexpr_id():
    node = IfExpr(1, None, None)
    assert node.id == 1

def test_ifexpr_path():
    node = IfExpr(1, None, None)
    assert node.path == [1]

def test_ifexpr_children():
    then_branch = ExprNode(2, None, None)
    else_branch = ExprNode(3, None, None)
    node = IfExpr(1, then_branch, else_branch)
    assert node.children == (then_branch, else_branch)


def test_ifexpr_then_branch():
    node = IfExpr(1, None, None)
    assert node.then_branch is None


def test_ifexpr_path():
    node = IfExpr(1, None, None)
    assert node.path == []
