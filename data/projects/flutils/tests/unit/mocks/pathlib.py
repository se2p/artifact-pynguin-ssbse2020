from unittest.mock import MagicMock


class PosixPathMock:

    """Mock of pathlib.PosixPath class."""

    def __init__(self, path, **kwargs):
        if isinstance(path, PosixPathMock):
            path = path.as_posix()
        self._path = path
        self.kwargs = kwargs
        self.glob_data = self.kwargs.get('glob', list())
        self._as_posix_ = None
        self._expanduser_ = None
        self._parent_ = self.kwargs.get('parent', None)
        self._is_dir_ = None
        self._is_file_ = None
        self._is_symlink_ = None
        self._is_socket_ = None
        self._is_fifo_ = None
        self._is_block_device_ = None
        self._is_char_device_ = None
        self._is_absolute_ = None
        self._exists_ = None
        self._mkdir_ = None
        self._chmod_ = None
        self._glob_ = None

    def __repr__(self):
        return "PosixPathMock({!r})".format(self._path)

    @property
    def as_posix(self):
        if self._as_posix_ is None:
            self._as_posix_ = MagicMock(return_value=self._path)
        return self._as_posix_

    @property
    def expanduser(self):
        if self._expanduser_ is None:
            self._expanduser_ = MagicMock(return_value=self._path)
            if self._path.startswith('~/'):
                self._expanduser_ = MagicMock(
                    return_value=PosixPathMock(
                        self._path.replace('~/', '/home/test_user/')
                    )
                )
        return self._expanduser_

    @property
    def parent(self):
        if self._parent_ is None:
            self._parent_ = PosixPathMock(
                '/'.join(self._path.split('/')[:-1]),
                is_dir=True,
                check=True
            )
        return self._parent_

    @property
    def is_dir(self):
        if self._is_dir_ is None:
            self._is_dir_ = MagicMock(
                return_value=self.kwargs.get('is_dir', False)
            )
        return self._is_dir_

    @property
    def is_file(self):
        if self._is_file_ is None:
            self._is_file_ = MagicMock(
                return_value=self.kwargs.get('is_file', False)
            )
        return self._is_file_

    @property
    def is_symlink(self):
        if self._is_symlink_ is None:
            self._is_symlink_ = MagicMock(
                return_value=self.kwargs.get('is_symlink', False)
            )
        return self._is_symlink_

    @property
    def is_socket(self):
        if self._is_socket_ is None:
            self._is_socket_ = MagicMock(
                return_value=self.kwargs.get('is_socket', False)
            )
        return self._is_socket_

    @property
    def is_fifo(self):
        if self._is_fifo_ is None:
            self._is_fifo_ = MagicMock(
                return_value=self.kwargs.get('is_fifo', False)
            )
        return self._is_fifo_

    @property
    def is_block_device(self):
        if self._is_block_device_ is None:
            self._is_block_device_ = MagicMock(
                return_value=self.kwargs.get('is_block_device', False)
            )
        return self._is_block_device_

    @property
    def is_char_device(self):
        if self._is_char_device_ is None:
            self._is_char_device_ = MagicMock(
                return_value=self.kwargs.get('is_char_device', False)
            )
        return self._is_char_device_

    @property
    def is_absolute(self):
        if self._is_absolute_ is None:
            self._is_absolute_ = MagicMock(
                return_value=self._path.startswith('/')
            )
        return self._is_absolute_

    @property
    def exists(self):
        if self._exists_ is None:
            self._exists_ = MagicMock(
                return_value=self.kwargs.get('exists', True)
            )
        return self._exists_

    @property
    def chmod(self):
        if self._chmod_ is None:
            self._chmod_ = MagicMock(return_value=None)
        return self._chmod_

    @property
    def mkdir(self):
        if self._mkdir_ is None:
            self._mkdir_ = MagicMock(return_value=None)
        return self._mkdir_

    @property
    def glob(self):
        if self._glob_ is None:
            self._glob_ = MagicMock(
                return_value=self._glob_results
            )
        return self._glob_

    @property
    def _glob_results(self):
        paths = self.kwargs.get('glob', list())
        if not paths:
            raise NotImplementedError("Non-relative patterns are unsupported")
        for p in paths:
            yield p


def Path(name, **kwargs):
    """Mock of the pathlib.Path function."""
    return PosixPathMock(name, **kwargs)
