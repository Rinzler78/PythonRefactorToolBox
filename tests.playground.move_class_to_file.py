from src.python_refactor_tool_box.source_directory import SourceDirectory
from tests.helper import (
    expected_samples_directory,
    input_samples_directory,
    load_tests_files,
)

# create_samples(samples_directory)

load_tests_files()

input_source_directory = SourceDirectory(input_samples_directory)

input_source_directory.refactor()
input_source_directory.refactor()

expected_source_directory = SourceDirectory(expected_samples_directory)

input_source_directory == expected_source_directory
