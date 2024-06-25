import ast
import os
from typing import Dict, List, Optional, Set

import astor
import autopep8

from .snake_case import to_snake_case


def format_code(code: str) -> str:
    return autopep8.fix_code(code)


def create_import(module_name: str, class_name: str) -> ast.ImportFrom:
    return ast.ImportFrom(
        module=module_name,
        names=[ast.alias(name=class_name, asname=None)],
        level=1,
        lineno=0,
        end_lineno=0,
    )


def create_code_from_elements(elements: dict[str, list[ast.AST]]) -> str:
    all_nodes = []

    for key, ast_list in elements.items():
        all_nodes.extend(ast_list)

    module = ast.Module(body=all_nodes, type_ignores=[])

    generated_code = astor.to_source(module)

    return format_code(generated_code)


def generate_module_name(class_name: str) -> str:
    return to_snake_case(class_name)
    # return class_name.lower().capitalize()


def get_required_imports_for_class(
    class_node: ast.ClassDef, imports: List[ast.AST]
) -> List[ast.AST]:
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
    def extract_names(node: ast.AST) -> Set[str]:
        return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}

    all_names = set()

    for nodes in elements.values():
        for node in nodes:
            all_names.update(extract_names(node))

    required_imports_set = set()

    for imp in imports:
        if isinstance(imp, ast.Import):
            for alias in imp.names:
                if alias.name.split(".")[0] in all_names:
                    required_imports_set.add(imp)
                    break
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
    # Récupérer tous les nœuds dans le corps de la classe
    class_body_nodes = set(ast.walk(class_node))

    # Parcourir chaque type d'élément et supprimer les éléments relatifs à la classe
    for key in elements:
        initial_length = len(elements[key])
        elements[key][:] = [
            node for node in elements[key] if node not in class_body_nodes
        ]
        removed_count = initial_length - len(elements[key])
        if removed_count > 0:
            print(f"Removed {removed_count} elements from {key}")


def load_code_elements_from_code(code: str) -> Dict[str, List[ast.stmt]]:
    tree = ast.parse(code)
    elements: Dict[str, List[ast.stmt]] = {}

    for node in ast.walk(tree):
        if not isinstance(node, ast.stmt):
            continue

        node_type = type(node).__name__
        if node_type in elements:
            elements[node_type].append(node)
        else:
            elements[node_type] = [node]

    # Remove un need ed AnnAssign nodes
    classes = get_classes(elements)
    ann_assign_list = get_ann_assigns(elements)

    if classes and ann_assign_list:
        for cls in classes:
            for ann_assign in cls.body:
                if ann_assign in ann_assign_list:
                    ann_assign_list.remove(ann_assign)

    # Remove un need ed Assign nodes
    assign_list = get_assigns(elements)

    if classes and assign_list:
        for cls in classes:
            for assign in cls.body:
                if assign in assign_list:
                    assign_list.remove(assign)

    # Remove un need ed Return nodes
    function_def_list = get_functions(elements)
    return_list = get_returns(elements)

    if function_def_list and function_def_list:
        for func_def in function_def_list:
            for return_def in func_def.body:
                if return_def in return_list:
                    return_list.remove(return_def)

    elements = {key: value for key, value in elements.items() if elements[key]}
    return elements


def load_code_elements_from_file(file_path: str) -> Dict[str, List[ast.stmt]]:
    with open(file_path) as file:
        code = file.read()

    return load_code_elements_from_code(code)


# Class methods
def get_classes(elements: Dict[str, List[ast.stmt]]) -> List[ast.ClassDef]:
    try:
        return elements["ClassDef"]
    except KeyError:
        elements["ClassDef"] = []
        return get_classes(elements)


def set_classes(
    elements: Dict[str, List[ast.stmt]], new_classes: List[ast.ClassDef]
) -> None:
    classes = get_classes(elements)
    classes.clear()

    add_classes(classes, new_classes)


def add_class(classes: List[ast.ClassDef], new_class: ast.ClassDef) -> None:
    if new_class not in classes:
        classes.append(new_class)


def add_classes(classes: List[ast.ClassDef], new_classes: List[ast.ClassDef]) -> None:
    for cls in new_classes:
        add_class(classes, cls)


# Imports methods
def get_imports(elements: Dict[str, List[ast.stmt]]) -> List[ast.Import]:
    try:
        return elements["Import"]
    except KeyError:
        elements["Import"] = []
        return get_imports(elements)


def set_imports(elements: Dict[str, List[ast.stmt]], imports: List[ast.Import]) -> None:
    import_nodes = get_imports(elements)
    import_nodes.clear()

    add_imports(import_nodes, imports)


def add_import(imports: List[ast.Import], new_import: ast.Import) -> None:
    if new_import not in imports:
        imports.append(new_import)


def add_imports(imports: List[ast.Import], new_imports: List[ast.Import]) -> None:
    for imp in new_imports:
        add_import(imports, imp)


# Imports from methods
def get_from_imports(elements: Dict[str, List[ast.stmt]]) -> List[ast.ImportFrom]:
    try:
        return elements["ImportFrom"]
    except KeyError:
        elements["ImportFrom"] = []
        return get_from_imports(elements)


def set_from_imports(
    elements: Dict[str, List[ast.stmt]], new_imports: List[ast.ImportFrom]
) -> None:
    from_imports = get_from_imports(elements)
    from_imports.clear()

    add_from_imports(from_imports, new_imports)


def add_from_import(
    from_imports: List[ast.ImportFrom], new_from_import: ast.ImportFrom
):
    if new_from_import not in from_imports:
        from_imports.append(new_from_import)


def add_from_imports(
    from_imports: List[ast.ImportFrom], new_from_import: List[ast.ImportFrom]
) -> None:
    for imp in new_from_import:
        add_from_import(from_imports, imp)


# Ann assign methods
def get_ann_assigns(elements: Dict[str, List[ast.stmt]]) -> List[ast.AnnAssign]:
    try:
        return elements["AnnAssign"]
    except KeyError:
        elements["AnnAssign"] = []
        return get_ann_assigns(elements)


def set_ann_assigns(
    elements: Dict[str, List[ast.stmt]], new_ann_assigns: List[ast.AnnAssign]
) -> None:
    ann_assigns = get_ann_assigns(elements)
    ann_assigns.clear()

    add_ann_assigns(ann_assigns, new_ann_assigns)


def add_ann_assign(
    ann_assigns: List[ast.AnnAssign], new_ann_assign: ast.AnnAssign
) -> None:
    if new_ann_assign not in ann_assigns:
        ann_assigns.append(new_ann_assign)


def add_ann_assigns(
    ann_assigns: List[ast.AnnAssign], new_ann_assigns: List[ast.AnnAssign]
) -> None:
    for ann_assign in new_ann_assigns:
        add_ann_assign(ann_assigns, ann_assign)


# Assign methods
def get_assigns(elements: Dict[str, List[ast.stmt]]) -> List[ast.Assign]:
    try:
        return elements["Assign"]
    except KeyError:
        elements["Assign"] = []
        return get_assigns(elements)


def set_assigns(
    elements: Dict[str, List[ast.stmt]], new_assigns: List[ast.Assign]
) -> None:
    assigns = get_assigns(elements)
    assigns.clear()

    add_assign(assigns, new_assigns)


def add_assign(assigns: List[ast.Assign], new_assign: ast.Assign) -> None:
    if new_assign not in assigns:
        assigns.append(new_assign)


def add_assigns(assigns: List[ast.Assign], new_assigns: List[ast.Assign]) -> None:
    for assign in new_assigns:
        add_assign(assigns, assign)


# Functions Methods
def get_functions(elements: Dict[str, List[ast.stmt]]) -> List[ast.FunctionDef]:
    try:
        return elements["FunctionDef"]
    except KeyError:
        elements["FunctionDef"] = []
        return get_functions(elements)


def set_functions(
    elements: Dict[str, List[ast.stmt]], new_function_defs: List[ast.FunctionDef]
) -> None:
    function_defs = get_functions(elements)
    function_defs.clear()

    add_functions(function_defs, new_function_defs)


def add_function(
    functions: List[ast.FunctionDef], new_function: ast.FunctionDef
) -> None:
    if new_function not in functions:
        functions.append(new_function)


def add_functions(
    functions: List[ast.FunctionDef], new_functions: List[ast.FunctionDef]
) -> None:
    for function in new_functions:
        add_function(functions, function)


def get_returns(elements: Dict[str, List[ast.stmt]]) -> List[ast.Return]:
    try:
        return elements["Return"]
    except KeyError:
        elements["Return"] = []
        return get_returns(elements)


def set_returns(
    elements: Dict[str, List[ast.stmt]], new_returns: List[ast.Return]
) -> None:
    returns = get_returns(elements)
    returns.clear()

    add_returns(returns, new_returns)


def add_return(returns: Dict[str, List[ast.stmt]], new_return: ast.Return) -> None:
    if new_return not in returns:
        returns.append(new_return)


def add_returns(
    returns: Dict[str, List[ast.stmt]], new_returns: List[ast.Return]
) -> None:
    for return_node in new_returns:
        add_return(returns, return_node)


def get_name(node: ast.stmt) -> str:
    if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
        return node.name
    elif isinstance(node, ast.ClassDef):
        return node.name
    elif isinstance(node, ast.ImportFrom):
        return node.module if node.module is not None else ""
    elif isinstance(node, ast.Import):
        return ", ".join(alias.name for alias in node.names)
    elif isinstance(node, ast.Global) or isinstance(node, ast.Nonlocal):
        return ", ".join(node.names)
    elif isinstance(node, ast.AnnAssign):
        return node.target.id
    else:
        return ""


def compare_from_code(left_code: str, right_code: str) -> bool:
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
    with open(left_file_path) as file:
        left_code = file.read()

    with open(right_file_path) as file:
        right_code = file.read()

    if left_code == right_code:
        return True

    same = compare_from_code(left_code, right_code)

    return same


def should_delete_file(code: str) -> bool:
    code = code.strip()

    if not code:
        return True

    lines = [line for line in code.split("\n") if line.strip()]

    return all(
        line.startswith("#") or line.startswith("import") or line.startswith("from")
        for line in lines
    )


def should_delete_file_from_elements(elements: Dict[str, List[ast.stmt]]) -> bool:
    if not elements:
        return True

    imports = get_imports(elements)
    from_imports = get_from_imports(elements)

    for key in elements:
        if elements[key] != imports and elements[key] != from_imports:
            return False
    return True


def find_class_dependent_files(
    class_name: str, current_file_path: str, directory_path: Optional[str] = None
) -> List[str]:
    if directory_path is None:
        directory_path = os.path.dirname(os.path.abspath(current_file_path))

    dependent_files = []

    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)

                # Skip the current file
                if os.path.abspath(file_path) == os.path.abspath(current_file_path):
                    continue

                # Parse the file
                with open(file_path) as f:
                    try:
                        file_content = f.read()
                        tree = ast.parse(file_content, filename=file_path)
                    except Exception as e:
                        print(f"Error parsing {file_path}: {e}")
                        continue

                # Check if the class is imported or used in this file
                class_found = False

                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        for alias in node.names:
                            if alias.name == class_name:
                                dependent_files.append(file_path)
                                class_found = True
                                break
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.name.split(".")[0] == class_name:
                                dependent_files.append(file_path)
                                class_found = True
                                break
                    elif isinstance(node, ast.Name) and node.id == class_name:
                        dependent_files.append(file_path)
                        class_found = True
                        break

                if class_found:
                    continue

    return list(set(dependent_files))


def find_module_dependent_files(
    module_name: str, current_file_path: str, directory_path: Optional[str] = None
) -> List[str]:

    if directory_path is None:
        directory_path = os.path.dirname(os.path.abspath(current_file_path))

    dependent_files = []

    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)

                # Skip the current file
                if os.path.abspath(file_path) == os.path.abspath(current_file_path):
                    continue

                # Parse the file
                with open(file_path) as f:
                    try:
                        file_content = f.read()
                        tree = ast.parse(file_content, filename=file_path)
                    except Exception as e:
                        print(f"Error parsing {file_path}: {e}")
                        continue

                # Check if the module is imported in this file
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        if node.module == module_name:
                            dependent_files.append(file_path)
                            break
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.name == module_name or alias.name.startswith(
                                module_name + "."
                            ):
                                dependent_files.append(file_path)
                                break

    return list(set(dependent_files))


def update_class_imports_in_file(
    target_file_path: str,
    class_name: str,
    previous_module_name: str,
    new_module_name: str,
) -> None:
    # Analyser le fichier cible
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
    with open(target_file_path) as file:
        file_content = file.read()

    tree = ast.parse(file_content, filename=target_file_path)

    class ImportUpdater(ast.NodeTransformer):
        def visit_Import(self, node: ast.Import) -> ast.AST:
            for alias in node.names:
                if alias.name == previous_module_name or alias.name.startswith(
                    previous_module_name + "."
                ):
                    alias.name = alias.name.replace(
                        previous_module_name, new_module_name, 1
                    )
            return node

        def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.AST:
            if node.module == previous_module_name or node.module.startswith(
                previous_module_name + "."
            ):
                node.module = node.module.replace(
                    previous_module_name, new_module_name, 1
                )
            return node

    updater = ImportUpdater()
    new_tree = updater.visit(tree)

    new_code = ast.unparse(new_tree)

    with open(target_file_path, "w") as file:
        file.write(new_code)
