#!/usr/bin/env python3
import csv
import ctypes
import glob
import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any


class MergeStatisticsCSV:
    def __init__(self, project_name: str, iteration: int) -> None:
        self._csv_header: Optional[List[str]] = None
        self._csv_rows: List[Dict[str, Any]] = []
        self._project_name: str = project_name
        self._iteration: int = iteration
        self._my_dir: str = os.path.dirname(os.path.abspath(__file__))
        csv.field_size_limit(int(ctypes.c_ulong(-1).value // 2))

    def merge(self) -> None:
        print("Load CSV files")
        self._load_csv_file_contents()
        print("Write result CSV file")
        self._write_csv_file()

    def _load_csv_file_contents(self) -> None:
        for input_file in glob.iglob(
            f"{self._my_dir}/../pynguin-results/{self._project_name}/statistics-*.csv"
        ):
            with open(input_file) as csv_file:
                reader = csv.DictReader(csv_file, quoting=csv.QUOTE_NONNUMERIC)
                content = [row for row in reader]
                if not self._csv_header:
                    self._retrieve_header(content)
                assert len(content) == 1,\
                    "Cannot handle CSV file with more than one result row!"
                self._csv_rows.append(content[0])

    def _retrieve_header(self, csv_content: List[Dict[str, Any]]) -> None:
        assert len(csv_content) > 0, "Cannot retrieve header from empty CSV file!"
        self._csv_header = [key for key, _ in csv_content[0].items()]

    def _write_csv_file(self) -> None:
        assert self._csv_header, "Cannot work with empty CSV header list!"
        p = Path(self._my_dir) / "data" / self._project_name
        p.mkdir(parents=True, exist_ok=True)
        with open(os.path.join(
            self._my_dir,
            "data",
            self._project_name,
            f"statistics-iteration-{self._iteration}.csv"
        ), mode="w") as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=self._csv_header,
                restval="0",
                quoting=csv.QUOTE_NONNUMERIC,
            )
            writer.writeheader()
            writer.writerows(self._csv_rows)


if __name__ == '__main__':
    merger = MergeStatisticsCSV(sys.argv[1], int(sys.argv[2]))
    merger.merge()
