# pylint: disable=E0611,E0401
import unittest
from distutils.version import StrictVersion
from unittest.mock import (
    Mock,
    PropertyMock,
)

# noinspection PyProtectedMember
from flutils.packages import (
    _VersionPart,
    _each_version_part,
)


class TestEachPart(unittest.TestCase):

    def test_each_part__1(self) -> None:
        ver_obj = Mock(spec=StrictVersion)
        type(ver_obj).__repr__ = Mock(
            return_value="MockedStrictVersion('1.2.3')"
        )
        type(ver_obj).version = PropertyMock(return_value=(1, 2, 3))
        type(ver_obj).prerelease = PropertyMock(return_value=None)
        exp = [
            _VersionPart(
                pos=0,
                txt='1',
                num=1,
                pre_txt='',
                pre_num=-1,
                name='major'
            ),
            _VersionPart(
                pos=1,
                txt='2',
                num=2,
                pre_txt='',
                pre_num=-1,
                name='minor'
            ),
            _VersionPart(
                pos=2,
                txt='3',
                num=3,
                pre_txt='',
                pre_num=-1,
                name='patch'
            ),
        ]
        ret = list(_each_version_part(ver_obj))
        self.assertEqual(
            ret,
            exp,
            msg=(
                '\n\n'
                '_each_version_part({ver_obj!s})\n\n'
                'expected:\n\n'
                '{exp!r}\n\n'
                'got:\n\n'
                '{ret!r}\n\n'
            ).format(ver_obj=ver_obj, exp=exp, ret=ret)
        )

    def test_each_part__2(self) -> None:
        ver_obj = Mock(spec=StrictVersion)
        type(ver_obj).__repr__ = Mock(
            return_value="MockedStrictVersion('1.6b2')"
        )
        type(ver_obj).version = PropertyMock(return_value=(1, 6, 0))
        type(ver_obj).prerelease = PropertyMock(return_value=('b', 2))
        exp = [
            _VersionPart(
                pos=0,
                txt='1',
                num=1,
                pre_txt='',
                pre_num=-1,
                name='major'
            ),
            _VersionPart(
                pos=1,
                txt='6b2',
                num=6,
                pre_txt='b',
                pre_num=2,
                name='minor'
            ),
            _VersionPart(
                pos=2,
                txt='',
                num=0,
                pre_txt='',
                pre_num=-1,
                name='patch'
            ),
        ]
        ret = list(_each_version_part(ver_obj))
        self.assertEqual(
            ret,
            exp,
            msg=(
                '\n\n'
                '_each_version_part({ver_obj!r})\n\n'
                'expected:\n\n'
                '{exp!r}\n\n'
                'got:\n\n'
                '{ret!r}\n\n'
            ).format(ver_obj=ver_obj, exp=exp, ret=ret)
        )

    def test_each_part__3(self) -> None:
        ver_obj = Mock(spec=StrictVersion)
        type(ver_obj).__repr__ = Mock(
            return_value="MockedStrictVersion('1.0.1a4')"
        )
        type(ver_obj).version = PropertyMock(return_value=(1, 0, 1))
        type(ver_obj).prerelease = PropertyMock(return_value=('a', 4))
        exp = [
            _VersionPart(
                pos=0,
                txt='1',
                num=1,
                pre_txt='',
                pre_num=-1,
                name='major'
            ),
            _VersionPart(
                pos=1,
                txt='0',
                num=0,
                pre_txt='',
                pre_num=-1,
                name='minor'
            ),
            _VersionPart(
                pos=2,
                txt='1a4',
                num=1,
                pre_txt='a',
                pre_num=4,
                name='patch'
            ),
        ]
        ret = list(_each_version_part(ver_obj))
        self.assertEqual(
            ret,
            exp,
            msg=(
                '\n\n'
                '_each_version_part({ver_obj!r})\n\n'
                'expected:\n\n'
                '{exp!r}\n\n'
                'got:\n\n'
                '{ret!r}\n\n'
            ).format(ver_obj=ver_obj, exp=exp, ret=ret)
        )
