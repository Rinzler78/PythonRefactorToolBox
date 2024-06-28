import ast
import os
import shutil
import zipfile

import astor

from python_refactor_tool_box.code_format_helper import format_code

global samples_directory
global input_samples_directory
global expected_samples_directory

samples_directory = "./samples"
input_samples_directory = f"{samples_directory}/input"
expected_samples_directory = f"{samples_directory}/expected"


def refactor_code(code: str) -> str:
    """
    Refactor the given code by sorting imports and formatting code.
    """
    tree = ast.parse(code)
    tree.body.sort(key=lambda node: isinstance(node, ast.ImportFrom))
    refactored_code = astor.to_source(tree)
    return format_code(refactored_code)


def create_sample_files(input_dir: str = input_samples_directory):
    """
    Create sample input Python files and their expected refactored output.
    """

    if os.path.exists(input_dir):
        shutil.rmtree(input_dir)

    samples = {
        "main.py": """
import os
import sys
from utils.helper import greet
from modules.mod1 import MyClass

class MyMainClass():
    def method_one(self):
        txt: str = "Method One"
        print(txt)
        return txt


def another_func():
    print("Another Function")
    return MyMainClass()

def main():
    greet()
    obj = MyClass()
    obj.method_one()

    my_main_class = another_func()

if __name__ == "__main__":
    main()
""",
        "utils/helper.py": """
def greet():
    print("Hello, world!")
""",
        "modules/mod1.py": """
class MyClass:
    def method_one(self):
        print("Method One")
""",
        "modules/mod2.py": """
from .mod1 import MyClass

class AnotherClass:
    def method_two(self):
        obj = MyClass()
        obj.method_one()
""",
        "subdir/subsubdir/sample.py": """
from modules.mod1 import MyClass

def run():
    obj = MyClass()
    obj.method_one()
""",
        "subdir/subsubdir/__init__.py": """
# This is an init file for the subsubdir package
""",
        "modules/__init__.py": """
# This is an init file for the modules package
""",
        "utils/__init__.py": """
# This is an init file for the utils package
""",
        "subdir/__init__.py": """
# This is an init file for the subdir package
""",
    }

    for filename, content in samples.items():
        input_path = os.path.join(input_dir, filename)
        os.makedirs(os.path.dirname(input_path), exist_ok=True)

        with open(input_path, "w") as input_file:
            input_file.write(content.strip())


def load_tests_files():
    if os.path.exists(samples_directory):
        shutil.rmtree(samples_directory)

    with zipfile.ZipFile("samples.zip", "r") as zip_ref:
        zip_ref.extractall(".")
