import unittest

from helper import (
    create_samples,
    expected_samples_directory,
    input_samples_directory,
    samples_directory,
)

from python_refactor_toolbox.python_refactor_tool import (
    compare_sources_directories,
    move_class_to_file_from_directory,
)


class TestMoveClassToFile(unittest.TestCase):

    def setUp(self):
        create_samples(samples_directory)

    def setup_method(self, method):
        self.setUp()

    def test_with_samples(self):
        move_class_to_file_from_directory(input_samples_directory)
        self.assertEqual(
            compare_sources_directories(
                input_samples_directory, expected_samples_directory
            ),
            True,
        )
