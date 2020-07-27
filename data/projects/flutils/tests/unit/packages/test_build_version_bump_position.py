import unittest

# noinspection PyProtectedMember
from flutils.packages import _build_version_bump_position


class TestBuildVersionBumpPosition(unittest.TestCase):

    def test_build_version_bump_position__1(self) -> None:
        exp = 2
        position = 2
        ret = _build_version_bump_position(position)
        self.assertEqual(
            ret,
            exp,
            msg=(
                '\n\n'
                '_build_version_bump_position({position!r})\n\n'
                'expected:\n\n'
                '{exp!r}\n\n'
                'got:\n\n'
                '{ret!r}\n\n'
            ).format(position=position, exp=exp, ret=ret)
        )

    def test_build_version_bump_position__2(self) -> None:
        exp = 0
        position = -3
        ret = _build_version_bump_position(position)
        self.assertEqual(
            ret,
            exp,
            msg=(
                '\n\n'
                '_build_version_bump_position({position!r})\n\n'
                'expected:\n\n'
                '{exp!r}\n\n'
                'got:\n\n'
                '{ret!r}\n\n'
            ).format(position=position, exp=exp, ret=ret)
        )

    def test_build_version_bump_position__3(self) -> None:
        exp = 2
        position = -1
        ret = _build_version_bump_position(position)
        self.assertEqual(
            ret,
            exp,
            msg=(
                '\n\n'
                '_build_version_bump_position({position!r})\n\n'
                'expected:\n\n'
                '{exp!r}\n\n'
                'got:\n\n'
                '{ret!r}\n\n'
            ).format(position=position, exp=exp, ret=ret)
        )

    def test_build_version_bump_position__4(self) -> None:
        position = 3
        with self.assertRaises(ValueError):
            _build_version_bump_position(position)

    def test_build_version_bump_position__5(self) -> None:
        position = -4
        with self.assertRaises(ValueError):
            _build_version_bump_position(position)
