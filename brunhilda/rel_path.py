import os

def rel_path(base_path: str, target_path: str) -> str:
    """
    Returns relative path from the base_path to the target_path.

    :param base_path: path (filename) from where the path originates
    :param target_path: path (filename) where the target is located
    """
    target_dir = os.path.dirname(target_path)
    base_dir = os.path.dirname(base_path)

    if target_dir != '':
        target_file = os.path.split(target_path)[1]
    else:
        target_file = target_path

    if target_dir == '':
        target_dir = '.'

    if base_dir == '':
        base_dir = '.'

    relative_dir = os.path.relpath(target_dir, base_dir)
    return os.path.join(relative_dir, target_file)