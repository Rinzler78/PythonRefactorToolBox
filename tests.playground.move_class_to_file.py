from src.python_refactor_toolbox.python_refactor_tool import (
    compare_sources_directories,
    move_class_to_file_from_directory,
)
from tests.helper import (
    create_samples,
    expected_samples_directory,
    input_samples_directory,
    samples_directory,
)

create_samples(samples_directory)
move_class_to_file_from_directory(input_samples_directory)
compare_sources_directories(input_samples_directory, expected_samples_directory)
