from pathlib import Path
from datetime import datetime

import pytest

from pydriller.metrics.process.code_churn import CodeChurn

TEST_COMMIT_DATA = [
    ('test-repos/pydriller', 'domain/commit.py', 'ab36bf45859a210b0eae14e17683f31d19eea041', '71e053f61fc5d31b3e31eccd9c79df27c31279bf', 47, 34, 16)
]

@pytest.mark.parametrize('path_to_repo, filepath, from_commit, to_commit, expected_count, expected_max, expected_avg', TEST_COMMIT_DATA)
def test_with_commits(path_to_repo, filepath, from_commit, to_commit, expected_count, expected_max, expected_avg):
    metric = CodeChurn(path_to_repo=path_to_repo,
                       from_commit=from_commit,
                       to_commit=to_commit)

    actual_count = metric.count()
    actual_max = metric.max()
    actual_avg = metric.avg()

    filepath = str(Path(filepath))

    assert actual_count[filepath] == expected_count
    assert actual_max[filepath] == expected_max
    assert actual_avg[filepath] == expected_avg


TEST_DATE_DATA = [
    ('test-repos/pydriller', 'domain/commit.py', datetime(2018, 3, 21), datetime(2018, 3, 27), 47, 34, 16)
]

@pytest.mark.parametrize('path_to_repo, filepath, since, to, expected_count, expected_max, expected_avg', TEST_DATE_DATA)
def test_with_dates(path_to_repo, filepath, since, to, expected_count, expected_max, expected_avg):
    metric = CodeChurn(path_to_repo=path_to_repo,
                       since=since,
                       to=to)

    actual_count = metric.count()
    actual_max = metric.max()
    actual_avg = metric.avg()

    filepath = str(Path(filepath))

    assert actual_count[filepath] == expected_count
    assert actual_max[filepath] == expected_max
    assert actual_avg[filepath] == expected_avg

