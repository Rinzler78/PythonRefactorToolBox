import argparse
import os
import sys

from .snake_case import to_snake_case  # noqa
from .source_directory import SourceDirectory  # noqa
from .source_file import SourceFile  # noqa

if sys.version_info[:2] >= (3, 8):
    # TODO: Import directly (no need for conditional) when `python_requires = >= 3.8`
    from importlib.metadata import PackageNotFoundError, version  # pragma: no cover
else:
    from importlib_metadata import PackageNotFoundError, version  # pragma: no cover

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = "python_refactor_tool_box"
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError


def init_module(path: str) -> None:
    if os.path.isdir(path):
        SourceDirectory(path).refactor()
    elif os.path.isfile(path):
        SourceFile(path).refactor()
    else:
        print(f"Error: {path} is neither a file nor a directory")


def main():
    parser = argparse.ArgumentParser(description="Initialize a Python module")
    parser.add_argument("path", type=str, help="Path to a directory or a file")

    args = parser.parse_args()
    init_module(args.path)


if __name__ == "__main__":
    main()
