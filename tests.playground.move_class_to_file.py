from src.python_refactor_tool_box.source_directory import SourceDirectory  # noqa
from src.python_refactor_tool_box.source_file import SourceFile  # noqa
from tests.helper import expected_samples_directory  # noqa
from tests.helper import input_samples_directory  # noqa
from tests.helper import load_tests_files  # noqa

# create_samples(samples_directory)

# load_tests_files()

# input_source_directory = SourceDirectory(input_samples_directory)

# input_source_directory.refactor()
# input_source_directory.refactor()

# expected_source_directory = SourceDirectory(expected_samples_directory)

# input_source_directory == expected_source_directory

ffbb_api_client_file = SourceFile(
    "../FFBBApiClient-Python/src/ffbb_api_client/__init__.py"
)
ffbb_api_client_file.refactor()
