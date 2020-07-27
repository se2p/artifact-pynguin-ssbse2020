# -*- coding: utf-8 -*-

"""Pack the distribution of apimd."""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2020"
__license__ = "MIT"
__email__ = "pyslvs@gmail.com"

from re import MULTILINE, search
from os.path import join as pth_join
from setuptools import setup, find_packages


def read(path: str):
    with open(path, 'r') as f:
        return f.read()


def find_version(path: str):
    m = search(r"^__version__ = ['\"]([^'\"]*)['\"]", read(path), MULTILINE)
    if m:
        return m.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name='apimd',
    version=find_version(pth_join('apimd', '__init__.py')),
    author=__author__,
    author_email=__email__,
    license=__license__,
    description="A Python API compiler for universal Markdown syntax.",
    long_description=read("README.md"),
    long_description_content_type='text/markdown',
    url="https://github.com/KmolYuan/apimd",
    packages=find_packages(),
    package_data={'apimd': ['py.typed']},
    entry_points={'console_scripts': ['apimd=apimd.__main__:main']},
    zip_safe=False,
    python_requires=">=3.7",
    options={'bdist_wheel': {'python_tag': 'cp37.cp38'}},
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Documentation",
        "Topic :: Utilities",
        "Environment :: Console",
        "Operating System :: OS Independent",
        "Typing :: Typed",
    ]
)
