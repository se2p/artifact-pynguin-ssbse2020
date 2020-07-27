import csv
import importlib
import inspect
import os
import sys
import typing
from dataclasses import dataclass
from typing import Set, Union, Callable, Tuple

from find_packages import find_modules


@dataclass
class ModuleTypes:
    parameter_types: Set[type]
    return_types: Set[type]


def extract_types_for_module(
    project_path: Union[str, os.PathLike], module_name: str
) -> ModuleTypes:
    sys.path.insert(0, project_path)
    module_types = ModuleTypes(set(), set())
    module = importlib.import_module(module_name)
    for key, member in inspect.getmembers(module):
        if (
            not inspect.isclass(member)
            and not inspect.ismethod(member)
            and not inspect.isfunction(member)
        ):
            continue
        parameter_types, return_types = infer_type_info(member)
        module_types.parameter_types.update(parameter_types)
        module_types.return_types.update(return_types)
    return module_types


def infer_type_info(element: Callable) -> Tuple[Set[type], Set[type]]:
    if inspect.isclass(element) and hasattr(element, "__init__"):
        return infer(getattr(element, "__init__"))
    return infer(element)


def infer(element: Callable) -> Tuple[Set[type], Set[type]]:
    parameter_types: Set[type] = set()
    return_types: Set[type] = set()
    signature = inspect.signature(element)
    hints = typing.get_type_hints(element)
    for param_name in signature.parameters:
        if param_name == "self":
            continue
        parameter_type = hints.get(param_name, None)
        if parameter_type is not None:
            parameter_types.add(parameter_type)
    return_type = hints.get("return", None)
    if return_type is not None:
        return_types.add(return_type)
    return parameter_types, return_types


def main():
    projects = [
        "apimd",
        "async_btree",
        "codetiming",
        "docstring_parser",
        "flutes",
        "flutils",
        "mimesis",
        "pypara",
        "python-string-utils",
        "pytutils",
    ]
    with open("/tmp/types.csv", mode="w") as csv_file:
        field_names = [
            "module",
            "num_parameter_types",
            "num_return_types",
            "parameter_types",
            "return_types",
        ]
        writer = csv.DictWriter(csv_file, fieldnames=field_names, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for project in projects:
            path = os.path.join(
                "/Users/sl/repos/papers/python-test-generation-experiments/projects",
                project
            )
            for module in find_modules(path):
                print(module)
                print(extract_types_for_module(path, module))
                module_types = extract_types_for_module(path, module)
                writer.writerow({
                    "module": module,
                    "num_parameter_types": len(module_types.parameter_types),
                    "num_return_types": len(module_types.return_types),
                    "parameter_types": module_types.parameter_types,
                    "return_types": module_types.return_types,
                })


if __name__ == '__main__':
    main()
