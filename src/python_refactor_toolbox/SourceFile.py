import ast
from typing import List

from .python_refactor_helper import (
    compare_classes,
    compare_imports,
    extract_classes_and_imports,
    move_class_to_file,
)


class SourceFile:
    __path: str = None
    __classes: List[ast.ClassDef] = None
    __imports: List[ast.AST] = None

    def __init__(self, path):
        self.__path = path
        self.load()

    def __eq__(self, other):
        if not (other and isinstance(other, SourceFile)):
            return False

        if not (
            (self.classes and other.classes and len(self.classes) == len(other.classes))
            and (
                self.imports
                and other.imports
                and len(self.imports) == len(other.imports)
            )
        ):
            return False

        return all(
            compare_imports(self.imports[i], other.imports[i])
            for i in range(len(self.imports))
        ) and all(
            compare_classes(self.classes[i], other.classes[i])
            for i in range(len(self.classes))
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    def load(self):
        classes, imports = extract_classes_and_imports(self.__path)
        self.__classes = classes or None
        self.__imports = imports or None

    @property
    def classes(self) -> List[ast.ClassDef]:
        if not self.__classes:
            self.load()
        return self.__classes

    @property
    def imports(self) -> List[ast.AST]:
        if not self.__imports:
            self.load()
        return self.__imports

    @property
    def path(self) -> str:
        return self.__path

    def refactor(self):
        move_class_to_file(self.__path)
