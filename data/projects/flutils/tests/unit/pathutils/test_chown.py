import unittest
from types import SimpleNamespace
from unittest.mock import patch

from flutils.pathutils import chown

from ..mocks.pathlib import PosixPathMock


class TestChown(unittest.TestCase):

    def setUp(self):
        # Mock a Path
        self.path = PosixPathMock(
            '/home/test_user/tmp/test.txt',
            is_file=True
        )

        # Mock the flutils.pathutils.normalize_path() return value
        patcher = patch(
            'flutils.pathutils.normalize_path',
            return_value=self.path
        )
        self.normalize_path = patcher.start()
        self.addCleanup(patcher.stop)

        # Mock the flutils.pathutils.get_os_user() return value
        patcher = patch(
            'flutils.pathutils.get_os_user',
            return_value=SimpleNamespace(pw_uid=9753)
        )
        self.get_os_user = patcher.start()
        self.addCleanup(patcher.stop)

        # Mock the flutils.pathutils.get_os_group() return value
        patcher = patch(
            'flutils.pathutils.get_os_group',
            return_value=SimpleNamespace(gr_gid=1357)
        )
        self.get_os_group = patcher.start()
        self.addCleanup(patcher.stop)

        # Mock os.chown
        patcher = patch(
            'flutils.pathutils.os.chown',
            return_value=True
        )
        self.os_chown = patcher.start()
        self.addCleanup(patcher.stop)

    def test_chown_default(self):
        chown('~/tmp/test.txt')
        self.normalize_path.assert_called_with('~/tmp/test.txt')
        self.get_os_user.assert_called_with(None)
        self.get_os_group.assert_called_with(None)
        self.os_chown.assert_called_with(self.path.as_posix(), 9753, 1357)

    def test_chown_current_owner(self):
        chown('~/tmp/test.txt', user='-1', group='-1')
        self.normalize_path.assert_called_with('~/tmp/test.txt')
        self.get_os_user.assert_not_called()
        self.get_os_group.assert_not_called()
        self.os_chown.assert_called_with(self.path.as_posix(), -1, -1)

    def test_chown_user_group(self):
        chown('~/tmp/test.txt', user='test_user', group='test_group')
        self.normalize_path.assert_called_with('~/tmp/test.txt')
        self.get_os_user.assert_called_with('test_user')
        self.get_os_group.assert_called_with('test_group')
        self.os_chown.assert_called_with(self.path.as_posix(), 9753, 1357)


class TestChownGlob(unittest.TestCase):

    def setUp(self):
        # Mock out the following structure:
        #
        # /home/test_user
        # │ 
        # └── dir_tmp
        #     ├── dir_sub
        #     │   └── file_four
        #     ├── file_one
        #     ├── fifo_two
        #     └── file_three

        self.file_four = PosixPathMock(
            '/home/test_user/dir_tmp/dir_sub/file_four',
            is_file=True
        )
        self.dir_sub = PosixPathMock(
            '/home/test_user/dir_tmp/dir_sub',
            is_dir=True

        )
        self.file_three = PosixPathMock(
            '/home/test_user/dir_tmp/file_three',
            is_file=True
        )
        self.fifo_two = PosixPathMock(
            '/home/test_user/dir_tmp/fifo_two',
            is_fifo=True
        )
        self.file_one = PosixPathMock(
            '/home/test_user/dir_tmp/file_one',
            is_file=True
        )
        self.dir_tmp = PosixPathMock(
            '/home/test_user/dir_tmp',
            is_dir=True
        )
        # The function input as a glob
        self.path = PosixPathMock(
            '/home/test_user/**',
            glob=[
                self.file_four,
                self.dir_sub,
                self.file_three,
                self.fifo_two,
                self.file_one,
                self.dir_tmp
            ]
        )

        # Mock the flutils.pathutils.normalize_path() return value
        patcher = patch(
            'flutils.pathutils.normalize_path',
            return_value=self.path
        )
        self.normalize_path = patcher.start()
        self.addCleanup(patcher.stop)

        # Mock the pathlib.Path() return value
        patcher = patch(
            'flutils.pathutils.Path',
            return_value=self.path
        )
        self.path_func = patcher.start()
        self.addCleanup(patcher.stop)

        # Mock the flutils.pathutils.get_os_user() return value
        patcher = patch(
            'flutils.pathutils.get_os_user',
            return_value=SimpleNamespace(pw_uid=9753)
        )
        self.get_os_user = patcher.start()
        self.addCleanup(patcher.stop)

        # Mock the flutils.pathutils.get_os_group() return value
        patcher = patch(
            'flutils.pathutils.get_os_group',
            return_value=SimpleNamespace(gr_gid=1357)
        )
        self.get_os_group = patcher.start()
        self.addCleanup(patcher.stop)

        # Mock os.chown
        patcher = patch(
            'flutils.pathutils.os.chown',
            return_value=True
        )
        self.os_chown = patcher.start()
        self.addCleanup(patcher.stop)

    def test_chown_glob(self):
        chown('~/**')
        self.normalize_path.assert_called_with('~/**')
        self.get_os_user.assert_called_with(None)
        self.get_os_group.assert_called_with(None)
        for path in self.path.glob_data:
            if path.kwargs.get('is_dir', False) is True:
                self.os_chown.assert_any_call(path.as_posix(), 9753, 1357)
                path.is_dir.assert_called()
                path.is_file.assert_not_called()
            elif path.kwargs.get('is_file', False) is True:
                self.os_chown.assert_any_call(path.as_posix(), 9753, 1357)
                path.is_dir.assert_called()
                path.is_file.assert_called()
            else:
                path.is_dir.assert_called()
                path.is_file.assert_called()

    def test_chown_include_parent(self):
        chown('~/tmp/*', include_parent=True)
        self.normalize_path.assert_called_with('~/tmp/*')
        self.get_os_user.assert_called_with(None)
        self.get_os_group.assert_called_with(None)
        for path in self.path.glob_data:
            if path.kwargs.get('is_dir', False) is True:
                self.os_chown.assert_any_call(path.as_posix(), 9753, 1357)
                path.is_dir.assert_called()
                path.is_file.assert_not_called()
            elif path.kwargs.get('is_file', False) is True:
                self.os_chown.assert_any_call(path.as_posix(), 9753, 1357)
                path.is_dir.assert_called()
                path.is_file.assert_called()
            else:
                path.is_dir.assert_called()
                path.is_file.assert_called()
        self.os_chown.assert_any_call(self.path.parent.as_posix(), 9753, 1357)


class TestChownEmptyGlob(unittest.TestCase):

    def setUp(self):

        # The function input as a glob
        self.path = PosixPathMock(
            '/home/test_user/**',
        )

        # Mock the flutils.pathutils.normalize_path() return value
        patcher = patch(
            'flutils.pathutils.normalize_path',
            return_value=self.path
        )
        self.normalize_path = patcher.start()
        self.addCleanup(patcher.stop)

        # Mock the pathlib.Path() return value
        patcher = patch(
            'flutils.pathutils.Path',
            return_value=self.path
        )
        self.path_func = patcher.start()
        self.addCleanup(patcher.stop)

        # Mock the flutils.pathutils.get_os_user() return value
        patcher = patch(
            'flutils.pathutils.get_os_user',
            return_value=SimpleNamespace(pw_uid=9753)
        )
        self.get_os_user = patcher.start()
        self.addCleanup(patcher.stop)

        # Mock the flutils.pathutils.get_os_group() return value
        patcher = patch(
            'flutils.pathutils.get_os_group',
            return_value=SimpleNamespace(gr_gid=1357)
        )
        self.get_os_group = patcher.start()
        self.addCleanup(patcher.stop)

        # Mock os.chown
        patcher = patch(
            'flutils.pathutils.os.chown',
            return_value=True
        )
        self.os_chown = patcher.start()
        self.addCleanup(patcher.stop)

    def test_chown_empty_glob(self):
        chown('~/**')
        self.normalize_path.assert_called_with('~/**')
        self.get_os_user.assert_called_with(None)
        self.get_os_group.assert_called_with(None)
        self.os_chown.assert_not_called()
