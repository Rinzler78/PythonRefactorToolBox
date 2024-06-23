import ast
import os
from typing import Dict, List, Set

import astor
import autopep8


def refactor_file(path: str) -> bool:
    if not os.path.exists(path):
        print(f"File not found : {path}")
        return False

    print(f"Refactoring code from file : {path}")
    with open(path) as file:
        code = file.read()

    refactored_code = refactor_code(code, path)

    if should_delete_file(refactored_code):
        os.remove(path)
    else:
        with open(path, "w") as file:
            file.write(refactored_code)

    return True


def refactor_code(code: str, current_file_path: str) -> str:
    # Extract elements from code
    elements = extract_code_elements(code)
    classes = get_classes_list(elements)
    imports_list = get_import_list(elements)
    import_from_list = get_import_from_list(elements)
    directory = os.path.dirname(current_file_path)

    i = 0

    while i < len(classes):
        class_node = classes[i]

        class_name = class_node.name
        module_name = generate_module_name(class_name)
        target_file_path = os.path.join(directory, f"{module_name}.py")

        print(f"Found class {class_name} :")
        print(f"- Target module {module_name}. Target file {target_file_path}")

        if current_file_path != target_file_path:
            # Create the class code
            required_imports = get_required_imports_for_class(
                class_node, imports_list + import_from_list
            )
            class_code = create_class_code(class_node, required_imports)

            # Save the class in the target module
            save_new_module(current_file_path, target_file_path, class_code)

            # Create the import to the class in the new module
            new_import = create_import(module_name, class_name)
            imports_list.insert(0, new_import)

            # Remove class form code elements
            remove_class_from_code_elements(class_node, elements)
        else:
            i += 1

    required_imports = get_required_imports_for_code_elements(
        elements, imports_list + import_from_list
    )
    imports_list.clear()
    import_from_list.clear()

    for imp in required_imports:
        if isinstance(imp, ast.Import):
            imports_list.append(imp)
        elif isinstance(imp, ast.ImportFrom):
            import_from_list.append(imp)

    new_code = create_code_from_elements(elements)

    return new_code


def format_code(code: str) -> str:
    return autopep8.fix_code(code)


def save_new_module(current_file_path: str, target_file_path: str, class_code: str):
    if (
        current_file_path.lower() == target_file_path.lower()
        and current_file_path != target_file_path
    ):
        print(f"Remove {current_file_path}")
        os.remove(current_file_path)

    print(f"Create {target_file_path}")

    with open(target_file_path, "w") as file:
        file.write(class_code)


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
    return class_name.lower().capitalize()


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


def create_class_code(class_node, required_imports: List[ast.AST]) -> str:
    import_code = "\n".join(ast.unparse(node).strip() for node in required_imports)
    class_code = ast.unparse(class_node).strip()
    return format_code(f"{import_code}\n\n{class_code}")


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


def extract_code_elements(code: str) -> Dict[str, List[ast.stmt]]:
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
    classes = get_classes_list(elements)
    ann_assign_list = get_ann_assign_list(elements)

    if classes and ann_assign_list:
        for cls in classes:
            for ann_assign in cls.body:
                if ann_assign in ann_assign_list:
                    ann_assign_list.remove(ann_assign)

    # Remove un need ed Assign nodes
    assign_list = get_assign_list(elements)

    if classes and assign_list:
        for cls in classes:
            for assign in cls.body:
                if assign in assign_list:
                    assign_list.remove(assign)

    # Remove un need ed Return nodes
    function_def_list = get_function_def_list(elements)
    return_list = get_return_list(elements)

    if function_def_list and function_def_list:
        for func_def in function_def_list:
            for return_def in func_def.body:
                if return_def in return_list:
                    return_list.remove(return_def)

    return elements


def get_classes_list(elements: Dict[str, List[ast.stmt]]) -> List[ast.ClassDef]:
    try:
        return elements["ClassDef"]
    except KeyError:
        elements["ClassDef"] = []
        return get_classes_list(elements)


def get_import_list(elements: Dict[str, List[ast.stmt]]) -> List[ast.AST]:
    try:
        return elements["Import"]
    except KeyError:
        elements["Import"] = []
        return get_import_list(elements)


def get_import_from_list(elements: Dict[str, List[ast.stmt]]) -> List[ast.AST]:
    try:
        return elements["ImportFrom"]
    except KeyError:
        elements["ImportFrom"] = []
        return get_import_from_list(elements)


def get_ann_assign_list(elements: Dict[str, List[ast.stmt]]) -> List[ast.AST]:
    try:
        return elements["AnnAssign"]
    except KeyError:
        elements["AnnAssign"] = []
        return get_ann_assign_list(elements)


def get_assign_list(elements: Dict[str, List[ast.stmt]]) -> List[ast.Assign]:
    try:
        return elements["Assign"]
    except KeyError:
        elements["Assign"] = []
        return get_assign_list(elements)


def get_function_def_list(elements: Dict[str, List[ast.stmt]]) -> List[ast.FunctionDef]:
    try:
        return elements["FunctionDef"]
    except KeyError:
        elements["FunctionDef"] = []
        return get_function_def_list(elements)


def get_return_list(elements: Dict[str, List[ast.stmt]]) -> List[ast.Return]:
    try:
        return elements["Return"]
    except KeyError:
        elements["Return"] = []
        return get_return_list(elements)


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
    left_elements = extract_code_elements(left_code)
    right_elements = extract_code_elements(right_code)

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
