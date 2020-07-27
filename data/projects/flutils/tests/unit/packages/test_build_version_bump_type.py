import unittest
from typing import (
    List,
    Tuple,
)

# noinspection PyProtectedMember
from flutils.packages import (
    _BUMP_VERSION_MAJOR,
    _BUMP_VERSION_MINOR,
    _BUMP_VERSION_MINOR_ALPHA,
    _BUMP_VERSION_MINOR_BETA,
    _BUMP_VERSION_PATCH,
    _BUMP_VERSION_PATCH_ALPHA,
    _BUMP_VERSION_PATCH_BETA,
    _build_version_bump_type,
)


class TestBuildVersionBumpType(unittest.TestCase):

    def test_build_version_bump_type__1(self) -> None:
        values: List[Tuple[Tuple[int, str], int]] = [
            ((0, ''), _BUMP_VERSION_MAJOR),
            ((1, None), _BUMP_VERSION_MINOR),
            ((2, ''), _BUMP_VERSION_PATCH),
            ((1, 'a'), _BUMP_VERSION_MINOR_ALPHA),
            ((1, 'alpha'), _BUMP_VERSION_MINOR_ALPHA),
            ((1, 'b'), _BUMP_VERSION_MINOR_BETA),
            ((1, 'beta'), _BUMP_VERSION_MINOR_BETA),
            ((2, 'a'), _BUMP_VERSION_PATCH_ALPHA),
            ((2, 'alpha'), _BUMP_VERSION_PATCH_ALPHA),
            ((2, 'b'), _BUMP_VERSION_PATCH_BETA),
            ((2, 'beta'), _BUMP_VERSION_PATCH_BETA),
        ]
        for args, exp in values:
            kwargs = {
                'position_positive': args[0],
                'pre_release': args[1],
                'exp': exp,
            }
            with self.subTest(**kwargs):
                kwargs['ret'] = _build_version_bump_type(*args)
                self.assertEqual(
                    kwargs['ret'],
                    exp,
                    msg=(
                        '\n\n'
                        '_build_version_bump_type('
                        '{position_positive!r}, {pre_release!r})\n\n'
                        'expected:\n\n'
                        '{exp!r}\n\n'
                        'got:\n\n'
                        '{ret!r}\n\n'
                    ).format(**kwargs)
                )

    def test_build_version_bump_type__2(self) -> None:
        values: List[Tuple[int, str]] = [
            (0, 'a'),
            (0, 'b'),
            (1, 'c'),
            (2, 'c'),
        ]
        for args in values:
            kwargs = {
                'position_positive': args[0],
                'pre_release': args[1],
            }
            with self.subTest(**kwargs):
                with self.assertRaises(ValueError):
                    _build_version_bump_type(*args)
