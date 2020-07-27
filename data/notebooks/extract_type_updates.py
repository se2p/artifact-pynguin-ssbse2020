#!/usr/bin/env python3
import ast
import csv
import ctypes
import glob
import pprint


def replace(s: str) -> str:
    return (
        s.replace("&gt;", ">")
        .replace("&lt;", "<")
        .replace("&quot;", '"')
        .replace("&amp;", "&")
    )


def extract_type_updates():
    types = {}
    for csv_file in glob.iglob("../data/**/*.csv"):
        name = csv_file.split("/")[-2]
        if name not in types:
            types[name] = {}
        reader = csv.DictReader(open(csv_file), quoting=csv.QUOTE_NONNUMERIC)
        for row in reader:
            module = row["TARGET_CLASS"]
            config = row["configuration_id"]
            if module not in types[name]:
                types[name][module] = {}
            try:
                parameter_type_updates = ast.literal_eval(row["ParameterTypeUpdates"])
            except SyntaxError:
                parameter_type_updates = []
            try:
                return_type_updates = ast.literal_eval(row["ReturnTypeUpdates"])
            except SyntaxError:
                return_type_updates = []
            types[name][module][config] = {
                "ParameterTypeUpdates": [replace(s) for s in parameter_type_updates],
                "ReturnTypeUpdates": [replace(s) for s in return_type_updates],
            }
    return types


def main():
    csv.field_size_limit(int(ctypes.c_ulong(-1).value // 2))
    pprint.pprint(extract_type_updates(), indent=1, width=240)


if __name__ == '__main__':
    main()
