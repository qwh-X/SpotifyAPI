import json

SEPARATOR = "."

def access_by_path(item: dict | list, path: list | str, sep=SEPARATOR):
    if isinstance(path, str):
        path = path.split(sep)

    for leaf in path:
        item = item[leaf]

    return item

def set_by_path(item: dict | list, path: list | str, replace_value, sep=SEPARATOR):
    if isinstance(path, str):
        path = path.split(sep)

    res = item
    for leaf in path[:-1]:
        res = res[leaf]
    res[path[-1]] = replace_value
