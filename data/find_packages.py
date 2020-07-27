#!/usr/bin/env python3
"""Searches for Python modules in a given path and prints them to STDOUT."""
import os
import sys
from typing import Set, Union

from setuptools import find_packages
from pkgutil import iter_modules


def error_print(*args, **kwargs) -> None:
    """Prints to STDERR.

    :param args: A list of arguments
    :param kwargs: A map of key-value-arguments
    """
    print(*args, file=sys.stderr, **kwargs)


def find_modules(path: Union[str, os.PathLike]) -> Set[str]:
    """Finds Python modules under a given path and returns them.

    :param path: The path to search for Python modules
    :return: A set of found modules
    """
    modules: Set[str] = set()
    for package in find_packages(
        path, exclude=[
            "*.tests",
            "*.tests.*",
            "tests.*",
            "tests",
            "test",
            "test.*",
            "*.test.*",
            "*.test",
        ]
    ):
        pkg_path = "{}/{}".format(path, package.replace(".", "/"))
        for info in iter_modules([pkg_path]):
            if not info.ispkg:
                modules.add(f"{package}.{info.name}")
    return modules


if __name__ == '__main__':
    if sys.version_info < (3, 6, 0):
        error_print("Requires at least Python 3.6.0")
        sys.exit(1)
    if not len(sys.argv) == 2:
        error_print("Usage: find_packages.py <path/to/project/root>")
        error_print("Searches for all Python modules in <path/to/project/root> and")
        error_print("returns them one module name per line")
        sys.exit(1)
    for module in find_modules(sys.argv[1].strip()):
        print(module.strip())
