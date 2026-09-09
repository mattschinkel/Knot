import json

from knot.values import Value


def serialize(value: Value, path: tuple) -> str:
    return json.dumps({
        'id': value.id,
        'path': list(path),
        'label': value.label,
        'children': []
    })

# Example usage
# serialize(IntVal(1), (1, 2, 3))
# '{"id": 1, "path": [1, 2, 3], "label": null, "children": []}'
