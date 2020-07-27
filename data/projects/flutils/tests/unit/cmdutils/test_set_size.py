# pylint: disable=E0611,E0401
import termios
import unittest
from unittest.mock import (
    MagicMock,
    patch,
)

# noinspection PyStatementEffect
from flutils.cmdutils import _set_size


class TestCmdutilsSetSize(unittest.TestCase):

    def setUp(self) -> None:
        patcher = patch(
            'flutils.cmdutils.struct.pack',
            autospec=True,
            return_value=555
        )
        self.struct_pack: MagicMock = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.cmdutils.fcntl.ioctl',
            autospec=True
        )
        self.fcntl_ioctl: MagicMock = patcher.start()
        self.addCleanup(patcher.stop)

    def test_set_size__1(self) -> None:
        ret = _set_size(22, 100, 50)
        self.assertEqual(ret, None)

    def test_set_size__2(self) -> None:
        _set_size(22, 100, 50)
        self.struct_pack.assert_called_once_with(
            'HHHH',
            50,
            100,
            0,
            0
        )

    def test_set_size__3(self) -> None:
        _set_size(22, 100, 50)
        self.fcntl_ioctl.assert_called_once_with(
            22,
            termios.TIOCSWINSZ,
            555
        )
