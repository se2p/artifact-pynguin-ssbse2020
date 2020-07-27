# pylint: disable=E0611,E0401
import errno
import sys
import unittest
from io import BytesIO
from unittest.mock import (
    MagicMock,
    PropertyMock,
    patch,
)

from flutils.cmdutils import run


def _get_different_eio() -> int:
    for x in range(1, 11):
        if x != errno.EIO:
            return x


class TestCmdutilsRun(unittest.TestCase):

    def setUp(self) -> None:
        patcher = patch(
            'flutils.cmdutils.shlex.split',
            return_value=['ls', '-Flap']
        )
        self.shlex_split = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.cmdutils.shutil.which',
            return_value='/bin/bash'
        )
        self.shutil_which = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.cmdutils.sys.stdout',
            spec=sys.stdout
        )
        self.sys_stdout_buffer = patcher.start()
        type(self.sys_stdout_buffer).encoding = PropertyMock(
            return_value='utf-8'
        )
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.cmdutils.sys.stderr',
            new_callable=BytesIO
        )
        self.sys_stderr_buffer = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.cmdutils.shutil.get_terminal_size',
            return_value=(115, 25)
        )
        self.shutil_get_terminal_size = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.cmdutils.pty.openpty',
            side_effect=[(10, 20), (30, 40)]
        )
        self.pty_openpty = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.cmdutils._set_size',
            side_effect=[None, None, None, None]
        )
        self.set_size = patcher.start()
        self.addCleanup(patcher.stop)

        #
        popen_obj = MagicMock()
        type(popen_obj).returncode = PropertyMock(return_value=0)

        patcher = patch('flutils.cmdutils.Popen')
        self.popen = patcher.start()
        # The following sets the return value as popen_obj
        # because Popen(...) is called as a context manager.
        self.popen.return_value.__enter__.return_value = popen_obj
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.cmdutils.os.close',
            side_effect=[None, None, None, None, OSError(), OSError()]
        )
        self.os_close = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.cmdutils.select',
            side_effect=[[(10, 30), None], [(10, 30), None]]
        )
        self.select = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.cmdutils.os.read',
            side_effect=[b'foo\n', b'bar\n', '', '']
        )
        self.os_read = patcher.start()
        self.addCleanup(patcher.stop)

    def test_return_code(self) -> None:
        ret = run(['ls', '-Flap'], force_dimensions=True)
        self.popen.assert_called()
        self.assertEqual(ret, 0)

    def test_bytes_command(self) -> None:
        with self.assertRaises(TypeError):
            run(b'ls -Flap')

    def test_stdout(self) -> None:
        stdout = BytesIO()
        run('ls -Flap', stdout=stdout)
        self.shlex_split.assert_called_once_with('ls -Flap')
        self.assertEqual(stdout.getvalue(), b'foo\n')

    def test_stderr(self) -> None:
        stderr = BytesIO()
        run('ls -Flap', stderr=stderr)
        self.shlex_split.assert_called_once_with('ls -Flap')
        self.assertEqual(stderr.getvalue(), b'bar\n')

    def test_interactive(self) -> None:
        run('ls -Flap', interactive=True)
        self.popen.assert_called_with(
            ['/bin/bash', '-i', '-c', 'ls', '-Flap'],
            stdout=20,
            stderr=40,
            stdin=20,
        )

    def test_encoding(self) -> None:
        run('ls -Flap', encoding='utf-8', stdout=sys.stdout)
        self.popen.assert_called_with(
            ['ls', '-Flap'],
            stdout=20,
            stderr=40,
            stdin=20,
            encoding='utf-8',
        )

    def test_write_error(self) -> None:
        run('ls -Flap', encoding='utf-8')
        self.popen.assert_called_with(
            ['ls', '-Flap'],
            stdout=20,
            stderr=40,
            stdin=20,
            encoding='utf-8',
        )

    def test_errno_eio(self) -> None:
        self.os_read.side_effect = [
            b'foo\n',
            b'bar\n',
            OSError(errno.EIO, 'end of file'),
            OSError(errno.EIO, 'end of file'),
        ]
        ret = run('ls -Flap')
        self.assertEqual(ret, 0)

    def test_different_errno_eio(self) -> None:
        self.os_read.side_effect = [
            OSError(_get_different_eio(), 'an error'),
        ]
        with self.assertRaises(OSError):
            run('ls -Flap')

    def test_missing_bash(self) -> None:
        self.shutil_which.return_value = ''
        with self.assertRaises(RuntimeError):
            run('ls -Flap', interactive=True)
