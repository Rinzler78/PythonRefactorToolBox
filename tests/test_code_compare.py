import unittest

from helper import (
    create_sample_files,
    expected_samples_directory,
    input_samples_directory,
)

from python_refactor_tool_box.code_compare_helper import (
    compare_codes_from_files,
    compare_from_code,
)


class TestCodeCompareHelper(unittest.TestCase):
    def setUp(self):
        create_sample_files()

    def setup_method(self, method):
        self.setUp()

    def test_compare_from_code_same_code(self):
        code = "def add(a, b):\n    return a + b\n"
        self.assertTrue(compare_from_code(code, code))

    def test_compare_from_code_different_code(self):
        code1 = "def add(a, b):\n    return a + b\n"
        code2 = "def add(a, b):\n return a + b\n"
        self.assertTrue(compare_from_code(code1, code2))

    def test_compare_codes_from_files_same_files(self):
        file_path = input_samples_directory + "/main.py"
        self.assertTrue(compare_codes_from_files(str(file_path), str(file_path)))

    def test_compare_codes_from_files_different_files(self):
        file_path1 = input_samples_directory + "/main.py"
        file_path2 = expected_samples_directory + "/utils/helper.py"
        self.assertFalse(compare_codes_from_files(str(file_path1), str(file_path2)))
