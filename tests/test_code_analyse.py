import ast
import unittest

from python_refactor_tool_box.code_analyze_helper import (
    should_delete_file,
    should_delete_file_from_code_tree,
)


class TestCodeAnalyzeHelper(unittest.TestCase):
    def test_should_delete_file_empty_code(self):
        self.assertTrue(should_delete_file(""))

    def test_should_delete_file_only_comments(self):
        code = """
        # This is a comment
        # Another comment
        """
        self.assertTrue(should_delete_file(code))

    def test_should_delete_file_only_imports(self):
        code = """
        import os
        from typing import List
        """
        self.assertTrue(should_delete_file(code))

    def test_should_delete_file_mixed_comments_and_imports(self):
        code = """
        # This is a comment
        import os
        from typing import List
        """
        self.assertTrue(should_delete_file(code))

    def test_should_not_delete_file_with_code(self):
        code = """
        def hello_world():
            print("Hello, World!")
        """
        self.assertFalse(should_delete_file(code))

    def test_should_delete_file_from_code_tree_empty_code_tree(self):
        code_tree = {}
        self.assertTrue(should_delete_file_from_code_tree(code_tree))

    def test_should_delete_file_from_code_tree_only_imports(self):
        code_tree = {
            ast.Import: [ast.Import(names=[ast.alias(name="os", asname=None)])],
            ast.ImportFrom: [
                ast.ImportFrom(
                    module="sys", names=[ast.alias(name="path", asname=None)]
                )
            ],
        }
        self.assertTrue(should_delete_file_from_code_tree(code_tree))

    def test_should_delete_file_from_code_tree_mixed_code(self):
        code_tree = {
            ast.Import: [ast.Import(names=[ast.alias(name="os", asname=None)])],
            ast.ImportFrom: [
                ast.ImportFrom(
                    module="sys", names=[ast.alias(name="path", asname=None)]
                )
            ],
            ast.FunctionDef: [
                ast.FunctionDef(
                    name="test_function",
                    args=ast.arguments(
                        args=[], vararg=None, kwonlyargs=[], kwarg=None, defaults=[]
                    ),
                    body=[],
                    decorator_list=[],
                    returns=None,
                )
            ],
        }
        self.assertFalse(should_delete_file_from_code_tree(code_tree))
