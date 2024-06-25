import autopep8

from .snake_case import to_snake_case


def format_code(code: str) -> str:
    """
    Format the given code string using autopep8.

    Args:
        code (str): The code to format.

    Returns:
        str: The formatted code.
    """
    return autopep8.fix_code(code)


def generate_module_name(class_name: str) -> str:
    """
    Generate a module name from a class name using snake case.

    Args:
        class_name (str): The class name.

    Returns:
        str: The module name in snake case.
    """
    return to_snake_case(class_name)
