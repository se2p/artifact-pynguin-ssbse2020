# pylint: disable=E0611,E0401
import unittest
from distutils.version import StrictVersion
from unittest.mock import (
    Mock,
    patch,
)

# noinspection PyProtectedMember
from flutils.packages import (
    _VersionInfo,
    _VersionPart,
    _build_version_info,
)


class TestBuildVersionInfo(unittest.TestCase):

    def test_build_version_info__1(self) -> None:
        arg = '1.2.3'
        exp = _VersionInfo(
            version=arg,
            major=_VersionPart(
                pos=0,
                txt='1',
                num=1,
                pre_txt='',
                pre_num=-1,
                name='major'
            ),
            minor=_VersionPart(
                pos=1,
                txt='2',
                num=2,
                pre_txt='',
                pre_num=-1,
                name='minor'
            ),
            patch=_VersionPart(
                pos=2,
                txt='3',
                num=3,
                pre_txt='',
                pre_num=-1,
                name='patch'
            ),
            pre_pos=-1
        )
        strict_version_obj = Mock(spec=StrictVersion)
        patcher = patch(
            'flutils.packages.StrictVersion',
            autospec=True,
            return_value=strict_version_obj
        )
        strict_version = patcher.start()
        self.addCleanup(patcher.stop)
        patcher = patch(
            'flutils.packages._each_version_part',
            return_value=[exp.major, exp.minor, exp.patch]
        )
        each_version_part = patcher.start()
        self.addCleanup(patcher.stop)
        ret = _build_version_info(arg)
        self.assertEqual(
            ret,
            exp,
            msg=(
                '\n\n'
                '_build_version_info({arg!r})\n\n'
                'expected:\n\n'
                '{exp!r}\n\n'
                'got:\n\n'
                '{ret!r}\n\n'
            ).format(arg=arg, exp=exp, ret=ret)
        )
        strict_version.assert_called_once_with(arg)
        each_version_part.assert_called_once_with(strict_version_obj)

    def test_build_version_info__2(self) -> None:
        arg = '2.6b2'
        exp = _VersionInfo(
            version=arg,
            major=_VersionPart(
                pos=0,
                txt='2',
                num=2,
                pre_txt='',
                pre_num=-1,
                name='major'
            ),
            minor=_VersionPart(
                pos=1,
                txt='6b2',
                num=6,
                pre_txt='b',
                pre_num=2,
                name='minor'
            ),
            patch=_VersionPart(
                pos=2,
                txt='',
                num=0,
                pre_txt='',
                pre_num=-1,
                name='patch'
            ),
            pre_pos=1
        )
        strict_version_obj = Mock(spec=StrictVersion)
        patcher = patch(
            'flutils.packages.StrictVersion',
            autospec=True,
            return_value=strict_version_obj
        )
        strict_version = patcher.start()
        self.addCleanup(patcher.stop)
        patcher = patch(
            'flutils.packages._each_version_part',
            return_value=[exp.major, exp.minor, exp.patch]
        )
        each_version_part = patcher.start()
        self.addCleanup(patcher.stop)
        ret = _build_version_info(arg)
        self.assertEqual(
            ret,
            exp,
            msg=(
                '\n\n'
                '_build_version_info({arg!r})\n\n'
                'expected:\n\n'
                '{exp!r}\n\n'
                'got:\n\n'
                '{ret!r}\n\n'
            ).format(arg=arg, exp=exp, ret=ret)
        )
        strict_version.assert_called_once_with(arg)
        each_version_part.assert_called_once_with(strict_version_obj)

    def test_build_version_info__3(self) -> None:
        arg = '2.10.1a4'
        exp = _VersionInfo(
            version=arg,
            major=_VersionPart(
                pos=0,
                txt='2',
                num=2,
                pre_txt='',
                pre_num=-1,
                name='major'
            ),
            minor=_VersionPart(
                pos=1,
                txt='10',
                num=10,
                pre_txt='',
                pre_num=-1,
                name='minor'
            ),
            patch=_VersionPart(
                pos=2,
                txt='1a4',
                num=1,
                pre_txt='a',
                pre_num=4,
                name='patch'
            ),
            pre_pos=2
        )
        strict_version_obj = Mock(spec=StrictVersion)
        patcher = patch(
            'flutils.packages.StrictVersion',
            autospec=True,
            return_value=strict_version_obj
        )
        strict_version = patcher.start()
        self.addCleanup(patcher.stop)
        patcher = patch(
            'flutils.packages._each_version_part',
            return_value=[exp.major, exp.minor, exp.patch]
        )
        each_version_part = patcher.start()
        self.addCleanup(patcher.stop)
        ret = _build_version_info(arg)
        self.assertEqual(
            ret,
            exp,
            msg=(
                '\n\n'
                '_build_version_info({arg!r})\n\n'
                'expected:\n\n'
                '{exp!r}\n\n'
                'got:\n\n'
                '{ret!r}\n\n'
            ).format(arg=arg, exp=exp, ret=ret)
        )
        strict_version.assert_called_once_with(arg)
        each_version_part.assert_called_once_with(strict_version_obj)

    def test_build_version_info__4(self) -> None:
        args = [
            '1b1',
            '1.2b2.0',
        ]
        for arg in args:
            with self.subTest(arg=arg):
                with self.assertRaises(ValueError):
                    _build_version_info(arg)
