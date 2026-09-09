from typing import Union

def generate_path(path: Union[str, tuple]) -> tuple:
    if isinstance(path, str):
        return tuple(segment for segment in path.strip('/').split('/') if segment)
    elif isinstance(path, tuple):
        return tuple(path)
    else:
        raise TypeError(f"Unsupported path type: {type(path)}")

if __name__ == "__main__":
    print(generate_path("a/b/c"))
    print(generate_path(("a", "b", "c")))
