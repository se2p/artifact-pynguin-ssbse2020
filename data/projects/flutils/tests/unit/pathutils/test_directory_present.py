import unittest
from unittest.mock import patch

from flutils.pathutils import directory_present

from ..mocks.pathlib import PosixPathMock


class TestDirectoryPresent(unittest.TestCase):

    def setUp(self):
        #  /home/test_user/tmp
        #  │
        #  └── dir_one
        #      │
        #      └── dir_two
        #          │
        #          └── path
        #
        self.tmp = PosixPathMock(
            '/home/test_user/tmp',
            is_dir=True,
            exists=True
        )
        self.dir_one = PosixPathMock(
            '/home/test_user/tmp/dir_one',
            is_dir=False,
            exists=False,
            parent=self.tmp,
        )
        self.dir_two = PosixPathMock(
            '/home/test_user/tmp/dir_one/dir_two',
            is_dir=False,
            exists=False,
            parent=self.dir_one
        )
        self.path = PosixPathMock(
            '/home/test_user/tmp/dir_one/dir_two/path',
            is_dir=False,
            exists=False,
            parent=self.dir_two
        )

        # patch the normalize_path() function to return self.path_one.
        patcher = patch(
            'flutils.pathutils.normalize_path',
            return_value=self.path
        )
        self.normalize_path = patcher.start()
        self.addCleanup(patcher.stop)

        # patch the exists_as() function to return multiple results.
        patcher = patch(
            'flutils.pathutils.exists_as',
            side_effect=[
                '',
                '',
                '',
                'directory'
            ]
        )
        self.exists_as = patcher.start()
        self.addCleanup(patcher.stop)

        # patch the chown() function.
        patcher = patch(
            'flutils.pathutils.chown',
            return_value=None
        )
        self.chown = patcher.start()
        self.addCleanup(patcher.stop)

        # patch the chmod() function.
        patcher = patch(
            'flutils.pathutils.chmod',
            return_value=None
        )
        self.chmod = patcher.start()
        self.addCleanup(patcher.stop)

    def test_directory_present_with_parents_default(self):
        directory_present(self.path.as_posix())
        self.normalize_path.assert_called_with(self.path.as_posix())
        self.path.mkdir.assert_called_with(mode=0o700)
        self.dir_two.mkdir.assert_called_with(mode=0o700)
        self.dir_one.mkdir.assert_called_with(mode=0o700)
        self.tmp.mkdir.assert_not_called()
        self.chown.assert_any_call(self.path, user=None, group=None)
        self.chown.assert_any_call(self.dir_two, user=None, group=None)
        self.chown.assert_any_call(self.dir_one, user=None, group=None)
        self.chmod.assert_not_called()

    def test_directory_present_with_parents_mode_user_group(self):
        mode = 0o770
        user = 'test_user'
        group = 'test_group'
        directory_present(
            self.path.as_posix(),
            mode=mode,
            user=user,
            group=group
        )
        self.normalize_path.assert_called_with(self.path.as_posix())
        self.path.mkdir.assert_called_with(mode=mode)
        self.dir_two.mkdir.assert_called_with(mode=mode)
        self.dir_one.mkdir.assert_called_with(mode=mode)
        self.tmp.mkdir.assert_not_called()
        self.chown.assert_any_call(self.path, user=user, group=group)
        self.chown.assert_any_call(self.dir_two, user=user, group=group)
        self.chown.assert_any_call(self.dir_one, user=user, group=group)
        self.chmod.assert_not_called()


class TestDirectoryPresentExisting(unittest.TestCase):

    def setUp(self):
        #  /home/test_user/tmp
        #  │
        #  └── dir_one
        #      │
        #      └── dir_two
        #          │
        #          └── path
        #
        self.tmp = PosixPathMock(
            '/home/test_user/tmp',
            is_dir=True,
            exists=True
        )
        self.dir_one = PosixPathMock(
            '/home/test_user/tmp/dir_one',
            is_dir=True,
            exists=True,
            parent=self.tmp,
        )
        self.dir_two = PosixPathMock(
            '/home/test_user/tmp/dir_one/dir_two',
            is_dir=True,
            exists=True,
            parent=self.dir_one
        )
        self.path = PosixPathMock(
            '/home/test_user/tmp/dir_one/dir_two/path',
            is_dir=True,
            exists=True,
            parent=self.dir_two
        )

        # patch the normalize_path() function to return self.path_one.
        patcher = patch(
            'flutils.pathutils.normalize_path',
            return_value=self.path
        )
        self.normalize_path = patcher.start()
        self.addCleanup(patcher.stop)

        # patch the exists_as() function to return multiple results.
        patcher = patch(
            'flutils.pathutils.exists_as',
            side_effect=[
                'directory',
                'directory',
                'directory',
                'directory'
            ]
        )
        self.exists_as = patcher.start()
        self.addCleanup(patcher.stop)

        # patch the chown() function.
        patcher = patch(
            'flutils.pathutils.chown',
            return_value=None
        )
        self.chown = patcher.start()
        self.addCleanup(patcher.stop)

        # patch the chmod() function.
        patcher = patch(
            'flutils.pathutils.chmod',
            return_value=None
        )
        self.chmod = patcher.start()
        self.addCleanup(patcher.stop)

    def test_directory_present_exists(self):
        directory_present(self.path.as_posix())
        self.normalize_path.assert_called_with(self.path.as_posix())
        self.path.mkdir.assert_not_called()
        self.dir_two.mkdir.assert_not_called()
        self.dir_one.mkdir.assert_not_called()
        self.tmp.mkdir.assert_not_called()
        self.chmod.assert_called_once_with(self.path, mode_dir=0o700)
        self.chown.assert_called_once_with(self.path, user=None, group=None)


class TestDirectoryPresentGlobError(unittest.TestCase):

    def setUp(self):
        #  /home/test_user/tmp
        #  │
        #  └── dir_one
        #      │
        #      └── dir_two
        #          │
        #          └── **
        #
        self.tmp = PosixPathMock(
            '/home/test_user/tmp',
            is_dir=True,
            exists=True
        )
        self.dir_one = PosixPathMock(
            '/home/test_user/tmp/dir_one',
            is_dir=True,
            exists=True,
            parent=self.tmp,
        )
        self.dir_two = PosixPathMock(
            '/home/test_user/tmp/dir_one/dir_two',
            is_dir=True,
            exists=True,
            parent=self.dir_one
        )
        self.path = PosixPathMock(
            '/home/test_user/tmp/dir_one/dir_two/**',
            is_dir=False,
            exists=False,
            parent=self.dir_two
        )

        # patch the normalize_path() function to return self.path_one.
        patcher = patch(
            'flutils.pathutils.normalize_path',
            return_value=self.path
        )
        self.normalize_path = patcher.start()
        self.addCleanup(patcher.stop)

        # patch the exists_as() function to return multiple results.
        patcher = patch(
            'flutils.pathutils.exists_as',
            side_effect=[
                '',
                'directory',
                'directory',
                'directory'
            ]
        )
        self.exists_as = patcher.start()
        self.addCleanup(patcher.stop)

        # patch the chown() function.
        patcher = patch(
            'flutils.pathutils.chown',
            return_value=None
        )
        self.chown = patcher.start()
        self.addCleanup(patcher.stop)

        # patch the chmod() function.
        patcher = patch(
            'flutils.pathutils.chmod',
            return_value=None
        )
        self.chmod = patcher.start()
        self.addCleanup(patcher.stop)

    def test_directory_present_glob_error(self):
        self.assertRaises(ValueError, directory_present, self.path.as_posix())
        self.normalize_path.assert_called_with(self.path.as_posix())
        self.path.mkdir.assert_not_called()
        self.dir_two.mkdir.assert_not_called()
        self.dir_one.mkdir.assert_not_called()
        self.tmp.mkdir.assert_not_called()
        self.chmod.assert_not_called()
        self.chown.assert_not_called()


class TestDirectoryPresentAbsoluteError(unittest.TestCase):

    def setUp(self):
        self.path = PosixPathMock(
            'home/test_user/tmp/dir_one/dir_two',
            exists=False,
        )

        # patch the normalize_path() function to return self.path_one.
        patcher = patch(
            'flutils.pathutils.normalize_path',
            return_value=self.path
        )
        self.normalize_path = patcher.start()
        self.addCleanup(patcher.stop)

        # patch the exists_as() function to return multiple results.
        patcher = patch(
            'flutils.pathutils.exists_as',
            side_effect=[
                '',
                ''
            ]
        )
        self.exists_as = patcher.start()
        self.addCleanup(patcher.stop)

        # patch the chown() function.
        patcher = patch(
            'flutils.pathutils.chown',
            return_value=None
        )
        self.chown = patcher.start()
        self.addCleanup(patcher.stop)

        # patch the chmod() function.
        patcher = patch(
            'flutils.pathutils.chmod',
            return_value=None
        )
        self.chmod = patcher.start()
        self.addCleanup(patcher.stop)

    def test_directory_present_absolute_error(self):
        self.assertRaises(ValueError, directory_present, self.path.as_posix())
        self.normalize_path.assert_called_with(self.path.as_posix())
        self.path.mkdir.assert_not_called()
        self.chmod.assert_not_called()
        self.chown.assert_not_called()


class TestDirectoryPresentFileError(unittest.TestCase):

    def setUp(self):
        #  /home/test_user/tmp
        #  │
        #  └── path
        #
        self.tmp = PosixPathMock(
            '/home/test_user/tmp',
            is_dir=True,
            exists=True
        )
        self.path = PosixPathMock(
            '/home/test_user/tmp/path',
            is_file=True,
            exists=True,
            parent=self.tmp
        )

        # patch the normalize_path() function to return self.path_one.
        patcher = patch(
            'flutils.pathutils.normalize_path',
            return_value=self.path
        )
        self.normalize_path = patcher.start()
        self.addCleanup(patcher.stop)

        # patch the exists_as() function to return multiple results.
        patcher = patch(
            'flutils.pathutils.exists_as',
            side_effect=[
                'file',
                'directory'
            ]
        )
        self.exists_as = patcher.start()
        self.addCleanup(patcher.stop)

        # patch the chown() function.
        patcher = patch(
            'flutils.pathutils.chown',
            return_value=None
        )
        self.chown = patcher.start()
        self.addCleanup(patcher.stop)

        # patch the chmod() function.
        patcher = patch(
            'flutils.pathutils.chmod',
            return_value=None
        )
        self.chmod = patcher.start()
        self.addCleanup(patcher.stop)

    def test_directory_present_file_error(self):
        self.assertRaises(
            FileExistsError,
            directory_present,
            self.path.as_posix()
        )
        self.normalize_path.assert_called_with(self.path.as_posix())
        self.path.mkdir.assert_not_called()
        self.tmp.mkdir.assert_not_called()
        self.chmod.assert_not_called()
        self.chown.assert_not_called()


class TestDirectoryPresentBlockDeviceError(unittest.TestCase):

    def setUp(self):
        #  /home/test_user/tmp
        #  │
        #  └── path
        #
        self.tmp = PosixPathMock(
            '/home/test_user/tmp',
            is_dir=True,
            exists=True
        )
        self.path = PosixPathMock(
            '/home/test_user/tmp/path',
            is_block_device=True,
            exists=False,
            parent=self.tmp
        )

        # patch the normalize_path() function to return self.path_one.
        patcher = patch(
            'flutils.pathutils.normalize_path',
            return_value=self.path
        )
        self.normalize_path = patcher.start()
        self.addCleanup(patcher.stop)

        # patch the exists_as() function to return multiple values.
        patcher = patch(
            'flutils.pathutils.exists_as',
            side_effect=[
                'block device',
                'directory'
            ]
        )
        self.exists_as = patcher.start()
        self.addCleanup(patcher.stop)

        # patch the chown() function.
        patcher = patch(
            'flutils.pathutils.chown',
            return_value=None
        )
        self.chown = patcher.start()
        self.addCleanup(patcher.stop)

        # patch the chmod() function.
        patcher = patch(
            'flutils.pathutils.chmod',
            return_value=None
        )
        self.chmod = patcher.start()
        self.addCleanup(patcher.stop)

    def test_directory_present_block_device_error(self):
        self.assertRaises(
            FileExistsError,
            directory_present,
            self.path.as_posix()
        )
        self.normalize_path.assert_called_with(self.path.as_posix())
        self.path.mkdir.assert_not_called()
        self.tmp.mkdir.assert_not_called()
        self.chmod.assert_not_called()
        self.chown.assert_not_called()


class TestDirectoryPresentCharDeviceError(unittest.TestCase):

    def setUp(self):
        #  /home/test_user/tmp
        #  │
        #  └── path
        #
        self.tmp = PosixPathMock(
            '/home/test_user/tmp',
            is_dir=True,
            exists=True
        )
        self.path = PosixPathMock(
            '/home/test_user/tmp/path',
            is_char_device=True,
            exists=False,
            parent=self.tmp
        )

        # patch the normalize_path() function to return self.path_one.
        patcher = patch(
            'flutils.pathutils.normalize_path',
            return_value=self.path
        )
        self.normalize_path = patcher.start()
        self.addCleanup(patcher.stop)

        # patch the exists_as() function to return multiple values.
        patcher = patch(
            'flutils.pathutils.exists_as',
            side_effect=[
                'char device',
                'directory'
            ]
        )
        self.exists_as = patcher.start()
        self.addCleanup(patcher.stop)

        # patch the chown() function.
        patcher = patch(
            'flutils.pathutils.chown',
            return_value=None
        )
        self.chown = patcher.start()
        self.addCleanup(patcher.stop)

        # patch the chmod() function.
        patcher = patch(
            'flutils.pathutils.chmod',
            return_value=None
        )
        self.chmod = patcher.start()
        self.addCleanup(patcher.stop)

    def test_directory_present_char_device_error(self):
        self.assertRaises(
            FileExistsError,
            directory_present,
            self.path.as_posix()
        )
        self.normalize_path.assert_called_with(self.path.as_posix())
        self.path.mkdir.assert_not_called()
        self.tmp.mkdir.assert_not_called()
        self.chmod.assert_not_called()
        self.chown.assert_not_called()


class TestDirectoryPresentFifoError(unittest.TestCase):

    def setUp(self):
        #  /home/test_user/tmp
        #  │
        #  └── path
        #
        self.tmp = PosixPathMock(
            '/home/test_user/tmp',
            is_dir=True,
            exists=True
        )
        self.path = PosixPathMock(
            '/home/test_user/tmp/path',
            is_fifo=True,
            exists=False,
            parent=self.tmp
        )

        # patch the normalize_path() function to return self.path_one.
        patcher = patch(
            'flutils.pathutils.normalize_path',
            return_value=self.path
        )
        self.normalize_path = patcher.start()
        self.addCleanup(patcher.stop)

        # patch the exists_as() function to return mutiple values.
        patcher = patch(
            'flutils.pathutils.exists_as',
            side_effect=[
                'FIFO',
                'directory'
            ]
        )
        self.exists_as = patcher.start()
        self.addCleanup(patcher.stop)

        # patch the chown() function.
        patcher = patch(
            'flutils.pathutils.chown',
            return_value=None
        )
        self.chown = patcher.start()
        self.addCleanup(patcher.stop)

        # patch the chmod() function.
        patcher = patch(
            'flutils.pathutils.chmod',
            return_value=None
        )
        self.chmod = patcher.start()
        self.addCleanup(patcher.stop)

    def test_directory_present_fifo_error(self):
        self.assertRaises(
            FileExistsError,
            directory_present,
            self.path.as_posix()
        )
        self.normalize_path.assert_called_with(self.path.as_posix())
        self.path.mkdir.assert_not_called()
        self.tmp.mkdir.assert_not_called()
        self.chmod.assert_not_called()
        self.chown.assert_not_called()


class TestDirectoryPresentSocketError(unittest.TestCase):

    def setUp(self):
        #  /home/test_user/tmp
        #  │
        #  └── path
        #
        self.tmp = PosixPathMock(
            '/home/test_user/tmp',
            is_dir=True,
            exists=True
        )
        self.path = PosixPathMock(
            '/home/test_user/tmp/path',
            is_socket=True,
            exists=False,
            parent=self.tmp
        )

        # patch the normalize_path() function to return self.path_one.
        patcher = patch(
            'flutils.pathutils.normalize_path',
            return_value=self.path
        )
        self.normalize_path = patcher.start()
        self.addCleanup(patcher.stop)

        # patch the exists_as() function to return multiple values.
        patcher = patch(
            'flutils.pathutils.exists_as',
            side_effect=[
                'socket',
                'directory'
            ]
        )
        self.exists_as = patcher.start()
        self.addCleanup(patcher.stop)

        # patch the chown() function.
        patcher = patch(
            'flutils.pathutils.chown',
            return_value=None
        )
        self.chown = patcher.start()
        self.addCleanup(patcher.stop)

        # patch the chmod() function.
        patcher = patch(
            'flutils.pathutils.chmod',
            return_value=None
        )
        self.chmod = patcher.start()
        self.addCleanup(patcher.stop)

    def test_directory_present_socket_error(self):
        self.assertRaises(
            FileExistsError,
            directory_present,
            self.path.as_posix()
        )
        self.normalize_path.assert_called_with(self.path.as_posix())
        self.path.mkdir.assert_not_called()
        self.tmp.mkdir.assert_not_called()
        self.chmod.assert_not_called()
        self.chown.assert_not_called()


class TestDirectoryPresentParentFileError(unittest.TestCase):

    def setUp(self):
        #  /home/test_user/tmp
        #  │
        #  └── path
        #
        self.tmp = PosixPathMock(
            '/home/test_user/tmp',
            is_file=True,
            exists=True
        )
        self.path = PosixPathMock(
            '/home/test_user/tmp/path',
            exists=False,
            parent=self.tmp
        )

        # patch the normalize_path() function to return self.path_one.
        patcher = patch(
            'flutils.pathutils.normalize_path',
            return_value=self.path
        )
        self.normalize_path = patcher.start()
        self.addCleanup(patcher.stop)

        # patch the exists_as() function to return multiple results.
        patcher = patch(
            'flutils.pathutils.exists_as',
            side_effect=[
                '',
                'file'
            ]
        )
        self.exists_as = patcher.start()
        self.addCleanup(patcher.stop)

        # patch the chown() function.
        patcher = patch(
            'flutils.pathutils.chown',
            return_value=None
        )
        self.chown = patcher.start()
        self.addCleanup(patcher.stop)

        # patch the chmod() function.
        patcher = patch(
            'flutils.pathutils.chmod',
            return_value=None
        )
        self.chmod = patcher.start()
        self.addCleanup(patcher.stop)

    def test_directory_present_parent_file_error(self):
        self.assertRaises(
            FileExistsError,
            directory_present,
            self.path.as_posix()
        )
        self.normalize_path.assert_called_with(self.path.as_posix())
        self.path.mkdir.assert_not_called()
        self.tmp.mkdir.assert_not_called()
        self.chmod.assert_not_called()
        self.chown.assert_not_called()


class TestDirectoryPresentParentBlockDeviceError(unittest.TestCase):

    def setUp(self):
        #  /home/test_user/tmp
        #  │
        #  └── path
        #
        self.tmp = PosixPathMock(
            '/home/test_user/tmp',
            is_block_device=True,
            exists=False
        )
        self.path = PosixPathMock(
            '/home/test_user/tmp/path',
            exists=False,
            parent=self.tmp
        )

        # patch the normalize_path() function to return self.path_one.
        patcher = patch(
            'flutils.pathutils.normalize_path',
            return_value=self.path
        )
        self.normalize_path = patcher.start()
        self.addCleanup(patcher.stop)

        # patch the exists_as() function to return multiple results.
        patcher = patch(
            'flutils.pathutils.exists_as',
            side_effect=[
                '',
                'block device'
            ]
        )
        self.exists_as = patcher.start()
        self.addCleanup(patcher.stop)

        # patch the chown() function.
        patcher = patch(
            'flutils.pathutils.chown',
            return_value=None
        )
        self.chown = patcher.start()
        self.addCleanup(patcher.stop)

        # patch the chmod() function.
        patcher = patch(
            'flutils.pathutils.chmod',
            return_value=None
        )
        self.chmod = patcher.start()
        self.addCleanup(patcher.stop)

    def test_directory_present_parent_block_device_error(self):
        self.assertRaises(
            FileExistsError,
            directory_present,
            self.path.as_posix()
        )
        self.normalize_path.assert_called_with(self.path.as_posix())
        self.path.mkdir.assert_not_called()
        self.tmp.mkdir.assert_not_called()
        self.chmod.assert_not_called()
        self.chown.assert_not_called()


class TestDirectoryPresentParentCharDeviceError(unittest.TestCase):

    def setUp(self):
        #  /home/test_user/tmp
        #  │
        #  └── path
        #
        self.tmp = PosixPathMock(
            '/home/test_user/tmp',
            is_char_device=True,
            exists=False
        )
        self.path = PosixPathMock(
            '/home/test_user/tmp/path',
            exists=False,
            parent=self.tmp
        )

        # patch the normalize_path() function to return self.path_one.
        patcher = patch(
            'flutils.pathutils.normalize_path',
            return_value=self.path
        )
        self.normalize_path = patcher.start()
        self.addCleanup(patcher.stop)

        # patch the exists_as() function to return multiple results.
        patcher = patch(
            'flutils.pathutils.exists_as',
            side_effect=[
                '',
                'char device'
            ]
        )
        self.exists_as = patcher.start()
        self.addCleanup(patcher.stop)

        # patch the chown() function.
        patcher = patch(
            'flutils.pathutils.chown',
            return_value=None
        )
        self.chown = patcher.start()
        self.addCleanup(patcher.stop)

        # patch the chmod() function.
        patcher = patch(
            'flutils.pathutils.chmod',
            return_value=None
        )
        self.chmod = patcher.start()
        self.addCleanup(patcher.stop)

    def test_directory_present_parent_char_device_error(self):
        self.assertRaises(
            FileExistsError,
            directory_present,
            self.path.as_posix()
        )
        self.normalize_path.assert_called_with(self.path.as_posix())
        self.path.mkdir.assert_not_called()
        self.tmp.mkdir.assert_not_called()
        self.chmod.assert_not_called()
        self.chown.assert_not_called()


class TestDirectoryPresentParentFifoError(unittest.TestCase):

    def setUp(self):
        #  /home/test_user/tmp
        #  │
        #  └── path
        #
        self.tmp = PosixPathMock(
            '/home/test_user/tmp',
            is_fifo=True,
            exists=False
        )
        self.path = PosixPathMock(
            '/home/test_user/tmp/path',
            exists=False,
            parent=self.tmp
        )

        # patch the normalize_path() function to return self.path_one.
        patcher = patch(
            'flutils.pathutils.normalize_path',
            return_value=self.path
        )
        self.normalize_path = patcher.start()
        self.addCleanup(patcher.stop)

        # patch the exists_as() function to return multiple results.
        patcher = patch(
            'flutils.pathutils.exists_as',
            side_effect=[
                '',
                'FIFO'
            ]
        )
        self.exists_as = patcher.start()
        self.addCleanup(patcher.stop)

        # patch the chown() function.
        patcher = patch(
            'flutils.pathutils.chown',
            return_value=None
        )
        self.chown = patcher.start()
        self.addCleanup(patcher.stop)

        # patch the chmod() function.
        patcher = patch(
            'flutils.pathutils.chmod',
            return_value=None
        )
        self.chmod = patcher.start()
        self.addCleanup(patcher.stop)

    def test_directory_present_parent_fifo_error(self):
        self.assertRaises(
            FileExistsError,
            directory_present,
            self.path.as_posix()
        )
        self.normalize_path.assert_called_with(self.path.as_posix())
        self.path.mkdir.assert_not_called()
        self.tmp.mkdir.assert_not_called()
        self.chmod.assert_not_called()
        self.chown.assert_not_called()


class TestDirectoryPresentParentSocketError(unittest.TestCase):

    def setUp(self):
        #  /home/test_user/tmp
        #  │
        #  └── path
        #
        self.tmp = PosixPathMock(
            '/home/test_user/tmp',
            is_socket=True,
            exists=False
        )
        self.path = PosixPathMock(
            '/home/test_user/tmp/path',
            exists=False,
            parent=self.tmp
        )

        # patch the normalize_path() function to return self.path_one.
        patcher = patch(
            'flutils.pathutils.normalize_path',
            return_value=self.path
        )
        self.normalize_path = patcher.start()
        self.addCleanup(patcher.stop)

        # patch the exists_as() function to return multiple results.
        patcher = patch(
            'flutils.pathutils.exists_as',
            side_effect=[
                '',
                'socket'
            ]
        )
        self.exists_as = patcher.start()
        self.addCleanup(patcher.stop)

        # patch the chown() function.
        patcher = patch(
            'flutils.pathutils.chown',
            return_value=None
        )
        self.chown = patcher.start()
        self.addCleanup(patcher.stop)

        # patch the chmod() function.
        patcher = patch(
            'flutils.pathutils.chmod',
            return_value=None
        )
        self.chmod = patcher.start()
        self.addCleanup(patcher.stop)

    def test_directory_present_parent_socket_error(self):
        self.assertRaises(
            FileExistsError,
            directory_present,
            self.path.as_posix()
        )
        self.normalize_path.assert_called_with(self.path.as_posix())
        self.path.mkdir.assert_not_called()
        self.tmp.mkdir.assert_not_called()
        self.chmod.assert_not_called()
        self.chown.assert_not_called()
