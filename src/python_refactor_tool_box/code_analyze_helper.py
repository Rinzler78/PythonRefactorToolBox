import ast
from typing import Dict, List

from .ast_helper import get_from_imports, get_imports


def should_delete_file(code: str) -> bool:
    """
    Determine if a file should be deleted based on its content.

    Args:
        code (str): The code to check.

    Returns:
        bool: True if the file should be deleted, False otherwise.
    """
    code = code.strip()

    if not code:
        return True

    lines = [line.strip() for line in code.split("\n")]
    return all(
        line.startswith("#") or line.startswith("import") or line.startswith("from")
        for line in lines
        if line
    )


def should_delete_file_from_code_tree(code_tree: Dict[str, List[ast.stmt]]) -> bool:
    """
    Determine if a file should be deleted based on its code_tree.

    Args:
        code_tree (Dict[str, List[ast.stmt]]): A dictionary of code code_tree.

    Returns:
        bool: True if the file should be deleted, False otherwise.
    """
    if not code_tree:
        return True

    imports = get_imports(code_tree)
    from_imports = get_from_imports(code_tree)

    for key in code_tree:
        if code_tree[key] != imports and code_tree[key] != from_imports:
            return False

    return True
