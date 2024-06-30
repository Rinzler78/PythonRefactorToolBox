import ast
import os
from typing import Dict, List

from .ast_helper import (
    add_ann_assign,
    add_ann_assigns,
    add_assign,
    add_assigns,
    add_class,
    add_classes,
    add_expr,
    add_exprs,
    add_function,
    add_functions,
    add_import,
    add_import_from,
    add_import_froms,
    add_imports,
    create_import_from,
    generate_code_from_tree,
    generate_code_tree_for_class,
    get_ann_assigns,
    get_assigns,
    get_classes,
    get_code_tree_required_imports,
    get_exprs,
    get_functions,
    get_import_froms,
    get_imports,
    load_code_code_tree_from_file,
    remove_class_from_code_tree,
    set_ann_assigns,
    set_assigns,
    set_classes,
    set_exprs,
    set_functions,
    set_import_froms,
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
    __code_tree: Dict[ast.stmt, List[ast.stmt]] = None

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
        code = generate_code_from_tree(self.code_tree)

        with open(self.path, "w") as file:
            file.write(code)
        return True

    @property
    def code_tree(self) -> Dict[str, List[ast.stmt]]:
        if self.__code_tree is None:
            self.__load_code_code_tree()
        return self.__code_tree

    @code_tree.setter
    def code_tree(self, new_code_tree: Dict[str, List[ast.stmt]]):
        self.__code_tree = new_code_tree

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
        remove_class_from_code_tree(class_node, self.code_tree)

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
    def import_froms(self) -> List[ast.AST]:
        return get_import_froms(self.code_tree)

    @import_froms.setter
    def import_froms(self, new_import_from: List[ast.AST]):
        set_import_froms(self.code_tree, new_import_from)

    def add_import_from(self, import_from_node: ast.ImportFrom) -> None:
        add_import_from(self.import_froms, import_from_node)

    def add_imports_from(self, import_froms: List[ast.ImportFrom]) -> None:
        add_import_froms(self.import_froms, import_froms)

    @property
    def all_imports(self):
        return self.imports + self.import_froms

    @all_imports.setter
    def all_imports(self, new_imports: List[ast.AST]):
        self.imports = [imp for imp in new_imports if isinstance(imp, ast.Import)]
        self.import_froms = [
            imp for imp in new_imports if isinstance(imp, ast.ImportFrom)
        ]

    @property
    def function_defs(self):
        return get_functions(self.code_tree)

    @function_defs.setter
    def function_defs(self, new_function_defs: List[ast.FunctionDef]):
        set_functions(self.code_tree, new_function_defs)

    def add_function_def(self, function_def_node: ast.FunctionDef) -> None:
        add_function(self.function_defs, function_def_node)

    def add_function_defs(self, function_defs: List[ast.FunctionDef]) -> None:
        add_functions(self.function_defs, function_defs)

    @property
    def assigns(self):
        return get_assigns(self.code_tree)

    @assigns.setter
    def assigns(self, new_assigns: List[ast.Assign]):
        set_assigns(self.code_tree, new_assigns)

    def add_assign(self, assign_node: ast.Assign) -> None:
        add_assign(self.assigns, assign_node)

    def add_assigns(self, assigns: List[ast.Assign]) -> None:
        add_assigns(self.assigns, assigns)

    @property
    def ann_assigns(self):
        return get_ann_assigns(self.code_tree)

    @ann_assigns.setter
    def ann_assigns(self, new_ann_assigns: List[ast.AnnAssign]):
        set_ann_assigns(self.code_tree, new_ann_assigns)

    def add_ann_assign(self, ann_assign_node: ast.AnnAssign) -> None:
        add_ann_assign(self.ann_assigns, ann_assign_node)

    def add_ann_assigns(self, ann_assigns: List[ast.AnnAssign]) -> None:
        add_ann_assigns(self.ann_assigns, ann_assigns)

    @property
    def exprs(self):
        return get_exprs(self.code_tree)

    @exprs.setter
    def exprs(self, new_exprs: List[ast.Expr]):
        set_exprs(self.code_tree, new_exprs)

    def add_expr(self, expr_node: ast.Expr) -> None:
        add_expr(self.code_tree, expr_node)

    def add_exprs(self, exprs: List[ast.Expr]) -> None:
        add_exprs(self.code_tree, exprs)

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
            class_code_tree = generate_code_tree_for_class(
                class_node, self.code_tree, module_name
            )
            source_file.code_tree = class_code_tree
            source_file.save()

            # Create the import to the class in the new module
            new_import = create_import_from(module_name, class_name)
            self.imports.insert(0, new_import)

            # Remove class form code code_tree
            self.remove_class(class_node)

            dependant_files_paths = find_class_dependent_files(module_name, self.path)

            for path in dependant_files_paths:
                update_class_imports_in_file(
                    path, class_node.name, self.module, source_file.module
                )

        self.all_imports = get_code_tree_required_imports(
            self.code_tree, self.imports + self.import_froms
        )

        self.save()

        return True
