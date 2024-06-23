import os
from typing import List

from .SourceFile import SourceFile


class SourceDirectory:
    __path: str = None
    __source_files: List[SourceFile] = None

    def __init__(self, path):
        self.__path = path
        self.load()

    def __eq__(self, other) -> bool:
        if not (other and isinstance(other, SourceDirectory)):
            return False

        if not (
            self.source_files
            and other.source_files
            and len(self.source_files) == len(other.source_files)
        ):
            return False

        return all(
            self.source_files[i] == other.source_files[i]
            for i in range(len(self.source_files))
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def path(self) -> str:
        return self.__path

    @property
    def source_files(self) -> List[SourceFile]:
        if not self.__source_files:
            self.load()
        return self.__source_files

    def load(self):
        if not self.__path:
            return

        source_files = []
        for root, _, files in os.walk(self.__path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    source_files.append(SourceFile(file_path))

        self.__source_files = source_files or None

    def refactor(self):
        for source_file in self.__source_files:
            source_file.refactor()
        self.load()
