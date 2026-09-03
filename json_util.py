import json

SEPARATOR = "."

def access_by_path(item: dict | list, path: list | str, sep=SEPARATOR):
    if isinstance(path, str):
        path = path.split(sep)

    traversed = []
    for leaf in path:
        try:
            item = item[leaf]
            traversed.append(leaf)
        except KeyError:
            raise KeyError(f"Invalid path: {path}.\
            Stopped at: {sep.join(traversed)}")

    return item

def set_by_path(item: dict | list, path: list | str, replace_value, sep=SEPARATOR):
    if isinstance(path, str):
        path = path.split(sep)

    traversed = []
    res = item
    for leaf in path[:-1]:
        try:
            res = res[leaf]
            traversed.append(leaf)
        except KeyError:
            raise KeyError(f"Invalid path: {path}.\
            Stopped at: {sep.join(traversed)}")
    res[path[-1]] = replace_value
