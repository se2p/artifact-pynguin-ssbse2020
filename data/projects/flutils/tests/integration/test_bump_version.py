import unittest
from typing import (
    List,
    Tuple,
    Union,
)

from flutils.packages import bump_version


class TestBumpVersion(unittest.TestCase):

    def setUp(self) -> None:
        self.values: List[Tuple[Tuple[str, int, Union[str, None]], str]] = [
            (('1.0', 0, None), '2.0'),
            (('1.1', 1, None), '1.2'),
            (('1.1', 2, None), '1.1.1'),
            (('1.1', 1, 'a'), '1.2a0'),
            (('1.1', 1, 'b'), '1.2b0'),
            (('1.10a10', 1, 'a'), '1.10a11'),
            (('1.10a10', 1, 'b'), '1.10b0'),
            (('10.12b6', 1, 'a'), '10.13a0'),
            (('10.12b6', 1, 'b'), '10.12b7'),
            (('2.3.12a7', 2, 'a'), '2.3.12a8'),
            (('2.3.12a7', 2, 'b'), '2.3.12b0'),
            (('2.3.12b7', 2, 'a'), '2.3.13a0'),
            (('2.3.2b77', 2, 'b'), '2.3.2b78'),
            (('6.10.2', 0, ''), '7.0'),
            (('7.10a5', 0, ''), '8.0'),
            (('757.6b57', 0, ''), '758.0'),
            (('51.678.1a5', 0, ''), '52.0'),
            (('211.678.178b2', 0, ''), '212.0'),
            (('6.5a2', 1, ''), '6.5'),
            (('6.5a2', 2, ''), '6.5.1'),
            (('6.2.5a2', 2, ''), '6.2.5'),
            (('6.5b2', 1, ''), '6.5'),
            (('6.5b2', 2, ''), '6.5.1'),
            (('6.2.5b2', 2, ''), '6.2.5'),
            (('1.2b0', 2, 'b'), '1.2.1b0'),
            # From bump_version doc string examples:
            (('1.2.2', 2, None), '1.2.3'),
            (('1.2.3', 1, None), '1.3'),
            (('1.3.4', 0, None), '2.0'),
            (('1.2.3', 2, 'a'), '1.2.4a0'),
            (('1.2.4a0', 2, 'a'), '1.2.4a1'),
            (('1.2.4a1', 2, 'b'), '1.2.4b0'),
            (('1.2.4a1', 2, None), '1.2.4'),
            (('1.2.4b1', 2, None), '1.2.4'),
            (('2.1.3', 1, 'a'), '2.2a0'),
            (('1.2b0', 2, None), '1.2.1'),
        ]

    def test_bump_version(self) -> None:
        for args, exp in self.values:
            kwargs = {
                'version': args[0],
                'position': args[1],
                'pre_release': args[2],
                'exp': exp
            }
            with self.subTest(**kwargs):
                kwargs['ret'] = bump_version(
                    args[0],
                    position=args[1],
                    pre_release=args[2]
                )
                self.assertEqual(
                    kwargs['ret'],
                    exp,
                    msg=(
                        '\n\n'
                        'bump_version({version!r}, '
                        'position={position!r}, '
                        'pre_release={pre_release!r})\n'
                        'expected: {exp!r}\n'
                        '     got: {ret!r}\n'
                    ).format(**kwargs)
                )
