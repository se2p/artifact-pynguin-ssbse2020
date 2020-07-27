import unittest
from typing import (
    List,
    NamedTuple,
    Optional,
)

from flutils.strutils import (
    as_escaped_unicode_literal,
    as_escaped_utf8_literal,
    camel_to_underscore,
    convert_escaped_utf8_literal,
    convert_escaped_unicode_literal,
    underscore_to_camel
)


class Values(NamedTuple):
    arg: str
    lower_first: Optional[bool]
    exp: str


def _add_values(
        arg: str,
        exp: str,
        values: List[Values],
        lower_first: Optional[bool] = None
) -> None:
    values.append(Values(arg, lower_first, exp))


class TestStrutils(unittest.TestCase):

    def test_camel_to_underscore(self) -> None:
        values: List[Values] = []
        _add_values('FooBar', 'foo_bar', values)
        _add_values('oneTwo', 'one_two', values)
        _add_values('THREEFourFive', 'three_four_five', values)
        _add_values('sixSEVENEight', 'six_seven_eight', values)
        for v in values:
            with self.subTest(v=v):
                ret = camel_to_underscore(v.arg)
                self.assertEqual(
                    ret,
                    v.exp,
                    msg=(
                        f'\n\n'
                        f'camel_to_underscore({v.arg!r})\n'
                        f'expected: {v.exp!r}\n'
                        f'     got: {ret!r}\n'
                    )
                )

    def test_underscore_to_camel(self) -> None:
        values: List[Values] = []
        _add_values('foo_bar', 'fooBar', values, lower_first=True)
        _add_values('one__two', 'OneTwo', values, lower_first=False)
        _add_values('three__four__', 'threeFour', values, lower_first=True)
        _add_values('__five_six__', 'FiveSix', values, lower_first=False)
        for v in values:
            with self.subTest(v=v):
                ret = underscore_to_camel(v.arg, lower_first=v.lower_first)
                self.assertEqual(
                    ret,
                    v.exp,
                    msg=(
                        f'\n\n'
                        f'underscore_to_camel({v.arg!r}, '
                        f'lower_first={v.lower_first!r})\n'
                        f'expected: {v.exp!r}\n'
                        f'     got: {ret!r}\n'
                    )
                )

    def test_as_escaped_unicode_literal(self) -> None:
        arg = '1.\u2605 \U0001f6d1'
        arg_lit = "'1.\\u2605 \\U0001f6d1'"
        ret = as_escaped_unicode_literal(arg)
        exp = '\\x31\\x2e\\u2605\\x20\\U0001f6d1'
        self.assertEqual(
            ret,
            exp,
            msg=(
                f'\n\n'
                f'as_escaped_unicode_literal({arg_lit})\n'
                f'expected: {exp!r}\n'
                f'     got: {ret!r}\n'
            )
        )

    def test_as_escaped_utf8_literal(self) -> None:
        arg = '1.\u2605 \U0001f6d1'
        arg_lit = "'1.\\u2605 \\U0001f6d1'"
        ret = as_escaped_utf8_literal(arg)
        exp = '\\x31\\x2e\\xe2\\x98\\x85\\x20\\xf0\\x9f\\x9b\\x91'
        self.assertEqual(
            ret,
            exp,
            msg=(
                f'\n\n'
                f'as_escaped_utf8_literal({arg_lit})\n'
                f'expected: {exp!r}\n'
                f'     got: {ret!r}\n'
            )
        )

    def test_convert_escaped_unicode_literal(self) -> None:
        exp = '\x31\x2e\u2605\x20\U0001f6d1'
        arg = '\\x31\\x2e\\u2605\\x20\\U0001f6d1'
        ret = convert_escaped_unicode_literal(arg)
        self.assertEqual(
            ret,
            exp,
            msg=(
                f'\n\n'
                f'convert_escaped_unicode_literal({arg!r})\n'
                f'expected: {exp!r}\n'
                f'     got: {ret!r}\n'
            )
        )

    def test_convert_escaped_utf8_literal(self) -> None:
        values = (
            ('hello\\xe2\\x98\\x85', 'hello\u2605'),  # hello★

        )
        for arg, exp in values:
            with self.subTest(arg=arg, exp=exp):
                ret = convert_escaped_utf8_literal(arg)
                self.assertEqual(
                    ret,
                    exp,
                    msg=(
                        f'\n\n'
                        f'convert_escaped_utf8_literal({arg})\n'
                        f'expected: {exp!r}\n'
                        f'     got: {ret!r}\n'
                    )
                )
