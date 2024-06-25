import ast
import os
from typing import List


def find_class_dependent_files(class_name: str, current_file_path: str) -> List[str]:
    """
    Find files that depend on a specific class.

    Args:
        class_name (str): The name of the class.
        current_file_path (str): The path to the current file.

    Returns:
        List[str]: A list of file paths that depend on the class.
    """
    directory_path = os.path.dirname(os.path.abspath(current_file_path))

    dependent_files = []

    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                if os.path.abspath(file_path) == os.path.abspath(current_file_path):
                    continue

                with open(file_path) as f:
                    try:
                        file_content = f.read()
                        tree = ast.parse(file_content, filename=file_path)
                    except Exception as e:
                        print(f"Error parsing {file_path}: {e}")
                        continue

                if any(
                    isinstance(node, (ast.ImportFrom, ast.Import))
                    and any(
                        alias.name == class_name
                        or alias.name.split(".")[0] == class_name
                        for alias in node.names
                    )
                    for node in ast.walk(tree)
                ):
                    dependent_files.append(file_path)

    return list(set(dependent_files))


def find_module_dependent_files(module_name: str, current_file_path: str) -> List[str]:
    """
    Find files that depend on a specific module.

    Args:
        module_name (str): The name of the module.
        current_file_path (str): The path to the current file.

    Returns:
        List[str]: A list of file paths that depend on the module.
    """
    directory_path = os.path.dirname(os.path.abspath(current_file_path))

    dependent_files = []

    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                if os.path.abspath(file_path) == os.path.abspath(current_file_path):
                    continue

                with open(file_path) as f:
                    try:
                        file_content = f.read()
                        tree = ast.parse(file_content, filename=file_path)
                    except Exception as e:
                        print(f"Error parsing {file_path}: {e}")
                        continue

                if any(
                    isinstance(node, ast.ImportFrom)
                    and node.module == module_name
                    or any(
                        alias.name.startswith(module_name + ".") for alias in node.names
                    )
                    for node in ast.walk(tree)
                ):
                    dependent_files.append(file_path)

    return list(set(dependent_files))
