import ast
import os
from typing import List, Tuple


def extract_classes_and_imports(
    filepath: str,
) -> Tuple[List[ast.ClassDef], List[ast.AST]]:
    with open(filepath) as file:
        tree = ast.parse(file.read())

    classes: List[ast.ClassDef] = []
    imports: List[ast.AST] = []

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            classes.append(node)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            imports.append(node)

    classes = sorted(classes, key=lambda x: x.name)
    imports = sorted(imports, key=lambda x: x.module)

    return classes, imports


def generate_class_code(class_node: ast.ClassDef, imports: List[ast.AST]) -> str:
    remove_unused_imports(ast.unparse(class_node), imports)
    imports_code = "".join(ast.unparse(imp) + "\n" for imp in imports)
    class_code = ast.unparse(class_node) + "\n"
    return imports_code + class_code


def get_class_dependencies(filepath: str, class_name: str) -> List[str]:
    with open(filepath) as file:
        tree = ast.parse(file.read())

    dependencies: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == class_name:
            dependencies.append(filepath)
            break

    return dependencies


def update_imports(filepath: str, old_class_name: str, new_module_name: str) -> None:
    with open(filepath) as file:
        tree = ast.parse(file.read())

    for node in tree.body:
        for alias in node.names:
            if (
                isinstance(node, ast.ImportFrom)
                and alias.name == old_class_name
                or not isinstance(node, ast.ImportFrom)
                and isinstance(node, ast.Import)
                and alias.name == old_class_name
            ):
                alias.name = new_module_name
    updated_code = ast.unparse(tree)

    with open(filepath, "w") as file:
        file.write(updated_code)


def is_code_dependent_on_class(code: str, class_name: str) -> bool:
    tree = ast.parse(code)
    return any(
        isinstance(node, ast.Name) and node.id == class_name for node in ast.walk(tree)
    )


def remove_unused_imports(code: str, imports: List[ast.AST]) -> None:
    tree = ast.parse(code)
    used_imports = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            used_imports.add(node.id)
        elif isinstance(node, ast.Attribute):
            used_imports.add(node.attr)

    new_imports = []
    for imp in imports:
        for alias in imp.names:
            if (
                isinstance(imp, ast.Import)
                and alias.name in used_imports
                or not isinstance(imp, ast.Import)
                and isinstance(imp, ast.ImportFrom)
                and alias.name in used_imports
            ):
                new_imports.append(imp)
                break
    imports.clear()
    imports.extend(iter(new_imports))


def remove_class_from_code(
    filepath: str,
    class_node: ast.ClassDef,
    class_name: str,
    new_module_name: str,
    imports: List[ast.AST],
) -> None:
    with open(filepath) as file:
        lines = file.readlines()

    class_start = class_node.lineno - 1
    class_end = class_node.end_lineno

    remaining_code = lines[:class_start] + lines[class_end:]
    remaining_code_str = "".join(remaining_code)

    if is_code_dependent_on_class(remaining_code_str, class_name):
        import_statement = f"from .{new_module_name} import {class_name}\n"
        remaining_code = [import_statement] + remaining_code
        imports.append(
            ast.parse(import_statement).body[0]
        )  # Add the import to the imports list

    remove_unused_imports(remaining_code_str, imports)

    remaining_code = [
        line
        for line in remaining_code
        if not line.startswith("from") and not line.startswith("import")
    ]

    for imp in imports:
        import_line = ast.unparse(imp) + "\n"
        if import_line not in remaining_code:
            remaining_code = [import_line] + remaining_code

    with open(filepath, "w") as file:
        file.writelines(remaining_code)


def move_class_to_file(filepath: str) -> None:
    classes, imports = extract_classes_and_imports(filepath)
    if not classes:
        return

    base_dir = os.path.dirname(filepath)

    for class_node in classes:
        class_name = class_node.name
        # class_filename = f"{to_snake_case(class_name)}.py"
        class_filename = f"{class_name}.py"
        class_filepath = os.path.join(base_dir, class_filename)

        if class_filepath != filepath and class_filepath == filepath.lower():
            new_filepath = os.path.join(base_dir, class_filename)
            os.rename(filepath, new_filepath)
            move_class_to_file(new_filepath)
            return

        if class_filepath == filepath:
            continue

        class_code = generate_class_code(class_node, imports)

        with open(class_filepath, "w") as file:
            file.write(class_code)

        remove_class_from_code(
            filepath, class_node, class_name, class_filename.replace(".py", ""), imports
        )

        for dep_file in os.listdir(base_dir):
            dep_filepath = os.path.join(base_dir, dep_file)
            if (
                dep_filepath != filepath
                and dep_filepath.endswith(".py")
                and get_class_dependencies(dep_filepath, class_name)
            ):
                update_imports(
                    dep_filepath, class_name, class_filename.replace(".py", "")
                )


def compare_sources_files(left_file_path: str, right_file_path: str) -> bool:
    left_classes, left_imports = extract_classes_and_imports(left_file_path)
    right_classes, right_imports = extract_classes_and_imports(right_file_path)

    if len(left_classes) != len(right_classes) or len(left_imports) != len(
        right_imports
    ):
        return False

    for i in range(len(left_classes)):
        left_class = left_classes[i]
        right_class = right_classes[i]

        if left_class.name != right_class.name:
            return False

        left_class_code = generate_class_code(left_class, left_imports)
        right_class_code = generate_class_code(right_class, right_imports)

        if left_class_code != right_class_code:
            return False

    for i in range(len(left_imports)):
        left_import = left_imports[i]
        right_import = right_imports[i]

        if ast.unparse(left_import) != ast.unparse(right_import):
            return False

    return True


def compare_classes(left_class: ast.ClassDef, right_class: ast.ClassDef) -> bool:
    if not left_class or not right_class or left_class.name != right_class.name:
        return False

    if (
        left_class.bases is None
        or right_class.bases is None
        or len(left_class.bases) != len(right_class.bases)
    ):
        return False

    for left, right in zip(left_class.bases, right_class.bases):
        if ast.dump(left) != ast.dump(right):
            return False

    if (
        left_class.keywords is None
        or right_class.keywords is None
        or len(left_class.keywords) != len(right_class.keywords)
    ):
        return False

    for keyword1, keyword2 in zip(left_class.keywords, right_class.keywords):
        if keyword1.arg != keyword2.arg or ast.dump(keyword1.value) != ast.dump(
            keyword2.value
        ):
            return False

    if (
        left_class.body is None
        or right_class.body is None
        or len(left_class.body) != len(right_class.body)
    ):
        return False

    for left, right in zip(left_class.body, right_class.body):
        if ast.dump(left) != ast.dump(right):
            return False

    if (
        left_class.decorator_list is None
        or right_class.decorator_list is None
        or len(left_class.decorator_list) != len(right_class.decorator_list)
    ):
        return False

    return all(
        ast.dump(left) == ast.dump(right)
        for left, right in zip(left_class.decorator_list, right_class.decorator_list)
    )


def compare_imports(node1, node2):
    if not isinstance(node1, type(node2)):
        return False

    for field in node1._fields:
        if field == "ctx":
            continue
        value1 = getattr(node1, field)
        value2 = getattr(node2, field)

        if isinstance(value1, list):
            if len(value1) != len(value2):
                return False
            for item1, item2 in zip(value1, value2):
                if not compare_imports(item1, item2):
                    return False
        elif isinstance(value1, ast.AST):
            if not compare_imports(value1, value2):
                return False
        elif value1 != value2:
            return False

    return True
