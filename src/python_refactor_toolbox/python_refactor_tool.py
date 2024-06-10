import ast
import os


def extract_classes_and_imports(filepath):
    with open(filepath) as file:
        tree = ast.parse(file.read())

    classes = []
    imports = []

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            classes.append(node)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            imports.append(node)

    classes = sorted(classes, key=lambda x: x.name)
    imports = sorted(imports, key=lambda x: x.module)

    return classes, imports


def generate_class_code(class_node, imports):
    remove_unused_imports(ast.unparse(class_node), imports)
    imports_code = "".join(ast.unparse(imp) + "\n" for imp in imports)
    class_code = ast.unparse(class_node) + "\n"
    return imports_code + class_code


def get_class_dependencies(filepath, class_name):
    with open(filepath) as file:
        tree = ast.parse(file.read())

    dependencies = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == class_name:
            dependencies.append(filepath)
            break

    return dependencies


def update_imports(filepath, old_class_name, new_module_name):
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


def is_code_dependent_on_class(code, class_name):
    tree = ast.parse(code)
    return any(
        isinstance(node, ast.Name) and node.id == class_name for node in ast.walk(tree)
    )


def remove_unused_imports(code, imports):
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
    for imp in new_imports:
        imports.append(imp)


def remove_class_from_code(filepath, class_node, class_name, new_module_name, imports):
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


def move_class_to_file(filepath):
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


def move_class_to_file_from_directory(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                move_class_to_file(os.path.join(root, file))


def compare_sources_files(left_file_path: str, right_file_path: str):
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


def compare_sources_directories(left_directory: str, right_directory: str) -> bool:
    for root, _, files in os.walk(left_directory):
        for file in files:
            left_file_path = os.path.join(root, file)
            right_file_path = os.path.join(right_directory, file)

            if not compare_sources_files(left_file_path, right_file_path):
                return False

    return True
