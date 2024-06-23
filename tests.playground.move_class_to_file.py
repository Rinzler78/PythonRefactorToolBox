from src.python_refactor_tool_box.source_directory import SourceDirectory
from tests.helper import (
    create_samples,
    expected_samples_directory,
    input_samples_directory,
    samples_directory,
)

create_samples(samples_directory)

input_source_directory = SourceDirectory(input_samples_directory)

input_source_directory.refactor()
input_source_directory.refactor()

expected_source_directory = SourceDirectory(expected_samples_directory)

input_source_directory == expected_source_directory
