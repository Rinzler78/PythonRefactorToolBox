import ast
import os
from typing import Dict, List

from .ast_helper import (
    add_class,
    add_classes,
    add_from_import,
    add_from_imports,
    add_import,
    add_imports,
    create_code,
    create_from_import,
    get_class_required_imports,
    get_classes,
    get_code_tree_required_imports,
    get_from_imports,
    get_imports,
    load_code_code_tree_from_file,
    remove_class_from_code_code_tree,
    set_classes,
    set_from_imports,
    set_imports,
    update_class_imports_in_file,
    update_module_imports_in_file,
)
from .code_analyze_helper import should_delete_file_from_code_tree
from .code_compare_helper import compare_codes_from_files
from .code_format_helper import generate_module_name
from .code_search_helper import find_class_dependent_files, find_module_dependent_files


class SourceFile:
    __path: str = None
    __code_tree: Dict[str, List[ast.stmt]] = None

    def __init__(self, path):
        self.__path = path
        self.__code_tree = None

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

    @property
    def path(self) -> str:
        return self.__path

    @property
    def file_name(self) -> str:
        return os.path.basename(self.__path)

    @property
    def module(self) -> str:
        return self.file_name.split(".")[0]

    @property
    def is_exists(self) -> bool:
        return os.path.exists(self.__path)

    def __load_code_code_tree(self):
        self.__code_tree = (
            load_code_code_tree_from_file(self.path)
            if os.path.exists(self.__path)
            else {}
        )

    @property
    def should_be_deleted(self) -> bool:
        return should_delete_file_from_code_tree(self.code_tree)

    def save(self) -> bool:
        print(f"Saving file {self.path}")
        code = create_code(self.code_tree)

        with open(self.path, "w") as file:
            file.write(code)
        return True

    @property
    def code_tree(self) -> Dict[str, List[ast.stmt]]:
        if not self.__code_tree:
            self.__load_code_code_tree()
        return self.__code_tree

    @property
    def classes(self) -> List[ast.ClassDef]:
        return get_classes(self.code_tree)

    @classes.setter
    def classes(self, new_classes: List[ast.ClassDef]):
        set_classes(self.code_tree, new_classes)

    def add_class(self, class_node: ast.ClassDef) -> None:
        add_class(self.classes, class_node)

    def add_classes(self, classes: List[ast.ClassDef]) -> None:
        add_classes(self.classes, classes)

    def remove_class(self, class_node: ast.ClassDef) -> None:
        remove_class_from_code_code_tree(class_node, self.code_tree)

    def remove_classes(self, classes: List[ast.ClassDef]) -> None:
        for class_node in classes:
            self.remove_class(class_node)

    @property
    def imports(self) -> List[ast.AST]:
        return get_imports(self.code_tree)

    @imports.setter
    def imports(self, new_imports: List[ast.AST]):
        set_imports(self.code_tree, new_imports)

    def add_import(self, import_node: ast.Import) -> None:
        add_import(self.imports, import_node)

    def add_imports(self, imports: List[ast.Import]) -> None:
        add_imports(self.imports, imports)

    @property
    def from_imports(self) -> List[ast.AST]:
        return get_from_imports(self.code_tree)

    @from_imports.setter
    def from_imports(self, new_from_import: List[ast.AST]):
        set_from_imports(self.code_tree, new_from_import)

    def add_from_import(self, from_import_node: ast.ImportFrom) -> None:
        add_from_import(self.from_imports, from_import_node)

    def add_imports_from(self, from_imports: List[ast.ImportFrom]) -> None:
        add_from_imports(self.from_imports, from_imports)

    @property
    def all_imports(self):
        return self.imports + self.from_imports

    @all_imports.setter
    def all_imports(self, new_imports: List[ast.AST]):
        self.imports = [imp for imp in new_imports if isinstance(imp, ast.Import)]
        self.from_imports = [
            imp for imp in new_imports if isinstance(imp, ast.ImportFrom)
        ]

    def move_to_module(self, target_module_name: str) -> bool:
        if not self.is_exists:
            print(f"File not found : {self.path}")
            return False

        previous_module = self.module
        target_module_name = generate_module_name(previous_module)

        if previous_module == target_module_name:
            return False

        # Load existing code
        self.__load_code_code_tree()

        # Remove existing file
        os.remove(self.path)

        dependant_files_paths = find_module_dependent_files(previous_module, self.path)

        # Change path
        self.__path = self.__path.replace(
            previous_module + ".py", target_module_name + ".py"
        )

        # Save new file
        self.save()

        for path in dependant_files_paths:
            update_module_imports_in_file(path, previous_module, self.module)

        return True

    def refactor(self) -> bool:
        if not os.path.exists(self.path):
            print(f"File not found : {self.path}")
            return False

        print(f"Refactoring code in file : {self.path}")

        module_name = generate_module_name(self.module)
        self.move_to_module(module_name)

        directory = os.path.dirname(self.path)

        i = 0

        while i < len(self.classes):
            class_node = self.classes[i]

            class_name = class_node.name
            module_name = generate_module_name(class_name)
            target_file_path = os.path.join(directory, f"{module_name}.py")

            print(f"Found class {class_name} :")
            print(f"- Target module {module_name}. Target file {target_file_path}")

            source_file = SourceFile(target_file_path)

            if self.path == source_file.path:
                i += 1
                continue
            if (
                self.path != source_file.path
                and self.path.lower() == source_file.path.lower()
            ):
                i += 1
                continue

            # Create the class code
            source_file.all_imports = get_class_required_imports(
                class_node, self.imports + self.from_imports
            )
            source_file.classes = [class_node]
            source_file.save()

            # Create the import to the class in the new module
            new_import = create_from_import(module_name, class_name)
            self.imports.insert(0, new_import)

            # Remove class form code code_tree
            self.remove_class(class_node)

            dependant_files_paths = find_class_dependent_files(module_name, self.path)

            for path in dependant_files_paths:
                update_class_imports_in_file(
                    path, class_node.name, self.module, source_file.module
                )

        self.all_imports = get_code_tree_required_imports(
            self.code_tree, self.imports + self.from_imports
        )

        self.save()

        return True
