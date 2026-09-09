from knot.path import Path

def generate_path(path_type, *parts):
    """Generate a Path object from a path type and variable path parts.

    Args:
        path_type: The type of path (e.g., 1, 2, 3)
        *parts: Variable path parts to append to the path

    Returns:
        Path: A Path object with the specified type and path
    """
    return Path(path_type, *parts)
