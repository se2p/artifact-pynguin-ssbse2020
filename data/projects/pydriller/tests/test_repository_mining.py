import logging
from datetime import datetime

import pytest

from pydriller import RepositoryMining, GitRepository

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


@pytest.fixture
def path():
    return None


@pytest.fixture
def to():
    return None


@pytest.fixture
def repo(path):
    return list(RepositoryMining(path_to_repo=path).traverse_commits())


@pytest.fixture
def repo_to(path, to):
    return list(RepositoryMining(path_to_repo=path, to=to).traverse_commits())


@pytest.fixture()
def git_repo(path):
    gr = GitRepository(path)
    yield gr
    gr.clear()


# It should fail when no URLs are specified
def test_no_url():
    with pytest.raises(Exception):
        list(RepositoryMining().traverse_commits())


# It should fail when URL is not a string or a List
def test_badly_formatted_repo_url():
    with pytest.raises(Exception):
        list(RepositoryMining(path_to_repo=set('repo')).traverse_commits())


@pytest.mark.parametrize('path,expected', [
    ("test-repos/small_repo", 5)
])
def test_simple_url(repo, expected):
    assert len(repo) == expected


@pytest.mark.parametrize('path,expected', [
    (["test-repos/small_repo", "test-repos/branches_merged"], 9)
])
def test_two_local_urls(repo, expected):
    assert len(repo) == expected


@pytest.mark.parametrize('path,to,expected', [
    ("https://github.com/ishepard/pydriller.git",
     datetime(2018, 10, 20),
     159)
])
def test_simple_remote_url(repo_to, expected):
    assert len(repo_to) == expected


@pytest.mark.parametrize('path,to,expected', [
    (["https://github.com/mauricioaniche/repodriller.git",
      "https://github.com/ishepard/pydriller"],
     datetime(2018, 10, 20),
     518)
])
def test_two_remote_urls(repo_to, expected):
    assert len(repo_to) == expected


@pytest.mark.parametrize('path,expected', [
    (["test-repos/small_repo", "test-repos/small_repo"], 10)
])
def test_2_identical_local_urls(repo, expected):
    assert len(repo) == expected


@pytest.mark.parametrize('path,to,expected', [
    (["test-repos/small_repo", "https://github.com/ishepard/pydriller.git"],
     datetime(2018, 10, 20),
     164)
])
def test_both_local_and_remote_urls(repo_to, expected):
    assert len(repo_to) == expected


@pytest.mark.parametrize('path,to,expected', [
    (["test-repos/small_repo", "https://github.com/mauricioaniche/repodriller.git",
      "test-repos/branches_merged", "https://github.com/ishepard/pydriller.git"],
     datetime(2018, 10, 20),
     527)
])
def test_both_local_and_remote_urls_list(repo_to, expected):
    assert len(repo_to) == expected


def test_badly_formatted_url():
    with pytest.raises(Exception):
        list(RepositoryMining(
            path_to_repo='https://github.com/ishepard.git/test')
             .traverse_commits())

    with pytest.raises(Exception):
        list(RepositoryMining(path_to_repo='test').traverse_commits())


@pytest.mark.parametrize('path', ["test-repos/histogram"])
def test_diff_without_histogram(git_repo):
    # without histogram
    commit = list(RepositoryMining('test-repos/histogram',
                                   single="93df8676e6fab70d9677e94fd0f6b17db095e890").traverse_commits())[0]

    diff = commit.modifications[0].diff_parsed
    assert len(diff['added']) == 11
    assert (3, '    if (path == null)') in diff['added']
    assert (5, '        log.error("Icon path is null");') in diff['added']
    assert (6, '        return null;') in diff['added']
    assert (8, '') in diff['added']
    assert (9, '    java.net.URL imgURL = GuiImporter.class.getResource(path);') in diff['added']
    assert (10, '') in diff['added']
    assert (11, '    if (imgURL == null)') in diff['added']
    assert (12, '    {') in diff['added']
    assert (14, '        return null;') in diff['added']
    assert (16, '    else') in diff['added']
    assert (17, '        return new ImageIcon(imgURL);') in diff['added']

    assert len(diff['deleted']) == 7
    assert (3, '    java.net.URL imgURL = GuiImporter.class.getResource(path);') in diff['deleted']
    assert (4, '') in diff['deleted']
    assert (5, '    if (imgURL != null)') in diff['deleted']
    assert (7, '        return new ImageIcon(imgURL);') in diff['deleted']
    assert (9, '    else') in diff['deleted']
    assert (10, '    {') in diff['deleted']
    assert (13, '    return null;') in diff['deleted']


@pytest.mark.parametrize('path', ["test-repos/histogram"])
def test_diff_with_histogram(git_repo):
    # with histogram
    commit = list(RepositoryMining('test-repos/histogram',
                                   single="93df8676e6fab70d9677e94fd0f6b17db095e890",
                                   histogram_diff=True).traverse_commits())[0]
    diff = commit.modifications[0].diff_parsed
    assert (4, '    {') in diff["added"]
    assert (5, '        log.error("Icon path is null");') in diff["added"]
    assert (6, '        return null;') in diff["added"]
    assert (7, '    }') in diff["added"]
    assert (8, '') in diff["added"]
    assert (11, '    if (imgURL == null)') in diff["added"]
    assert (12, '    {') in diff["added"]
    assert (13, '        log.error("Couldn\'t find icon: " + imgURL);') in diff["added"]
    assert (14, '        return null;') in diff["added"]
    assert (17, '        return new ImageIcon(imgURL);') in diff["added"]

    assert (6, '    {') in diff["deleted"]
    assert (7, '        return new ImageIcon(imgURL);') in diff["deleted"]
    assert (10, '    {') in diff["deleted"]
    assert (11, '        log.error("Couldn\'t find icon: " + imgURL);') in diff["deleted"]
    assert (12, '    }') in diff["deleted"]
    assert (13, '    return null;') in diff["deleted"]


def test_ignore_add_whitespaces():
    commit = list(RepositoryMining('test-repos/whitespace',
                                   single="338a74ceae164784e216555d930210371279ba8e").traverse_commits())[0]
    assert len(commit.modifications) == 1
    commit = list(RepositoryMining('test-repos/whitespace',
                                   skip_whitespaces=True,
                                   single="338a74ceae164784e216555d930210371279ba8e").traverse_commits())[0]
    assert len(commit.modifications) == 0


@pytest.mark.parametrize('path', ["test-repos/whitespace"])
def test_ignore_add_whitespaces_and_modified_normal_line(git_repo):
    commit = list(RepositoryMining('test-repos/whitespace',
                                   single="52716ef1f11e07308b5df1b313aec5496d5e91ce").traverse_commits())[0]
    assert len(commit.modifications) == 1
    parsed_normal_diff = commit.modifications[0].diff_parsed
    commit = list(RepositoryMining('test-repos/whitespace',
                                   skip_whitespaces=True,
                                   single="52716ef1f11e07308b5df1b313aec5496d5e91ce").traverse_commits())[0]
    assert len(commit.modifications) == 1
    parsed_wo_whitespaces_diff = commit.modifications[0].diff_parsed
    assert len(parsed_normal_diff['added']) == 2
    assert len(parsed_wo_whitespaces_diff['added']) == 1

    assert len(parsed_normal_diff['deleted']) == 1
    assert len(parsed_wo_whitespaces_diff['deleted']) == 0


def test_ignore_deleted_whitespaces():
    commit = list(RepositoryMining('test-repos/whitespace',
                                   single="e6e429f6b485e18fb856019d9953370fd5420b20").traverse_commits())[0]
    assert len(commit.modifications) == 1
    commit = list(RepositoryMining('test-repos/whitespace',
                                   skip_whitespaces=True,
                                   single="e6e429f6b485e18fb856019d9953370fd5420b20").traverse_commits())[0]
    assert len(commit.modifications) == 0


def test_ignore_add_whitespaces_and_changed_file():
    commit = list(RepositoryMining('test-repos/whitespace',
                                   single="532068e9d64b8a86e07eea93de3a57bf9e5b4ae0").traverse_commits())[0]
    assert len(commit.modifications) == 2
    commit = list(RepositoryMining('test-repos/whitespace',
                                   skip_whitespaces=True,
                                   single="532068e9d64b8a86e07eea93de3a57bf9e5b4ae0").traverse_commits())[0]
    assert len(commit.modifications) == 1


def test_clone_repo_to(tmp_path):
    dt2 = datetime(2018, 10, 20)
    url = "https://github.com/ishepard/pydriller.git"
    assert len(list(RepositoryMining(
        path_to_repo=url,
        to=dt2,
        clone_repo_to=str(tmp_path)).traverse_commits())) == 159


def test_clone_repo_to_not_existing():
    with pytest.raises(Exception):
        list(RepositoryMining("https://github.com/ishepard/pydriller",
                              clone_repo_to="NOTEXISTINGDIR").traverse_commits())
