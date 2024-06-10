import unittest
from typing import List

from helper import (
    create_samples,
    expected_samples_directory,
    input_samples_directory,
    samples_directory,
)

from python_refactor_toolbox.SourceDirectory import SourceDirectory
from python_refactor_toolbox.SourceFile import SourceFile


class TestSourceFile(unittest.TestCase):
    def setUp(self):
        create_samples(samples_directory)

    def setup_method(self, method):
        self.setUp()

    def __get_source_files(self, directory) -> List[SourceFile]:
        return SourceDirectory(directory).source_files

    def test_refactor(self):
        input_source_files = self.__get_source_files(input_samples_directory)

        for file in input_source_files:
            file.refactor()

        input_source_files = self.__get_source_files(input_samples_directory)
        expected_source_files = self.__get_source_files(expected_samples_directory)

        self.assertTrue(len(input_source_files), len(expected_source_files))

        for i in range(len(input_source_files)):
            self.assertTrue(input_source_files[i] == expected_source_files[i])
