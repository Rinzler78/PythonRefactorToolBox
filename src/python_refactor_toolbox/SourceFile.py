from .python_refactor_tool import compare_sources_files, move_class_to_file


class SourceFile:
    __path: str = None

    def __init__(self, path):
        self.__path = path

    def __eq__(self, other):
        return compare_sources_files(self.__path, other.path)

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def path(self) -> str:
        return self.__path

    def refactor(self):
        move_class_to_file(self.__path)
