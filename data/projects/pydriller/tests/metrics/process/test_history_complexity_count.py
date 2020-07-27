from pathlib import Path
from datetime import datetime

import pytest
from pydriller.metrics.process.history_complexity import HistoryComplexity

TEST_COMMIT_DATA = [
    ('test-repos/pydriller', 'scm/git_repository.py', '90ca34ebfe69629cb7f186a1582fc38a73cc572e', '90ca34ebfe69629cb7f186a1582fc38a73cc572e', 40.49),
    ('test-repos/pydriller', 'scm/git_repository.py', '71e053f61fc5d31b3e31eccd9c79df27c31279bf', '90ca34ebfe69629cb7f186a1582fc38a73cc572e', 47.05),
    ('https://github.com/geerlingguy/ansible-role-solr', 'tasks/main.yml', '7fb350c30be1124b51aab4a88352428e0a853b9a', '678429591513fe86045e892a1da680c8ac36e00f', .0)
]

@pytest.mark.parametrize('path_to_repo, filepath, from_commit, to_commit, expected', TEST_COMMIT_DATA)
def test_with_commits(path_to_repo, filepath, from_commit, to_commit, expected):
    metric = HistoryComplexity(path_to_repo=path_to_repo,
                               from_commit=from_commit,
                               to_commit=to_commit)
    
    count = metric.count()
    filepath = str(Path(filepath))
    assert count[filepath] == expected


TEST_DATE_DATA = [
    ('test-repos/pydriller', 'scm/git_repository.py', datetime(2018, 3, 22, 11, 30), datetime(2018, 3, 23), 40.49),
    ('test-repos/pydriller', 'scm/git_repository.py', datetime(2018, 3, 22, 11, 30), datetime(2018, 3, 27), 47.05),
]

@pytest.mark.parametrize('path_to_repo, filepath, since, to, expected', TEST_DATE_DATA)
def test_with_dates(path_to_repo, filepath, since, to, expected):
    metric = HistoryComplexity(path_to_repo=path_to_repo,
                               since=since,
                               to=to)
    
    count = metric.count()
    filepath = str(Path(filepath))
    assert count[filepath] == expected
