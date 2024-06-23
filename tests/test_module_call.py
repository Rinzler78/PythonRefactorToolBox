import unittest
from unittest.mock import patch

from helper import create_samples, input_samples_directory, samples_directory

from python_refactor_tool_box.__init__ import main

input_file = input_samples_directory + "/Bobo.py"


class TestModuleCall(unittest.TestCase):
    def setUp(self):
        create_samples(samples_directory)

    def setup_method(self, method):
        self.setUp()

    @patch("sys.argv", ["init_module.py", input_samples_directory])
    def test_call_with_directory(self):
        with patch("builtins.print"):
            main()

    @patch("sys.argv", ["init_module.py", input_file])
    def test_call_with_file(self):
        with patch("builtins.print"):
            main()

    @patch("sys.argv", ["init_module.py", "/invalid/path"])
    def test_call_with_invalid_path(self):
        with patch("builtins.print") as mocked_print:
            main()
            mocked_print.assert_any_call(
                "Error: /invalid/path is neither a file nor a directory"
            )


if __name__ == "__main__":
    unittest.main()
