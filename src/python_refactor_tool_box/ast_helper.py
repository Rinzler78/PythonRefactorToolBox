import ast
from typing import Dict, List, Set, Type, TypeVar

import astor

from .code_format_helper import format_code


def create_import_from(
    module_name: str, class_name: str, level: int = 1
) -> ast.ImportFrom:
    """
    Create an ImportFrom AST node.

    Args:
        module_name (str): The name of the module to import from.
        class_name (str): The name of the class to import.

    Returns:
        ast.ImportFrom: The ImportFrom node.
    """
    return ast.ImportFrom(
        module=module_name, names=[ast.alias(name=class_name, asname=None)], level=level
    )


def create_code(code_tree: Dict[Type[ast.AST], List[ast.AST]]) -> str:
    """
    Generate code from AST code_tree.

    Args:
        code_tree (Dict[Type[ast.AST], List[ast.AST]]): A dictionary of AST code_tree.

    Returns:
        str: The generated code.
    """
    all_nodes = []
    seen_nodes = set()

    def add_to_seen_recursively(node):
        """
        Add the node and its body elements to seen_nodes recursively.
        """
        node_dump = ast.dump(node)
        if node_dump not in seen_nodes:
            seen_nodes.add(node_dump)
            if hasattr(node, "body") and isinstance(node.body, list):
                for n in node.body:
                    add_to_seen_recursively(n)

    for ast_list in code_tree.values():
        for node in ast_list:
            node_dump = ast.dump(node)
            if node_dump not in seen_nodes:
                seen_nodes.add(node_dump)
                all_nodes.append(node)
                if hasattr(node, "body") and isinstance(node.body, list):
                    for n in node.body:
                        add_to_seen_recursively(n)

    module = ast.Module(body=all_nodes, type_ignores=[])
    generated_code = astor.to_source(module)
    return format_code(generated_code)


def get_class_required_imports(
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


def get_code_tree_required_imports(
    code_tree: Dict[str, List[ast.AST]], imports: List[ast.AST]
) -> List[ast.AST]:
    """
    Determine the required imports for given code code_tree.

    Args:
        code_tree (Dict[str, List[ast.AST]]): A dictionary of code code_tree.
        imports (List[ast.AST]): A list of import nodes.

    Returns:
        List[ast.AST]: A list of required import nodes.
    """

    def extract_names(node: ast.AST) -> Set[str]:
        return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}

    all_names = {
        name
        for nodes in code_tree.values()
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


def remove_class_from_code_code_tree(
    class_node: ast.ClassDef, code_tree: Dict[ast.stmt, List[ast.stmt]]
) -> None:
    """
    Remove code_tree related to a specific class from code code_tree.

    Args:
        class_node (ast.ClassDef): The class node.
        code_tree (Dict[str, List[ast.stmt]]): A dictionary of code code_tree.
    """
    class_body_nodes = set(ast.walk(class_node))

    for key in code_tree:
        initial_length = len(code_tree[key])
        code_tree[key][:] = [
            node for node in code_tree[key] if node not in class_body_nodes
        ]
        removed_count = initial_length - len(code_tree[key])
        if removed_count > 0:
            print(f"Removed {removed_count} code_tree from {key}")


def load_code_code_tree_from_code(code: str) -> Dict[ast.stmt, List[ast.stmt]]:
    """
    Load code code_tree from a given code string.

    Args:
        code (str): The code to parse.

    Returns:
        Dict[str, List[ast.stmt]]: A dictionary of code code_tree.
    """
    tree = ast.parse(code)
    code_tree: Dict[ast.stmt, List[ast.stmt]] = {}

    for node in ast.walk(tree):
        if not isinstance(node, ast.stmt):
            continue

        code_tree.setdefault(type(node), []).append(node)

    code_tree = {key: value for key, value in code_tree.items() if code_tree[key]}
    return code_tree


def load_code_code_tree_from_file(file_path: str) -> Dict[str, List[ast.stmt]]:
    """
    Load code code_tree from a file.

    Args:
        file_path (str): The path to the file.

    Returns:
        Dict[str, List[ast.stmt]]: A dictionary of code code_tree.
    """
    with open(file_path) as file:
        code = file.read()
    return load_code_code_tree_from_code(code)


T = TypeVar("T", bound=ast.AST)


def get_elements_by_type(
    element_type: Type[T], code_tree: Dict[Type[ast.AST], List[ast.AST]]
) -> List[T]:
    """
    Retrieve elements of a specific type from the code_tree.

    Args:
        element_type (Type[T]): The type of elements to retrieve.
        code_tree (Dict[Type[ast.AST], List[ast.AST]]): A dictionary of code elements.

    Returns:
        List[T]: A list of elements of the specified type.
    """
    try:
        return code_tree[element_type]
    except KeyError:
        code_tree[element_type] = []

    return get_elements_by_type(element_type, code_tree)


def set_elements_by_type(
    element_type: Type[T],
    code_tree: Dict[Type[ast.AST], List[ast.AST]],
    new_elements: List[T],
) -> None:
    """
    Set new elements of a specific type in the code_tree.

    Args:
        element_type (Type[T]): The type of elements to update.
        code_tree (Dict[Type[ast.AST], List[ast.AST]]): A dictionary of code elements.
        new_elements (List[T]): The new elements to set.
    """
    elements = get_elements_by_type(element_type, code_tree)
    elements.clear()
    elements.extend(new_elements)


def add_element(
    element_type: Type[T], code_tree: Dict[Type[ast.AST], List[ast.AST]], new_element: T
) -> None:
    """
    Add an element to the code_tree if not already present.

    Args:
        element_type (Type[T]): The type of element to add.
        code_tree (Dict[Type[ast.AST], List[ast.AST]]): A dictionary of code elements.
        new_element (T): The new element to add.
    """
    elements = get_elements_by_type(element_type, code_tree)
    if new_element not in elements:
        elements.append(new_element)


def add_elements(
    element_type: Type[T],
    code_tree: Dict[Type[ast.AST], List[ast.AST]],
    new_elements: List[T],
) -> None:
    """
    Add multiple elements to the code_tree if not already present.

    Args:
        element_type (Type[T]): The type of elements to add.
        code_tree (Dict[Type[ast.AST], List[ast.AST]]): A dictionary of code elements.
        new_elements (List[T]): The new elements to add.
    """
    elements = get_elements_by_type(element_type, code_tree)
    for element in new_elements:
        if element not in elements:
            elements.append(element)


# Fonctions spécialisées


# Pour ast.ClassDef
def get_classes(code_tree: Dict[Type[ast.AST], List[ast.AST]]) -> List[ast.ClassDef]:
    return get_elements_by_type(ast.ClassDef, code_tree)


def set_classes(
    code_tree: Dict[Type[ast.AST], List[ast.AST]], new_classes: List[ast.ClassDef]
) -> None:
    set_elements_by_type(ast.ClassDef, code_tree, new_classes)


def add_class(
    code_tree: Dict[Type[ast.AST], List[ast.AST]], new_class: ast.ClassDef
) -> None:
    add_element(ast.ClassDef, code_tree, new_class)


def add_classes(
    code_tree: Dict[Type[ast.AST], List[ast.AST]], new_classes: List[ast.ClassDef]
) -> None:
    add_elements(ast.ClassDef, code_tree, new_classes)


# Pour ast.Import
def get_imports(code_tree: Dict[Type[ast.AST], List[ast.AST]]) -> List[ast.Import]:
    return get_elements_by_type(ast.Import, code_tree)


def set_imports(
    code_tree: Dict[Type[ast.AST], List[ast.AST]], new_imports: List[ast.Import]
) -> None:
    set_elements_by_type(ast.Import, code_tree, new_imports)


def add_import(
    code_tree: Dict[Type[ast.AST], List[ast.AST]], new_import: ast.Import
) -> None:
    add_element(ast.Import, code_tree, new_import)


def add_imports(
    code_tree: Dict[Type[ast.AST], List[ast.AST]], new_imports: List[ast.Import]
) -> None:
    add_elements(ast.Import, code_tree, new_imports)


# Pour ast.ImportFrom
def get_import_froms(
    code_tree: Dict[Type[ast.AST], List[ast.AST]]
) -> List[ast.ImportFrom]:
    return get_elements_by_type(ast.ImportFrom, code_tree)


def set_import_froms(
    code_tree: Dict[Type[ast.AST], List[ast.AST]],
    new_import_froms: List[ast.ImportFrom],
) -> None:
    set_elements_by_type(ast.ImportFrom, code_tree, new_import_froms)


def add_import_from(
    code_tree: Dict[Type[ast.AST], List[ast.AST]], new_import_from: ast.ImportFrom
) -> None:
    add_element(ast.ImportFrom, code_tree, new_import_from)


def add_import_froms(
    code_tree: Dict[Type[ast.AST], List[ast.AST]],
    new_import_froms: List[ast.ImportFrom],
) -> None:
    add_elements(ast.ImportFrom, code_tree, new_import_froms)


# Pour ast.AnnAssign
def get_ann_assigns(
    code_tree: Dict[Type[ast.AST], List[ast.AST]]
) -> List[ast.AnnAssign]:
    return get_elements_by_type(ast.AnnAssign, code_tree)


def set_ann_assigns(
    code_tree: Dict[Type[ast.AST], List[ast.AST]], new_ann_assigns: List[ast.AnnAssign]
) -> None:
    set_elements_by_type(ast.AnnAssign, code_tree, new_ann_assigns)


def add_ann_assign(
    code_tree: Dict[Type[ast.AST], List[ast.AST]], new_ann_assign: ast.AnnAssign
) -> None:
    add_element(ast.AnnAssign, code_tree, new_ann_assign)


def add_ann_assigns(
    code_tree: Dict[Type[ast.AST], List[ast.AST]], new_ann_assigns: List[ast.AnnAssign]
) -> None:
    add_elements(ast.AnnAssign, code_tree, new_ann_assigns)


# Pour ast.Assign
def get_assigns(code_tree: Dict[Type[ast.AST], List[ast.AST]]) -> List[ast.Assign]:
    return get_elements_by_type(ast.Assign, code_tree)


def set_assigns(
    code_tree: Dict[Type[ast.AST], List[ast.AST]], new_assigns: List[ast.Assign]
) -> None:
    set_elements_by_type(ast.Assign, code_tree, new_assigns)


def add_assign(
    code_tree: Dict[Type[ast.AST], List[ast.AST]], new_assign: ast.Assign
) -> None:
    add_element(ast.Assign, code_tree, new_assign)


def add_assigns(
    code_tree: Dict[Type[ast.AST], List[ast.AST]], new_assigns: List[ast.Assign]
) -> None:
    add_elements(ast.Assign, code_tree, new_assigns)


# Pour ast.FunctionDef
def get_functions(
    code_tree: Dict[Type[ast.AST], List[ast.AST]]
) -> List[ast.FunctionDef]:
    return get_elements_by_type(ast.FunctionDef, code_tree)


def set_functions(
    code_tree: Dict[Type[ast.AST], List[ast.AST]], new_functions: List[ast.FunctionDef]
) -> None:
    set_elements_by_type(ast.FunctionDef, code_tree, new_functions)


def add_function(
    code_tree: Dict[Type[ast.AST], List[ast.AST]], new_function: ast.FunctionDef
) -> None:
    add_element(ast.FunctionDef, code_tree, new_function)


def add_functions(
    code_tree: Dict[Type[ast.AST], List[ast.AST]], new_functions: List[ast.FunctionDef]
) -> None:
    add_elements(ast.FunctionDef, code_tree, new_functions)


# Pour ast.Return
def get_returns(code_tree: Dict[Type[ast.AST], List[ast.AST]]) -> List[ast.Return]:
    return get_elements_by_type(ast.Return, code_tree)


def set_returns(
    code_tree: Dict[Type[ast.AST], List[ast.AST]], new_returns: List[ast.Return]
) -> None:
    set_elements_by_type(ast.Return, code_tree, new_returns)


def add_return(
    code_tree: Dict[Type[ast.AST], List[ast.AST]], new_return: ast.Return
) -> None:
    add_element(ast.Return, code_tree, new_return)


def add_returns(
    code_tree: Dict[Type[ast.AST], List[ast.AST]], new_returns: List[ast.Return]
) -> None:
    add_elements(ast.Return, code_tree, new_returns)


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
