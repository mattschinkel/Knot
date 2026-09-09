from knot.ast import Program, Node

def print_ast(node):
    if isinstance(node, Program):
        return f"Program({node.body})"
    elif isinstance(node, Node):
        return f"Node(id={node.id}, path={node.path}, label={node.label})"
    else:
        return f"Unknown({node})"
