import functools
import getpass
import grp
import os
import pwd
import sys
from collections import deque
from os import PathLike
from pathlib import (
    Path,
    PosixPath,
    WindowsPath,
)
from typing import (
    Deque,
    Generator,
    Optional,
    Union,
    cast,
)


__all__ = [
    'chmod',
    'chown',
    'directory_present',
    'exists_as',
    'find_paths',
    'get_os_group',
    'get_os_user',
    'normalize_path',
    'path_absent',
]


_PATH = Union[
    PathLike,
    PosixPath,
    WindowsPath,
    bytes,
    str,
]

_STR_OR_INT_OR_NONE = Union[
    str,
    int,
    None
]


def chmod(
        path: _PATH,
        mode_file: Optional[int] = None,
        mode_dir: Optional[int] = None,
        include_parent: bool = False
) -> None:
    """Change the mode of a path.

    This function processes the given ``path`` with
    :obj:`~flutils.normalize_path`.

    If the given ``path`` does NOT exist, nothing will be done.

    This function will **NOT** change the mode of:

    - symlinks (symlink targets that are files or directories will be changed)
    - sockets
    - fifo
    - block devices
    - char devices

    Args:
        path (:obj:`str`, :obj:`bytes` or :obj:`Path <pathlib.Path>`):
            The path of the file or directory to have it's mode changed.  This
            value can be a :term:`glob pattern`.
        mode_file (:obj:`int`, optional): The mode applied to the given
            ``path`` that is a file or a symlink target that is a file.
            Defaults to ``0o600``.
        mode_dir (:obj:`int`, optional): The mode applied to the given
            ``path`` that is a directory or a symlink target that is a
            directory. Defaults to ``0o700``.
        include_parent (:obj:`bool`, optional): A value of :obj:`True`` will
            chmod the parent directory of the given ``path`` that contains a
            a :term:`glob pattern`.  Defaults to :obj:`False`.

    :rtype: :obj:`None`

    Examples:
        >>> from flutils.pathutils import chmod
        >>> chmod('~/tmp/flutils.tests.osutils.txt', 0o660)

        Supports a :term:`glob pattern`.  So to recursively change the mode
        of a directory just do:

        >>> chmod('~/tmp/**', mode_file=0o644, mode_dir=0o770)

        To change the mode of a directory's immediate contents:

        >>> chmod('~/tmp/*')

    """

    path = normalize_path(path)

    if mode_file is None:
        mode_file = 0o600

    if mode_dir is None:
        mode_dir = 0o700

    if '*' in path.as_posix():
        try:
            for sub_path in Path().glob(path.as_posix()):
                if sub_path.is_dir() is True:
                    sub_path.chmod(mode_dir)
                elif sub_path.is_file():
                    sub_path.chmod(mode_file)

        # Path().glob() returns an iterator that will
        # raise NotImplementedError if there
        # are no results from the glob pattern.
        except NotImplementedError:
            pass

        else:
            if include_parent is True:
                parent = path.parent
                if parent.is_dir():
                    parent.chmod(mode_dir)
    else:
        if path.exists() is True:
            if path.is_dir():
                path.chmod(mode_dir)
            elif path.is_file():
                path.chmod(mode_file)


def chown(
        path: _PATH,
        user: Optional[str] = None,
        group: Optional[str] = None,
        include_parent: bool = False
) -> None:
    """Change ownership of a path.

    This function processes the given ``path`` with
    :obj:`~flutils.normalize_path`.

    If the given ``path`` does NOT exist, nothing will be done.

    Args:
        path (:obj:`str`, :obj:`bytes` or :obj:`Path <pathlib.Path>`):
            The path of the file or directory that will have it's ownership
            changed.  This value can be a :term:`glob pattern`.
        user (:obj:`str` or :obj:`int`, optional): The "login name" used to set
            the owner of ``path``.  A value of ``'-1'`` will leave the
            owner unchanged.  Defaults to the "login name" of the current user.
        group (:obj:`str` or :obj:`int`, optional): The group name used to set
            the group of ``path``.  A value of ``'-1'`` will leave the
            group unchanged.  Defaults to the current user's group.
        include_parent (:obj:`bool`, optional): A value of :obj:`True` will
            chown the parent directory of the given ``path`` that contains
            a :term:`glob pattern`.  Defaults to :obj:`False`.

    Raises:
        OSError: If the given :obj:`user` does not exist as a "login
            name" for this operating system.
        OSError: If the given :obj:`group` does not exist as a "group
            name" for this operating system.

    :rtype: :obj:`None`

    Examples:
        >>> from flutils.pathutils import chown
        >>> chown('~/tmp/flutils.tests.osutils.txt')

        Supports a :term:`glob pattern`.  So to recursively change the
        ownership of a directory just do:

        >>> chown('~/tmp/**')


        To change ownership of all the directory's immediate contents:

        >>> chown('~/tmp/*', user='foo', group='bar')

    """
    path = normalize_path(path)
    if isinstance(user, str) and user == '-1':
        uid = -1
    else:
        uid = get_os_user(user).pw_uid

    if isinstance(user, str) and group == '-1':
        gid = -1
    else:
        gid = get_os_group(group).gr_gid

    if '*' in path.as_posix():
        try:
            for sub_path in Path().glob(path.as_posix()):
                if sub_path.is_dir() or sub_path.is_file():
                    os.chown(sub_path.as_posix(), uid, gid)
        except NotImplementedError:
            # Path().glob() returns an iterator that will
            # raise NotImplementedError if there
            # are no results from the glob pattern.
            pass
        else:
            if include_parent is True:
                path = path.parent
                if path.is_dir() is True:
                    os.chown(path.as_posix(), uid, gid)
    else:
        if path.exists() is True:
            os.chown(path.as_posix(), uid, gid)


def directory_present(
        path: _PATH,
        mode: Optional[int] = None,
        user: Optional[str] = None,
        group: Optional[str] = None,
) -> Path:
    """Ensure the state of the given :obj:`path` is present and a directory.

    This function processes the given ``path`` with
    :obj:`~flutils.normalize_path`.

    If the given ``path`` does **NOT** exist, it will be created as a
    directory.

    If the parent paths of the given ``path`` do not exist, they will also be
    created with the ``mode``, ``user`` and ``group``.

    If the given ``path`` does exist as a directory, the ``mode``, ``user``,
    and :``group`` will be applied.

    Args:
        path (:obj:`str`, :obj:`bytes` or :obj:`Path <pathlib.Path>`):
            The path of the directory.
        mode (:obj:`int`, optional): The mode applied to the ``path``.
            Defaults to ``0o700``.
        user (:obj:`str` or :obj:`int`, optional): The "login name" used to
            set the owner of the given ``path``.  A value of ``'-1'`` will
            leave the owner unchanged.  Defaults to the "login name" of the
            current user.
        group (:obj:`str` or :obj:`int`, optional): The group name used to set
            the group of the given ``path``.  A value of ``'-1'`` will leave
            the group unchanged.  Defaults to the current user's group.

    Raises:
        ValueError: if the given ``path`` contains a glob pattern.
        ValueError: if the given ``path`` is not an absolute path.
        FileExistsError: if the given ``path`` exists and is not a directory.
        FileExistsError: if a parent of the given ``path`` exists and is
            not a directory.

    :rtype: :obj:`Path <pathlib.Path>`

        * :obj:`PosixPath <pathlib.PosixPath>` or
          :obj:`WindowsPath <pathlib.WindowsPath>` depending on the system.

        .. Note:: :obj:`Path <pathlib.Path>` objects are immutable. Therefore,
           any given ``path`` of type :obj:`Path <pathlib.Path>` will not be
           the same object returned.

    Example:
        >>> from flutils.pathutils import directory_present
        >>> directory_present('~/tmp/test_path')
        PosixPath('/Users/len/tmp/test_path')

    """
    path = normalize_path(path)

    if '*' in path.as_posix():
        raise ValueError(
            'The path: %r must NOT contain any glob patterns.'
            % path.as_posix()
        )
    if path.is_absolute() is False:
        raise ValueError(
            'The path: %r must be an absolute path.  A path is considered '
            'absolute if it has both a root and (if the flavour allows) a '
            'drive.'
            % path.as_posix()
        )

    # Create a queue of paths to be created as directories.
    paths: Deque = deque()

    path_exists_as = exists_as(path)
    if path_exists_as == '':
        paths.append(path)
    elif path_exists_as != 'directory':
        raise FileExistsError(
            'The path: %r can NOT be created as a directory because it '
            'already exists as a %s.' % (path.as_posix(), path_exists_as)
        )

    parent = path.parent
    child = path

    # Traverse the path backwards and add any directories that
    # do no exist to the path queue.
    while child.as_posix() != parent.as_posix():
        parent_exists_as = exists_as(parent)
        if parent_exists_as == '':
            paths.appendleft(parent)
            child = parent
            parent = parent.parent
        elif parent_exists_as == 'directory':
            break
        else:
            raise FileExistsError(
                'Unable to create the directory: %r because the'
                'parent path: %r exists as a %s.'
                % (path.as_posix, parent.as_posix(), parent_exists_as)
            )

    if mode is None:
        mode = 0o700

    if paths:
        for build_path in paths:
            build_path.mkdir(mode=mode)
            chown(build_path, user=user, group=group)
    else:
        # The given path already existed only need to do a chown.
        chmod(path, mode_dir=mode)
        chown(path, user=user, group=group)

    return path


def exists_as(path: _PATH) -> str:
    """Return a string describing the file type if it exists.

    This function processes the given ``path`` with
    :obj:`~flutils.normalize_path`.

    Args:
        path (:obj:`str`, :obj:`bytes` or :obj:`Path <pathlib.Path>`):
            The path to check for existence.

    :rtype:
        :obj:`str`

        * ``''`` (empty string): if the given ``path`` does NOT exist; or,
          is a broken symbolic link; or, other errors (such as permission
          errors) are propagated.
        * ``'directory'``: if the given ``path`` points to a directory or
          is a symbolic link pointing to a directory.
        * ``'file'``: if the given ``path`` points to a regular file or is a
          symbolic link pointing to a regular file.
        * ``'block device'``: if the given ``path`` points to a block device or
          is a symbolic link pointing to a block device.
        * ``'char device'``: if the given ``path`` points to a character device
          or is a symbolic link pointing to a character device.
        * ``'FIFO'``: if the given ``path`` points to a FIFO or is a symbolic
          link pointing to a FIFO.
        * ``'socket'``: if the given ``path`` points to a Unix socket or is a
          symbolic link pointing to a Unix socket.

    Example:
        >>> from flutils.pathutils import exists_as
        >>> exists_as('~/tmp')
        'directory'
    """
    path = normalize_path(path)

    if path.is_dir():
        return 'directory'
    if path.is_file():
        return 'file'
    if path.is_block_device():
        return 'block device'
    if path.is_char_device():
        return 'char device'
    if path.is_fifo():
        return 'FIFO'
    if path.is_socket():
        return 'socket'
    return ''


def find_paths(
        pattern: _PATH
) -> Generator[Path, None, None]:
    """Find all paths that match the given :term:`glob pattern`.

    This function pre-processes the given ``pattern`` with
    :obj:`~flutils.normalize_path`.

    Args:
        pattern (:obj:`str`, :obj:`bytes` or :obj:`Path <pathlib.Path>`):
            The path to find; which may contain a :term:`glob pattern`.

    :rtype:
        :obj:`Generator <typing.Generator>`

    Yields:
        :obj:`pathlib.PosixPath` or :obj:`pathlib.WindowsPath`

    Example:
        >>> from flutils.pathutils import find_paths
        >>> list(find_paths('~/tmp/*'))
        [PosixPath('/home/test_user/tmp/file_one'),
        PosixPath('/home/test_user/tmp/dir_one')]

    """
    pattern = normalize_path(pattern)
    search = pattern.as_posix()[len(pattern.anchor):]
    yield from Path(pattern.anchor).glob(search)


def get_os_group(name: _STR_OR_INT_OR_NONE = None) -> grp.struct_group:
    """Get an operating system group object.

    Args:
        name (:obj:`str` or :obj:`int`, optional): The "group name" or ``gid``.
            Defaults to the current users's group.

    Raises:
        OSError: If the given ``name`` does not exist as a "group
            name" for this operating system.
        OSError: If the given ``name`` is a ``gid`` and it does not
            exist.

    :rtype:
        :obj:`struct_group <grp>`

        * A tuple like object.

    Example:
        >>> from flutils.pathutils import get_os_group
        >>> get_os_group('bar')
        grp.struct_group(gr_name='bar', gr_passwd='*', gr_gid=2001,
        gr_mem=['foo'])
    """
    if name is None:
        name = get_os_user().pw_gid
        name = cast(int, name)
    if isinstance(name, int):
        try:
            return grp.getgrgid(name)
        except KeyError:
            raise OSError(
                'The given gid: %r, is not a valid gid for this operating '
                'system.' % name
            )
    try:
        return grp.getgrnam(name)
    except KeyError:
        raise OSError(
            'The given name: %r, is not a valid "group name" '
            'for this operating system.' % name
        )


def get_os_user(name: _STR_OR_INT_OR_NONE = None) -> pwd.struct_passwd:
    """Return an user object representing an operating system user.

    Args:
        name (:obj:`str` or :obj:`int`, optional): The "login name" or
            ``uid``.  Defaults to the current user's "login name".
    Raises:
        OSError: If the given ``name`` does not exist as a "login
            name" for this operating system.
        OSError: If the given ``name`` is an ``uid`` and it does not
            exist.

    :rtype:
        :obj:`struct_passwd <pwd>`

        * A tuple like object.

    Example:
        >>> from flutils.pathutils import get_os_user
        >>> get_os_user('foo')
        pwd.struct_passwd(pw_name='foo', pw_passwd='********', pw_uid=1001,
        pw_gid=2001, pw_gecos='Foo Bar', pw_dir='/home/foo',
        pw_shell='/usr/local/bin/bash')
    """
    if isinstance(name, int):
        try:
            return pwd.getpwuid(name)
        except KeyError:
            raise OSError(
                'The given uid: %r, is not a valid uid for this operating '
                'system.' % name
            )
    if name is None:
        name = getpass.getuser()
    try:
        return pwd.getpwnam(name)
    except KeyError:
        raise OSError(
            'The given name: %r, is not a valid "login name" '
            'for this operating system.' % name
        )


@functools.singledispatch
def normalize_path(path: _PATH) -> Path:
    """Normalize a given path.

    The given ``path`` will be normalized in the following process.

    #. :obj:`bytes` will be converted to a :obj:`str` using the encoding
       given by :obj:`getfilesystemencoding() <sys.getfilesystemencoding>`.
    #. :obj:`PosixPath <pathlib.PosixPath>` and
       :obj:`WindowsPath <pathlib.WindowsPath>` will be converted
       to a :obj:`str` using the :obj:`as_posix() <pathlib.PurePath.as_posix>`
       method.
    #. An initial component of ``~`` will be replaced by that user’s
       home directory.
    #. Any environment variables will be expanded.
    #. Non absolute paths will have the current working directory from
       :obj:`os.getcwd() <os.cwd>`prepended.  If needed, use
       :obj:`os.chdir() <os.chdir>` to change the current working directory
       before calling this function.
    #. Redundant separators and up-level references will be normalized, so
       that ``A//B``, ``A/B/``, ``A/./B`` and ``A/foo/../B`` all become
       ``A/B``.

    Args:
        path (:obj:`str`, :obj:`bytes` or :obj:`Path <pathlib.Path>`):
            The path to be normalized.

    :rtype:
        :obj:`Path <pathlib.Path>`

        * :obj:`PosixPath <pathlib.PosixPath>` or
          :obj:`WindowsPath <pathlib.WindowsPath>` depending on the system.

        .. Note:: :obj:`Path <pathlib.Path>` objects are immutable. Therefore,
           any given ``path`` of type :obj:`Path <pathlib.Path>` will not be
           the same object returned.

    Example:

        >>> from flutils.pathutils import normalize_path
        >>> normalize_path('~/tmp/foo/../bar')
        PosixPath('/home/test_user/tmp/bar')

    """
    path = cast(PathLike, path)
    path = os.path.expanduser(path)
    path = cast(PathLike, path)
    path = os.path.expandvars(path)
    path = cast(PathLike, path)
    if os.path.isabs(path) is False:
        path = os.path.join(os.getcwd(), path)
    path = cast(PathLike, path)
    path = os.path.normpath(path)
    path = cast(PathLike, path)
    path = os.path.normcase(path)
    path = cast(PathLike, path)
    return Path(path)


@normalize_path.register(bytes)
def _normalize_path_bytes(path: bytes) -> Path:
    out: str = path.decode(sys.getfilesystemencoding())
    return normalize_path(out)


@normalize_path.register(Path)
def _normalize_path_pathlib(path: Path) -> Path:
    return normalize_path(path.as_posix())


def path_absent(
        path: _PATH,
) -> None:
    """Ensure the given ``path`` does **NOT** exist.

    *New in version 0.4.*

    If the given ``path`` does exist, it will be deleted.

    If the given ``path`` is a directory, this function will
    recursively delete all of the directory's contents.

    This function processes the given ``path`` with
    :obj:`~flutils.normalize_path`.

    Args:
        path (:obj:`str`, :obj:`bytes` or :obj:`Path <pathlib.Path>`):
            The path to remove.

    :rtype: :obj:`None`

    Example:
        >>> from flutils.pathutils import path_absent
        >>> path_absent('~/tmp/test_path')

    """
    path = normalize_path(path)
    path = path.as_posix()
    path = cast(str, path)
    if os.path.exists(path):
        if os.path.islink(path):
            os.unlink(path)
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path, topdown=False):
                for name in files:
                    p = os.path.join(root, name)
                    if os.path.isfile(p) or os.path.islink(p):
                        os.unlink(p)
                for name in dirs:
                    p = os.path.join(root, name)
                    if os.path.islink(p):
                        os.unlink(p)
                    else:
                        os.rmdir(p)
            if os.path.isdir(path):
                os.rmdir(path)
        else:
            os.unlink(path)
