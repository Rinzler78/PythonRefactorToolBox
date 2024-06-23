from .python_refactor_helper import compare_codes_from_files, refactor_from_file


class SourceFile:
    __path: str = None

    def __init__(self, path):
        self.__path = path

    def __eq__(self, other):
        if not (other and isinstance(other, SourceFile)):
            return False

        return compare_codes_from_files(self.__path, other.__path)

    def __ne__(self, other):
        return not self.__eq__(other)

    def load_code(self, code: str):
        self.code = code

    @property
    def path(self) -> str:
        return self.__path

    def refactor(self):
        refactor_from_file(self.__path)
