import ast
import os
from typing import Dict, List, Set

import astor
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


def create_import(module_name: str, class_name: str) -> ast.ImportFrom:
    """
    Create an ImportFrom AST node.

    Args:
        module_name (str): The name of the module to import from.
        class_name (str): The name of the class to import.

    Returns:
        ast.ImportFrom: The ImportFrom node.
    """
    return ast.ImportFrom(
        module=module_name, names=[ast.alias(name=class_name, asname=None)], level=1
    )


def create_code_from_elements(elements: Dict[str, List[ast.AST]]) -> str:
    """
    Generate code from AST elements.

    Args:
        elements (Dict[str, List[ast.AST]]): A dictionary of AST elements.

    Returns:
        str: The generated code.
    """
    all_nodes = [node for ast_list in elements.values() for node in ast_list]
    module = ast.Module(body=all_nodes, type_ignores=[])
    generated_code = astor.to_source(module)
    return format_code(generated_code)


def generate_module_name(class_name: str) -> str:
    """
    Generate a module name from a class name using snake case.

    Args:
        class_name (str): The class name.

    Returns:
        str: The module name in snake case.
    """
    return to_snake_case(class_name)


def get_required_imports_for_class(
    class_node: ast.ClassDef, imports: List[ast.AST]
) -> List[ast.AST]:
    """
    Determine the required imports for a given class.

    Args:
        class_node (ast.ClassDef): The class node.
        imports (List[ast.AST]): A list of import nodes.

    Returns:
        List[ast.AST]: A list of required import nodes.
    """
    required_imports = []
    class_names = {
        node.id for node in ast.walk(class_node) if isinstance(node, ast.Name)
    }

    for imp in imports:
        if isinstance(imp, ast.Import):
            for alias in imp.names:
                if alias.name.split(".")[0] in class_names:
                    required_imports.append(imp)
        elif isinstance(imp, ast.ImportFrom):
            if imp.module and any(alias.name in class_names for alias in imp.names):
                required_imports.append(imp)

    import_modules = [
        imp.module if isinstance(imp, ast.ImportFrom) else alias.name
        for imp in required_imports
        for alias in (imp.names if isinstance(imp, ast.Import) else [imp])
    ]

    print(f"class {class_node.name} requires imports: {', '.join(import_modules)}")
    return required_imports


def get_required_imports_for_code_elements(
    elements: Dict[str, List[ast.AST]], imports: List[ast.AST]
) -> List[ast.AST]:
    """
    Determine the required imports for given code elements.

    Args:
        elements (Dict[str, List[ast.AST]]): A dictionary of code elements.
        imports (List[ast.AST]): A list of import nodes.

    Returns:
        List[ast.AST]: A list of required import nodes.
    """

    def extract_names(node: ast.AST) -> Set[str]:
        return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}

    all_names = {
        name
        for nodes in elements.values()
        for node in nodes
        for name in extract_names(node)
    }
    required_imports_set = set()

    for imp in imports:
        if isinstance(imp, ast.Import):
            if any(alias.name.split(".")[0] in all_names for alias in imp.names):
                required_imports_set.add(imp)
        elif isinstance(imp, ast.ImportFrom):
            if imp.module and any(alias.name in all_names for alias in imp.names):
                required_imports_set.add(imp)

    required_imports = list(required_imports_set)

    import_modules = [
        imp.module if isinstance(imp, ast.ImportFrom) else alias.name
        for imp in required_imports
        for alias in (imp.names if isinstance(imp, ast.Import) else [imp])
    ]

    print(f"Required imports: {', '.join(import_modules)}")

    return required_imports


def remove_class_from_code_elements(
    class_node: ast.ClassDef, elements: Dict[str, List[ast.stmt]]
) -> None:
    """
    Remove elements related to a specific class from code elements.

    Args:
        class_node (ast.ClassDef): The class node.
        elements (Dict[str, List[ast.stmt]]): A dictionary of code elements.
    """
    class_body_nodes = set(ast.walk(class_node))

    for key in elements:
        initial_length = len(elements[key])
        elements[key][:] = [
            node for node in elements[key] if node not in class_body_nodes
        ]
        removed_count = initial_length - len(elements[key])
        if removed_count > 0:
            print(f"Removed {removed_count} elements from {key}")


def load_code_elements_from_code(code: str) -> Dict[str, List[ast.stmt]]:
    """
    Load code elements from a given code string.

    Args:
        code (str): The code to parse.

    Returns:
        Dict[str, List[ast.stmt]]: A dictionary of code elements.
    """
    tree = ast.parse(code)
    elements: Dict[str, List[ast.stmt]] = {}

    for node in ast.walk(tree):
        if not isinstance(node, ast.stmt):
            continue

        node_type = type(node).__name__
        elements.setdefault(node_type, []).append(node)

    # Remove unnecessary AnnAssign nodes
    classes = get_classes(elements)
    ann_assign_list = get_ann_assigns(elements)

    if classes and ann_assign_list:
        for cls in classes:
            for ann_assign in cls.body:
                if ann_assign in ann_assign_list:
                    ann_assign_list.remove(ann_assign)

    # Remove unnecessary Assign nodes
    assign_list = get_assigns(elements)

    if classes and assign_list:
        for cls in classes:
            for assign in cls.body:
                if assign in assign_list:
                    assign_list.remove(assign)

    # Remove unnecessary Return nodes
    function_def_list = get_functions(elements)
    return_list = get_returns(elements)

    if function_def_list and return_list:
        for func_def in function_def_list:
            for return_def in func_def.body:
                if return_def in return_list:
                    return_list.remove(return_def)

    elements = {key: value for key, value in elements.items() if elements[key]}
    return elements


def load_code_elements_from_file(file_path: str) -> Dict[str, List[ast.stmt]]:
    """
    Load code elements from a file.

    Args:
        file_path (str): The path to the file.

    Returns:
        Dict[str, List[ast.stmt]]: A dictionary of code elements.
    """
    with open(file_path) as file:
        code = file.read()
    return load_code_elements_from_code(code)


# Class methods
def get_classes(elements: Dict[str, List[ast.stmt]]) -> List[ast.ClassDef]:
    """
    Retrieve class definitions from elements.

    Args:
        elements (Dict[str, List[ast.stmt]]): A dictionary of code elements.

    Returns:
        List[ast.ClassDef]: A list of class definitions.
    """
    return elements.get("ClassDef", [])


def set_classes(
    elements: Dict[str, List[ast.stmt]], new_classes: List[ast.ClassDef]
) -> None:
    """
    Set new class definitions in the elements.

    Args:
        elements (Dict[str, List[ast.stmt]]): A dictionary of code elements.
        new_classes (List[ast.ClassDef]): The new class definitions.
    """
    classes = get_classes(elements)
    classes.clear()
    add_classes(classes, new_classes)


def add_class(classes: List[ast.ClassDef], new_class: ast.ClassDef) -> None:
    """
    Add a class definition to the list if not already present.

    Args:
        classes (List[ast.ClassDef]): The list of class definitions.
        new_class (ast.ClassDef): The new class definition.
    """
    if new_class not in classes:
        classes.append(new_class)


def add_classes(classes: List[ast.ClassDef], new_classes: List[ast.ClassDef]) -> None:
    """
    Add multiple class definitions to the list if not already present.

    Args:
        classes (List[ast.ClassDef]): The list of class definitions.
        new_classes (List[ast.ClassDef]): The new class definitions.
    """
    for cls in new_classes:
        add_class(classes, cls)


# Imports methods
def get_imports(elements: Dict[str, List[ast.stmt]]) -> List[ast.Import]:
    """
    Retrieve import statements from elements.

    Args:
        elements (Dict[str, List[ast.stmt]]): A dictionary of code elements.

    Returns:
        List[ast.Import]: A list of import statements.
    """
    return elements.get("Import", [])


def set_imports(elements: Dict[str, List[ast.stmt]], imports: List[ast.Import]) -> None:
    """
    Set new import statements in the elements.

    Args:
        elements (Dict[str, List[ast.stmt]]): A dictionary of code elements.
        imports (List[ast.Import]): The new import statements.
    """
    import_nodes = get_imports(elements)
    import_nodes.clear()
    add_imports(import_nodes, imports)


def add_import(imports: List[ast.Import], new_import: ast.Import) -> None:
    """
    Add an import statement to the list if not already present.

    Args:
        imports (List[ast.Import]): The list of import statements.
        new_import (ast.Import): The new import statement.
    """
    if new_import not in imports:
        imports.append(new_import)


def add_imports(imports: List[ast.Import], new_imports: List[ast.Import]) -> None:
    """
    Add multiple import statements to the list if not already present.

    Args:
        imports (List[ast.Import]): The list of import statements.
        new_imports (List[ast.Import]): The new import statements.
    """
    for imp in new_imports:
        add_import(imports, imp)


# Imports from methods
def get_from_imports(elements: Dict[str, List[ast.stmt]]) -> List[ast.ImportFrom]:
    """
    Retrieve import-from statements from elements.

    Args:
        elements (Dict[str, List[ast.stmt]]): A dictionary of code elements.

    Returns:
        List[ast.ImportFrom]: A list of import-from statements.
    """
    return elements.get("ImportFrom", [])


def set_from_imports(
    elements: Dict[str, List[ast.stmt]], new_imports: List[ast.ImportFrom]
) -> None:
    """
    Set new import-from statements in the elements.

    Args:
        elements (Dict[str, List[ast.stmt]]): A dictionary of code elements.
        new_imports (List[ast.ImportFrom]): The new import-from statements.
    """
    from_imports = get_from_imports(elements)
    from_imports.clear()
    add_from_imports(from_imports, new_imports)


def add_from_import(
    from_imports: List[ast.ImportFrom], new_from_import: ast.ImportFrom
) -> None:
    """
    Add an import-from statement to the list if not already present.

    Args:
        from_imports (List[ast.ImportFrom]): The list of import-from statements.
        new_from_import (ast.ImportFrom): The new import-from statement.
    """
    if new_from_import not in from_imports:
        from_imports.append(new_from_import)


def add_from_imports(
    from_imports: List[ast.ImportFrom], new_from_import: List[ast.ImportFrom]
) -> None:
    """
    Add multiple import-from statements to the list if not already present.

    Args:
        from_imports (List[ast.ImportFrom]): The list of import-from statements.
        new_from_import (List[ast.ImportFrom]): The new import-from statements.
    """
    for imp in new_from_import:
        add_from_import(from_imports, imp)


# Ann assign methods
def get_ann_assigns(elements: Dict[str, List[ast.stmt]]) -> List[ast.AnnAssign]:
    """
    Retrieve annotated assignment statements from elements.

    Args:
        elements (Dict[str, List[ast.stmt]]): A dictionary of code elements.

    Returns:
        List[ast.AnnAssign]: A list of annotated assignment statements.
    """
    return elements.get("AnnAssign", [])


def set_ann_assigns(
    elements: Dict[str, List[ast.stmt]], new_ann_assigns: List[ast.AnnAssign]
) -> None:
    """
    Set new annotated assignment statements in the elements.

    Args:
        elements (Dict[str, List[ast.stmt]]): A dictionary of code elements.
        new_ann_assigns (List[ast.AnnAssign]): The new annotated assignment statements.
    """
    ann_assigns = get_ann_assigns(elements)
    ann_assigns.clear()
    add_ann_assigns(ann_assigns, new_ann_assigns)


def add_ann_assign(
    ann_assigns: List[ast.AnnAssign], new_ann_assign: ast.AnnAssign
) -> None:
    """
    Add an annotated assignment statement to the list if not already present.

    Args:
        ann_assigns (List[ast.AnnAssign]): The list of annotated assignment statements.
        new_ann_assign (ast.AnnAssign): The new annotated assignment statement.
    """
    if new_ann_assign not in ann_assigns:
        ann_assigns.append(new_ann_assign)


def add_ann_assigns(
    ann_assigns: List[ast.AnnAssign], new_ann_assigns: List[ast.AnnAssign]
) -> None:
    """
    Add multiple annotated assignment statements to the list if not already present.

    Args:
        ann_assigns (List[ast.AnnAssign]): The list of annotated assignment statements.
        new_ann_assigns (List[ast.AnnAssign]): The new annotated assignment statements.
    """
    for ann_assign in new_ann_assigns:
        add_ann_assign(ann_assigns, ann_assign)


# Assign methods
def get_assigns(elements: Dict[str, List[ast.stmt]]) -> List[ast.Assign]:
    """
    Retrieve assignment statements from elements.

    Args:
        elements (Dict[str, List[ast.stmt]]): A dictionary of code elements.

    Returns:
        List[ast.Assign]: A list of assignment statements.
    """
    return elements.get("Assign", [])


def set_assigns(
    elements: Dict[str, List[ast.stmt]], new_assigns: List[ast.Assign]
) -> None:
    """
    Set new assignment statements in the elements.

    Args:
        elements (Dict[str, List[ast.stmt]]): A dictionary of code elements.
        new_assigns (List[ast.Assign]): The new assignment statements.
    """
    assigns = get_assigns(elements)
    assigns.clear()
    add_assigns(assigns, new_assigns)


def add_assign(assigns: List[ast.Assign], new_assign: ast.Assign) -> None:
    """
    Add an assignment statement to the list if not already present.

    Args:
        assigns (List[ast.Assign]): The list of assignment statements.
        new_assign (ast.Assign): The new assignment statement.
    """
    if new_assign not in assigns:
        assigns.append(new_assign)


def add_assigns(assigns: List[ast.Assign], new_assigns: List[ast.Assign]) -> None:
    """
    Add multiple assignment statements to the list if not already present.

    Args:
        assigns (List[ast.Assign]): The list of assignment statements.
        new_assigns (List[ast.Assign]): The new assignment statements.
    """
    for assign in new_assigns:
        add_assign(assigns, assign)


# Functions Methods
def get_functions(elements: Dict[str, List[ast.stmt]]) -> List[ast.FunctionDef]:
    """
    Retrieve function definitions from elements.

    Args:
        elements (Dict[str, List[ast.stmt]]): A dictionary of code elements.

    Returns:
        List[ast.FunctionDef]: A list of function definitions.
    """
    return elements.get("FunctionDef", [])


def set_functions(
    elements: Dict[str, List[ast.stmt]], new_function_defs: List[ast.FunctionDef]
) -> None:
    """
    Set new function definitions in the elements.

    Args:
        elements (Dict[str, List[ast.stmt]]): A dictionary of code elements.
        new_function_defs (List[ast.FunctionDef]): The new function definitions.
    """
    function_defs = get_functions(elements)
    function_defs.clear()
    add_functions(function_defs, new_function_defs)


def add_function(
    functions: List[ast.FunctionDef], new_function: ast.FunctionDef
) -> None:
    """
    Add a function definition to the list if not already present.

    Args:
        functions (List[ast.FunctionDef]): The list of function definitions.
        new_function (ast.FunctionDef): The new function definition.
    """
    if new_function not in functions:
        functions.append(new_function)


def add_functions(
    functions: List[ast.FunctionDef], new_functions: List[ast.FunctionDef]
) -> None:
    """
    Add multiple function definitions to the list if not already present.

    Args:
        functions (List[ast.FunctionDef]): The list of function definitions.
        new_functions (List[ast.FunctionDef]): The new function definitions.
    """
    for function in new_functions:
        add_function(functions, function)


def get_returns(elements: Dict[str, List[ast.stmt]]) -> List[ast.Return]:
    """
    Retrieve return statements from elements.

    Args:
        elements (Dict[str, List[ast.stmt]]): A dictionary of code elements.

    Returns:
        List[ast.Return]: A list of return statements.
    """
    return elements.get("Return", [])


def set_returns(
    elements: Dict[str, List[ast.stmt]], new_returns: List[ast.Return]
) -> None:
    """
    Set new return statements in the elements.

    Args:
        elements (Dict[str, List[ast.stmt]]): A dictionary of code elements.
        new_returns (List[ast.Return]): The new return statements.
    """
    returns = get_returns(elements)
    returns.clear()
    add_returns(returns, new_returns)


def add_return(returns: Dict[str, List[ast.stmt]], new_return: ast.Return) -> None:
    """
    Add a return statement to the list if not already present.

    Args:
        returns (Dict[str, List[ast.stmt]]): The list of return statements.
        new_return (ast.Return): The new return statement.
    """
    if new_return not in returns:
        returns.append(new_return)


def add_returns(
    returns: Dict[str, List[ast.stmt]], new_returns: List[ast.Return]
) -> None:
    """
    Add multiple return statements to the list if not already present.

    Args:
        returns (Dict[str, List[ast.stmt]]): The list of return statements.
        new_returns (List[ast.Return]): The new return statements.
    """
    for return_node in new_returns:
        add_return(returns, return_node)


def get_name(node: ast.stmt) -> str:
    """
    Get the name of a node.

    Args:
        node (ast.stmt): The node.

    Returns:
        str: The name of the node.
    """
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return node.name
    elif isinstance(node, (ast.ImportFrom, ast.Import)):
        return ", ".join(alias.name for alias in node.names)
    elif isinstance(node, (ast.Global, ast.Nonlocal)):
        return ", ".join(node.names)
    elif isinstance(node, ast.AnnAssign):
        return node.target.id
    return ""


def compare_from_code(left_code: str, right_code: str) -> bool:
    """
    Compare two pieces of code to determine if they are equivalent.

    Args:
        left_code (str): The first piece of code.
        right_code (str): The second piece of code.

    Returns:
        bool: True if the codes are equivalent, False otherwise.
    """
    left_elements = load_code_elements_from_code(left_code)
    right_elements = load_code_elements_from_code(right_code)

    if len(left_elements) != len(right_elements):
        return False

    for type_name in left_elements:
        if type_name not in right_elements:
            return False
        if len(left_elements[type_name]) != len(right_elements[type_name]):
            return False
        if sorted(ast.dump(node) for node in left_elements[type_name]) != sorted(
            ast.dump(node) for node in right_elements[type_name]
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

    lines = [line for line in code.split("\n") if line.strip()]
    return all(
        line.startswith("#") or line.startswith("import") or line.startswith("from")
        for line in lines
    )


def should_delete_file_from_elements(elements: Dict[str, List[ast.stmt]]) -> bool:
    """
    Determine if a file should be deleted based on its elements.

    Args:
        elements (Dict[str, List[ast.stmt]]): A dictionary of code elements.

    Returns:
        bool: True if the file should be deleted, False otherwise.
    """
    if not elements:
        return True

    imports = get_imports(elements)
    from_imports = get_from_imports(elements)

    for key in elements:
        if elements[key] != imports and elements[key] != from_imports:
            return False

    return True


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


def update_class_imports_in_file(
    target_file_path: str,
    class_name: str,
    previous_module_name: str,
    new_module_name: str,
) -> None:
    """
    Update class imports in a target file.

    Args:
        target_file_path (str): The path to the target file.
        class_name (str): The class name.
        previous_module_name (str): The previous module name.
        new_module_name (str): The new module name.
    """
    with open(target_file_path) as file:
        file_content = file.read()

    tree = ast.parse(file_content, filename=target_file_path)

    class ImportUpdater(ast.NodeTransformer):
        def visit_Import(self, node: ast.Import) -> ast.AST:
            for alias in node.names:
                if alias.name == previous_module_name:
                    alias.name = new_module_name
            return node

        def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.AST:
            if node.module == previous_module_name:
                for alias in node.names:
                    if alias.name == class_name:
                        node.module = new_module_name
            return node

    updater = ImportUpdater()
    new_tree = updater.visit(tree)
    new_code = ast.unparse(new_tree)

    with open(target_file_path, "w") as file:
        file.write(new_code)


def update_module_imports_in_file(
    target_file_path: str, previous_module_name: str, new_module_name: str
) -> None:
    """
    Update module imports in a target file.

    Args:
        target_file_path (str): The path to the target file.
        previous_module_name (str): The previous module name.
        new_module_name (str): The new module name.
    """
    with open(target_file_path) as file:
        file_content = file.read()

    tree = ast.parse(file_content, filename=target_file_path)

    class ImportUpdater(ast.NodeTransformer):
        def visit_Import(self, node: ast.Import) -> ast.AST:
            for alias in node.names:
                if alias.name.startswith(previous_module_name):
                    alias.name = alias.name.replace(
                        previous_module_name, new_module_name, 1
                    )
            return node

        def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.AST:
            if node.module and node.module.startswith(previous_module_name):
                node.module = node.module.replace(
                    previous_module_name, new_module_name, 1
                )
            return node

    updater = ImportUpdater()
    new_tree = updater.visit(tree)
    new_code = ast.unparse(new_tree)

    with open(target_file_path, "w") as file:
        file.write(new_code)
