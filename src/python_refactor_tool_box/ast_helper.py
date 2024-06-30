import ast
from typing import Dict, List, Set, Type, TypeVar

import astor

from .code_format_helper import format_code

T = TypeVar("T", bound=ast.AST)

nodes_with_body = []
nodes_with_final_body = []
nodes_with_handlers = []
nodes_with_orelse = []


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


def clean_code_tree(
    code_tree: Dict[Type[ast.AST], List[ast.AST]]
) -> Dict[Type[ast.AST], List[ast.AST]]:
    """
    Clean the code tree by removing duplicate nodes.

    Args:
        code_tree (Dict[Type[ast.AST], List[ast.AST]]): A dictionary of AST code_tree.

    Returns:
        Dict[Type[ast.AST], List[ast.AST]]: A cleaned dictionary of AST code_tree.
    """
    seen_nodes = {}
    new_code_tree = {key: [] for key in code_tree}

    def add_to_seen_recursively(node):
        """
        Add the node and its body elements to seen_nodes recursively.
        """

        node_id = id(node)
        if node_id in seen_nodes:
            return

        seen_nodes[node_id] = node

        sub_nodes: list = []

        if isinstance(node, tuple(nodes_with_body)) and isinstance(node.body, list):
            sub_nodes.extend(node.body)

        elif hasattr(node, "body") and isinstance(node.body, list):
            nodes_with_body.append(type(node))
            print(f"Adding {type(node).__name__} to nodes_with_body")
            sub_nodes.extend(node.body)

        if isinstance(node, tuple(nodes_with_handlers)) and isinstance(
            node.handlers, list
        ):
            sub_nodes.extend(node.handlers)

        elif hasattr(node, "handlers") and isinstance(node.handlers, list):
            nodes_with_handlers.append(type(node))
            print(f"Adding {type(node).__name__} to nodes_with_handlers")
            sub_nodes.extend(node.handlers)

        if isinstance(node, tuple(nodes_with_final_body)) and isinstance(
            node.finalbody, list
        ):
            sub_nodes.extend(node.finalbody)

        elif hasattr(node, "finalbody") and isinstance(node.finalbody, list):
            nodes_with_final_body.append(type(node))
            print(f"Adding {type(node).__name__} to nodes_with_final_body")
            sub_nodes.extend(node.finalbody)

        if isinstance(node, tuple(nodes_with_orelse)) and isinstance(node.orelse, list):
            sub_nodes.extend(node.orelse)

        elif hasattr(node, "orelse") and isinstance(node.orelse, list):
            nodes_with_orelse.append(type(node))
            print(f"Adding {type(node).__name__} to nodes_with_orelse")
            sub_nodes.extend(node.orelse)

        if sub_nodes:
            for n in sub_nodes:
                add_to_seen_recursively(n)

    def add_nodes_to_new_tree(node_type: Type[ast.AST]):
        """
        Add nodes of specified types to new_code_tree and mark them as seen.
        """
        if node_type in code_tree:
            for node in code_tree[node_type]:
                node_id = id(node)
                if node_id not in seen_nodes:
                    new_code_tree[node_type].append(node)
                    add_to_seen_recursively(node)

    for node_type in code_tree:
        add_nodes_to_new_tree(node_type)

    new_code_tree = {key: value for key, value in new_code_tree.items() if value}
    return new_code_tree


def generate_code_from_tree(code_tree: Dict[Type[ast.AST], List[ast.AST]]) -> str:
    """
    Generate code from a cleaned AST code_tree.

    Args:
        code_tree (Dict[Type[ast.AST], List[ast.AST]]): A code_tree dictionary.

    Returns:
        str: The generated code.
    """
    code_nodes = []

    prior_types = [ast.Import, ast.ImportFrom, ast.ClassDef]
    remaining_types = [t for t in code_tree.keys() if t not in prior_types]

    def add_nodes_from_types(node_types):
        """
        Add nodes of specified types to code_nodes.
        """
        for node_type in node_types:
            if node_type in code_tree:
                for node in code_tree[node_type]:
                    code_nodes.append(node)

    # Process nodes in prior_types first
    add_nodes_from_types(prior_types)

    # Process nodes in remaining_types
    add_nodes_from_types(remaining_types)

    module = ast.Module(body=code_nodes, type_ignores=[])
    generated_code = astor.to_source(module)
    return format_code(generated_code)


def generate_code_tree_for_class(
    class_node: ast.ClassDef,
    code_tree: Dict[Type[ast.AST], List[ast.AST]],
    target_module_name: str,
) -> Dict[Type[ast.AST], List[ast.AST]]:
    """
    Create a code tree containing the class and the necessary imports
    for its usage, pointing to the target module.

    Args:
        class_node (ast.ClassDef): The class node.
        code_tree (Dict[Type[ast.AST], List[ast.AST]]): The original code tree.
        target_module_name (str): The name of the target module.

    Returns:
        Dict[Type[ast.AST], List[ast.AST]]: A new code tree.
    """
    new_code_tree = {ast.Import: [], ast.ImportFrom: [], ast.ClassDef: [class_node]}

    # Add required imports
    new_code_tree[ast.Import].extend(
        get_class_required_imports(class_node, get_imports(code_tree))
    )
    new_code_tree[ast.ImportFrom].extend(
        get_class_required_import_froms(class_node, get_import_froms(code_tree))
    )

    # Determine necessary elements used in the class
    required_functions = get_class_required_functions(
        class_node, get_functions(code_tree)
    )
    required_assigns = get_class_required_assigns(class_node, get_assigns(code_tree))
    required_ann_assigns = get_class_required_ann_assigns(
        class_node, get_ann_assigns(code_tree)
    )

    # Add imports for the necessary elements
    def add_imports_for_elements(elements, element_type):
        for elem in elements:
            if element_type == ast.FunctionDef:
                new_code_tree[ast.ImportFrom].append(
                    create_import_from(target_module_name, elem.name)
                )
            elif element_type in {ast.Assign, ast.AnnAssign}:
                targets = elem.targets if element_type == ast.Assign else [elem.target]
                for target in targets:
                    if isinstance(target, ast.Name):
                        new_code_tree[ast.ImportFrom].append(
                            create_import_from(target_module_name, target.id)
                        )

    add_imports_for_elements(required_functions, ast.FunctionDef)
    add_imports_for_elements(required_assigns, ast.Assign)
    add_imports_for_elements(required_ann_assigns, ast.AnnAssign)

    # Clean up new_code_tree by removing empty lists
    new_code_tree = {key: value for key, value in new_code_tree.items() if value}

    return clean_code_tree(new_code_tree)


def get_required_imports_for_elements(
    code_tree: Dict[Type[ast.AST], List[ast.AST]], elements: List[ast.AST]
) -> List[ast.AST]:
    """
    Determine the required imports for a given list of elements

    Args:
        code_tree (Dict[Type[ast.AST], List[ast.AST]]): The original code tree.
        elements (List[ast.AST]): A list of nodes.

    Returns:
        List[ast.AST]: A list of required import nodes.
    """
    required_imports = []
    element_names = {
        node.id
        for elem in elements
        for node in ast.walk(elem)
        if isinstance(node, ast.Name)
    }

    imports = get_imports(code_tree)
    import_froms = get_import_froms(code_tree)

    import_modules = set()
    for imp in imports:
        for alias in imp.names:
            import_modules.add(alias.name.split(".")[0])

    for imp in import_froms:
        if imp.module:
            import_modules.add(imp.module.split(".")[0])
            import_modules.update(alias.name for alias in imp.names)

    for name in element_names:
        if name in import_modules:
            for imp in imports:
                for alias in imp.names:
                    if alias.name.split(".")[0] == name:
                        required_imports.append(imp)
                        break
            for imp in import_froms:
                if imp.module and (
                    imp.module.split(".")[0] == name
                    or any(alias.name == name for alias in imp.names)
                ):
                    required_imports.append(imp)
                    break

    return required_imports


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

    return required_imports


def get_class_required_import_froms(
    class_node: ast.ClassDef, import_froms: List[ast.ImportFrom]
) -> List[ast.ImportFrom]:
    """
    Determine the required import-froms for a given class.

    Args:
        class_node (ast.ClassDef): The class node.
        import_froms (List[ast.ImportFrom]): A list of import-from nodes.

    Returns:
        List[ast.ImportFrom]: A list of required import-from nodes.
    """
    required_import_froms = []
    class_names = {
        node.id for node in ast.walk(class_node) if isinstance(node, ast.Name)
    }

    for imp in import_froms:
        if imp.module and any(alias.name in class_names for alias in imp.names):
            required_import_froms.append(imp)

    return required_import_froms


def get_class_required_functions(
    class_node: ast.ClassDef, functions: List[ast.FunctionDef]
) -> List[ast.FunctionDef]:
    """
    Determine the required functions for a given class.

    Args:
        class_node (ast.ClassDef): The class node.
        functions (List[ast.FunctionDef]): A list of function nodes.

    Returns:
        List[ast.FunctionDef]: A list of required function nodes.
    """
    required_functions = []
    class_names = {
        node.id for node in ast.walk(class_node) if isinstance(node, ast.Name)
    }

    for func in functions:
        if func.name in class_names:
            required_functions.append(func)

    return required_functions


def get_class_required_assigns(
    class_node: ast.ClassDef, assigns: List[ast.Assign]
) -> List[ast.Assign]:
    """
    Determine the required assignments for a given class.

    Args:
        class_node (ast.ClassDef): The class node.
        assigns (List[ast.Assign]): A list of assignment nodes.

    Returns:
        List[ast.Assign]: A list of required assignment nodes.
    """
    required_assigns = []
    class_names = {
        node.id for node in ast.walk(class_node) if isinstance(node, ast.Name)
    }

    for assign in assigns:
        if any(
            isinstance(target, ast.Name) and target.id in class_names
            for target in assign.targets
        ):
            required_assigns.append(assign)

    return required_assigns


def get_class_required_ann_assigns(
    class_node: ast.ClassDef, ann_assigns: List[ast.AnnAssign]
) -> List[ast.AnnAssign]:
    """
    Determine the required annotated assignments for a given class.

    Args:
        class_node (ast.ClassDef): The class node.
        ann_assigns (List[ast.AnnAssign]): A list of annotated assignment nodes.

    Returns:
        List[ast.AnnAssign]: A list of required annotated assignment nodes.
    """
    required_ann_assigns = []
    class_names = {
        node.id for node in ast.walk(class_node) if isinstance(node, ast.Name)
    }

    for ann_assign in ann_assigns:
        if (
            isinstance(ann_assign.target, ast.Name)
            and ann_assign.target.id in class_names
        ):
            required_ann_assigns.append(ann_assign)

    return required_ann_assigns


def get_class_required_exprs(
    class_node: ast.ClassDef, exprs: List[ast.Expr]
) -> List[ast.Expr]:
    """
    Determine the required expressions for a given class.

    Args:
        class_node (ast.ClassDef): The class node.
        exprs (List[ast.Expr]): A list of expression nodes.

    Returns:
        List[ast.Expr]: A list of required expression nodes.
    """
    required_exprs = []
    class_names = {
        node.id for node in ast.walk(class_node) if isinstance(node, ast.Name)
    }

    for expr in exprs:
        if any(
            isinstance(arg, ast.Name) and arg.id in class_names
            for arg in ast.walk(expr)
        ):
            required_exprs.append(expr)

    return required_exprs


def get_class_dependencies(
    class_node: ast.ClassDef, code_tree: Dict[Type[ast.AST], List[ast.AST]]
) -> Dict[Type[ast.AST], List[ast.AST]]:
    """
    Get all required dependencies for a given class node.

    Args:
        class_node (ast.ClassDef): The class node.
        code_tree (Dict[Type[ast.AST], List[ast.AST]]): The original code tree.

    Returns:
        Dict[Type[ast.AST], List[ast.AST]]: A new code tree.
    """
    new_code_tree = {key: [] for key in code_tree}

    new_code_tree[ast.Import] = get_class_required_imports(
        class_node, get_imports(code_tree)
    )
    new_code_tree[ast.ImportFrom] = get_class_required_import_froms(
        class_node, get_import_froms(code_tree)
    )
    new_code_tree[ast.FunctionDef] = get_class_required_functions(
        class_node, get_functions(code_tree)
    )
    new_code_tree[ast.Assign] = get_class_required_assigns(
        class_node, get_assigns(code_tree)
    )
    new_code_tree[ast.AnnAssign] = get_class_required_ann_assigns(
        class_node, get_ann_assigns(code_tree)
    )
    new_code_tree[ast.Expr] = get_class_required_exprs(class_node, get_exprs(code_tree))

    return {key: value for key, value in new_code_tree.items() if value}


def get_required_imports_for_functions(
    code_tree: Dict[Type[ast.AST], List[ast.AST]], functions: List[ast.FunctionDef]
) -> List[ast.AST]:
    """
    Determine the required imports for a given list of functions.

    Args:
        code_tree (Dict[Type[ast.AST], List[ast.AST]]): The original code tree.
        functions (List[ast.FunctionDef]): A list of function nodes.

    Returns:
        List[ast.AST]: A list of required import nodes.
    """
    required_imports = []
    function_names = {
        node.id
        for func in functions
        for node in ast.walk(func)
        if isinstance(node, ast.Name)
    }

    imports = get_imports(code_tree)
    import_froms = get_import_froms(code_tree)

    import_modules = set()
    for imp in imports:
        for alias in imp.names:
            import_modules.add(alias.name.split(".")[0])

    for imp in import_froms:
        if imp.module:
            import_modules.add(imp.module.split(".")[0])
            import_modules.update(alias.name for alias in imp.names)

    for name in function_names:
        if name in import_modules:
            for imp in imports:
                for alias in imp.names:
                    if alias.name.split(".")[0] == name:
                        required_imports.append(imp)
                        break
            for imp in import_froms:
                if imp.module and (
                    imp.module.split(".")[0] == name
                    or any(alias.name == name for alias in imp.names)
                ):
                    required_imports.append(imp)
                    break

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


def remove_class_from_code_tree(
    class_node: ast.ClassDef, code_tree: Dict[Type[ast.AST], List[ast.AST]]
) -> None:
    """
    Remove code_tree related to a specific class from code code_tree.

    Args:
        class_node (ast.ClassDef): The class node.
        code_tree (Dict[Type[ast.AST], List[ast.AST]]): A dictionary of code code_tree.
    """

    def remove_nodes(
        nodes_to_remove: set, code_tree: Dict[Type[ast.AST], List[ast.AST]]
    ) -> None:
        elements_to_remove = {}
        for key in list(code_tree.keys()):
            elements_to_remove[key] = [
                node for node in code_tree[key] if node in nodes_to_remove
            ]
            for node in elements_to_remove[key]:
                nodes_to_remove.remove(node)

        for key, elements in elements_to_remove.items():
            initial_length = len(code_tree[key])
            code_tree[key][:] = [
                node for node in code_tree[key] if node not in elements
            ]
            removed_count = initial_length - len(code_tree[key])
            if removed_count > 0:
                print(f"Removed {removed_count} nodes from {key.__name__}")

    # Get all nodes within the class node, including nested body elements
    nodes_to_remove = set(ast.walk(class_node))

    # Remove class node itself
    nodes_to_remove.add(class_node)

    # Remove nodes from the code tree
    remove_nodes(nodes_to_remove, code_tree)


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

    # Clean code tree to prevent from duplicate nodes
    code_tree = clean_code_tree(code_tree)

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


# For ast.ClassDef
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


# For ast.Import
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


# For ast.ImportFrom
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


# For ast.AnnAssign
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


# For ast.Assign
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


# For ast.FunctionDef
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


# For ast.Return
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


# For ast.Expr
def add_returns(
    code_tree: Dict[Type[ast.AST], List[ast.AST]], new_returns: List[ast.Return]
) -> None:
    add_elements(ast.Return, code_tree, new_returns)


def get_exprs(code_tree: Dict[Type[ast.AST], List[ast.AST]]) -> List[ast.Expr]:
    return get_elements_by_type(ast.Expr, code_tree)


def set_exprs(
    code_tree: Dict[Type[ast.AST], List[ast.AST]], new_exprs: List[ast.Expr]
) -> None:
    set_elements_by_type(ast.Expr, code_tree, new_exprs)


def add_expr(code_tree: Dict[Type[ast.AST], List[ast.AST]], new_expr: ast.Expr) -> None:
    add_element(ast.Expr, code_tree, new_expr)


def add_exprs(
    code_tree: Dict[Type[ast.AST], List[ast.AST]], new_exprs: List[ast.Expr]
) -> None:
    add_elements(ast.Expr, code_tree, new_exprs)


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
    elif isinstance(node, ast.Expr):
        return node.value.n
    elif isinstance(node, ast.Assign):
        return ", ".join([get_name(trgt) for trgt in node.targets])
    elif isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Attribute):
        return node.attr
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
