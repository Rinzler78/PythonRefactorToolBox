from src.python_refactor_toolbox.SourceDirectory import SourceDirectory
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


# def __get_source_files(directory):
#     return SourceDirectory(directory).source_files


# input_source_files = __get_source_files(input_samples_directory)

# for file in input_source_files:
#     file.refactor()

# input_source_files = __get_source_files(input_samples_directory)
# expected_source_files = __get_source_files(expected_samples_directory)

# if len(input_source_files) != len(expected_source_files):
#     print(len(input_source_files))
#     print(len(expected_source_files))

# for i in range(len(input_source_files)):
#     if not input_source_files[i] == expected_source_files[i]:
#         print(i)
#         print(input_source_files[i])
#         print(expected_source_files[i])
