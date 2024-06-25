import ast

from .ast_helper import load_code_code_tree_from_code


def compare_from_code(left_code: str, right_code: str) -> bool:
    """
    Compare two pieces of code to determine if they are equivalent.

    Args:
        left_code (str): The first piece of code.
        right_code (str): The second piece of code.

    Returns:
        bool: True if the codes are equivalent, False otherwise.
    """
    left_code_tree = load_code_code_tree_from_code(left_code)
    right_code_tree = load_code_code_tree_from_code(right_code)

    if len(left_code_tree) != len(right_code_tree):
        return False

    for type_name in left_code_tree:
        if type_name not in right_code_tree:
            return False
        if len(left_code_tree[type_name]) != len(right_code_tree[type_name]):
            return False
        if sorted(ast.dump(node) for node in left_code_tree[type_name]) != sorted(
            ast.dump(node) for node in right_code_tree[type_name]
        ):
            return False

    return True


def compare_codes_from_files(left_file_path: str, right_file_path: str) -> bool:
    """
    Compare two files to determine if they are equivalent.

    Args:
        left_file_path (str): The path to the first file.
        right_file_path (str): The path to the second file.

    Returns:
        bool: True if the files are equivalent, False otherwise.
    """
    with open(left_file_path) as left_file, open(right_file_path) as right_file:
        left_code = left_file.read()
        right_code = right_file.read()

    return left_code == right_code or compare_from_code(left_code, right_code)
