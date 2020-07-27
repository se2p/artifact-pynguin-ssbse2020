import unittest
from collections import UserString
from typing import (
    NamedTuple,
    Tuple,
)

from flutils.codecs import register_codecs
# noinspection PyProtectedMember
from flutils.codecs.raw_utf8_escape import (
    NAME,
    _get_codec_info,
    decode,
    encode,
)


class Values(NamedTuple):
    txt_str: str
    txt_bytes: bytes
    txt_str_len: int
    txt_bytes_len: int


TEST_VALUES: Tuple[Values, ...] = (
    Values(
        'Test',
        b'Test',
        4,
        4,
    ),
    Values(
        (
            '1.\u2605 2.\u2606 3.\u2b50\ufe0e 4.\u2729 5.\u272a 6.\u272b'
            '7.\u272d 8.\u272e 9.\U0001f1fa\U0001f1f8 10.\U0001f1fe\U0001f1f9 '
            '11.\U0001f6d1'
        ),
        (
            b'1.\\xe2\\x98\\x85 2.\\xe2\\x98\\x86 3.\\xe2\\xad\\x90\\xef\\xb8'
            b'\\x8e 4.\\xe2\\x9c\\xa9 5.\\xe2\\x9c\\xaa 6.\\xe2\\x9c\\xab7.'
            b'\\xe2\\x9c\\xad 8.\\xe2\\x9c\\xae 9.\\xf0\\x9f\\x87\\xba\\xf0'
            b'\\x9f\\x87\\xb8 10.\\xf0\\x9f\\x87\\xbe\\xf0\\x9f\\x87\\xb9 11.'
            b'\\xf0\\x9f\\x9b\\x91'
        ),
        47,
        221,
    ),
    Values(
        'Te\\st\u2605',
        b'Te\\st\\xe2\\x98\\x85',
        6,
        17,
    ),
    Values(
        '\u2606\u2b50\ufe0e',
        b'\\xe2\\x98\\x86\\xe2\\xad\\x90\\xef\\xb8\\x8e',
        3,
        36,
    )

)
register_codecs()


class AString(UserString):
    pass


class AStringPatched(UserString):

    # Need to add the encode method because of:
    #     https://bugs.python.org/issue36582
    #
    # The pull request of the fix:
    #    https://github.com/python/cpython/pull/13138
    #
    # The bug is a result of the UserString.encode
    # method not returning bytes.
    def encode(self, *args, **kwargs) -> bytes:
        return self.data.encode(*args, **kwargs)


class TestRawUtf8Escape(unittest.TestCase):

    def test_encode_value_bytes(self) -> None:
        for v in TEST_VALUES:
            ret = encode(v.txt_str)[0]
            self.assertEqual(
                ret,
                v.txt_bytes,
                msg=(
                    f'\n\n'
                    f'encode({v.txt_str!r})[0]\n\n'
                    f'expected: {v.txt_bytes!r}\n\n'
                    f'     got: {ret!r}\n\n'
                )
            )

    def test_encode_consumed_value(self) -> None:
        for v in TEST_VALUES:
            ret = encode(v.txt_str)[1]
            self.assertEqual(
                ret,
                v.txt_str_len,
                msg=(
                    f'\n\n'
                    f'encode({v.txt_str!r})[1]\n\n'
                    f'expected: {v.txt_str_len!r}\n\n'
                    f'     got: {ret!r}\n\n'
                )
            )

    def test_encode_raises_unicode_encode_error(self) -> None:
        with self.assertRaises(UnicodeEncodeError):
            encode('Hello\\x80')

    def test_decode_value_bytes(self) -> None:
        for v in TEST_VALUES:
            ret = decode(v.txt_bytes)[0]
            self.assertEqual(
                ret,
                v.txt_str,
                msg=(
                    f'\n\n'
                    f'decode({v.txt_bytes!r})[0]\n\n'
                    f'expected: {v.txt_str!r}\n\n'
                    f'     got: {ret!r}\n\n'
                )
            )

    def test_decode_consumed_value(self) -> None:
        for v in TEST_VALUES:
            ret = decode(v.txt_bytes)[1]
            self.assertEqual(
                ret,
                v.txt_bytes_len,
                msg=(
                    f'\n\n'
                    f'decode({v.txt_bytes!r})[1]\n\n'
                    f'expected: {v.txt_bytes_len!r}\n\n'
                    f'     got: {ret!r}\n\n'
                )
            )

    def test_encode_raises_unicode_decode_error(self) -> None:
        with self.assertRaises(UnicodeDecodeError):
            decode(b'Hello\\x80')

    def test_registered_encode_value(self) -> None:
        for v in TEST_VALUES:
            ret = v.txt_str.encode(NAME)
            self.assertEqual(
                ret,
                v.txt_bytes,
                msg=(
                    f'\n\n'
                    f'{v.txt_str!r}.encode({NAME!r})\n\n'
                    f'expected: {v.txt_bytes!r}\n\n'
                    f'     got: {ret!r}\n\n'
                )
            )

    def test_registered_decode_value(self) -> None:
        for v in TEST_VALUES:
            ret = v.txt_bytes.decode(NAME)
            self.assertEqual(
                ret,
                v.txt_str,
                msg=(
                    f'\n\n'
                    f'{v.txt_bytes!r}.decode({NAME!r})\n\n'
                    f'expected: {v.txt_str!r}\n\n'
                    f'     got: {ret!r}\n\n'
                )
            )

    def test_encode_user_string(self) -> None:
        # This test is setup to get around the bug:
        # https://bugs.python.org/issue36582
        # This test will also work once the bug has
        # been fixed.
        arg = 'Testing1'
        obj = AString(arg)

        # Verify that encode returns bytes.  If not,
        # then use the patched UserString.
        chk = obj.encode('utf-8')
        if isinstance(chk, bytes) is False:
            obj = AStringPatched(arg)

        # Perform the test
        exp = b'Testing1'
        ret = obj.encode(NAME)
        ret_type = type(ret).__name__

        self.assertEqual(
            ret,
            exp,
            msg=(
                f'\n\n'
                f'{arg!r}.encode({NAME!r})\n\n'
                f'expected: {exp!r}\n\n'
                f'     got: {ret!r}\n\n'
                f'    type: {ret_type}\n\n'
            )
        )

    def test_get_codec_info(self) -> None:
        val = _get_codec_info('foo')
        self.assertEqual(val, None)
