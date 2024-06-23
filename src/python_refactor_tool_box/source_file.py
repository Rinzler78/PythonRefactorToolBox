import ast
import os

from .python_refactor_helper import (
    compare_codes_from_files,
    create_class_code,
    create_code_from_elements,
    create_import,
    generate_module_name,
    get_classes_list,
    get_import_from_list,
    get_import_list,
    get_required_imports_for_class,
    get_required_imports_for_code_elements,
    load_code_elements_from_file,
    remove_class_from_code_elements,
    save_new_module,
    should_delete_file,
)


class SourceFile:
    __path: str = None

    def __init__(self, path):
        self.__path = path

    def __eq__(self, other):
        if not (other and isinstance(other, SourceFile)):
            return False
        if other.file_name != self.file_name:
            return False

        return compare_codes_from_files(self.__path, other.__path)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.__path

    def __repr__(self):
        return self.__path

    def load_code(self, code: str):
        self.code = code

    @property
    def path(self) -> str:
        return self.__path

    @property
    def file_name(self) -> str:
        return os.path.basename(self.__path)

    def refactor(self) -> bool:
        if not os.path.exists(self.path):
            print(f"File not found : {self.path}")
            return False

        directory = os.path.dirname(self.path)
        print(f"Refactoring code in file : {self.path}")

        # Extract elements from code
        elements = load_code_elements_from_file(self.path)
        classes = get_classes_list(elements)
        imports_list = get_import_list(elements)
        import_from_list = get_import_from_list(elements)

        i = 0

        while i < len(classes):
            class_node = classes[i]

            class_name = class_node.name
            module_name = generate_module_name(class_name)
            target_file_path = os.path.join(directory, f"{module_name}.py")

            print(f"Found class {class_name} :")
            print(f"- Target module {module_name}. Target file {target_file_path}")

            if self.path == target_file_path:
                i += 1
                continue
            if (
                self.path != target_file_path
                and self.path.lower() == target_file_path.lower()
            ):
                i += 1
                os.remove(self.path)
                self.__path = target_file_path
                continue

            # Create the class code
            required_imports = get_required_imports_for_class(
                class_node, imports_list + import_from_list
            )
            class_code = create_class_code(class_node, required_imports)

            # Save the class in the target module
            save_new_module(self.path, target_file_path, class_code)

            # Create the import to the class in the new module
            new_import = create_import(module_name, class_name)
            imports_list.insert(0, new_import)

            # Remove class form code elements
            remove_class_from_code_elements(class_node, elements)

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

        if should_delete_file(new_code):
            os.remove(self.path)
        else:
            with open(self.path, "w") as file:
                file.write(new_code)

        return True
