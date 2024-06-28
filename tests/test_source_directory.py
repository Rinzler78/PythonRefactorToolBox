import unittest

from helper import (
    create_sample_files,
    expected_samples_directory,
    input_samples_directory,
    samples_directory,
)

from python_refactor_tool_box import SourceDirectory


class TestSourceDirectory(unittest.TestCase):
    def setUp(self):
        create_sample_files()

    def setup_method(self, method):
        self.setUp()

    def test_load(self):
        source_directory = SourceDirectory(samples_directory)
        source_directory.load()

    def test_refactor(self):
        input_source_directory = SourceDirectory(input_samples_directory)
        input_source_directory.refactor()

        expected_source_directory = SourceDirectory(expected_samples_directory)
        expected_source_directory.refactor()

        self.assertTrue(input_source_directory == expected_source_directory)
