import codecs
from collections import UserString
from functools import reduce
from typing import ByteString as _ByteString
from typing import (
    Generator,
    Optional,
    Tuple,
    Union,
    cast,
)

_Str = Union[str, UserString]


def _each_utf8_hex(text: _Str) -> Generator[str, None, None]:
    for char in text:
        if ord(char) < 128 and char.isprintable():
            yield char
            continue
        utf8_bytes = char.encode('utf8')
        for utf8_byte in utf8_bytes:
            str_hex = '\\%s' % hex(utf8_byte)[1:]
            yield str_hex


def encode(
        text: _Str,
        errors: _Str = 'strict'
) -> Tuple[bytes, int]:
    """Convert a :obj:`str`, that may contain escaped utf8 hexadecimal, to
    bytes of escaped utf8 hexadecimal.

    Args:
        text (str or :obj:`~UserString`): The string input.
        errors (str or :obj:`~UserString`): The error checking level.

    Returns:
        bytes: The given ``text`` converted into escaped utf8 bytes.
        int: The number of given ``text`` characters consumed

    Raises:
         UnicodeEncodeError: if the given ``text`` contains escaped
            utf8 hexadecimal that references invalid utf8 bytes.
    """

    # Convert the given 'text', that are of type UserString into a str.
    # if isinstance(text, UserString):
    #     text_input = str(text)
    # else:

    text_input = str(text)

    # Convert the given 'errors', that are of type UserString into a str.
    errors_input = str(errors)

    # Convert the string into utf-8 bytes
    text_bytes_utf8 = text_input.encode('utf-8')
    text_bytes_utf8 = cast(bytes, text_bytes_utf8)

    # Convert the utf8 bytes into a string of latin-1 characters.
    # This basically maps the exact utf8 bytes to the string. Also,
    # this converts any escaped hexadecimal sequences \\xHH into
    # \xHH bytes.
    text_str_latin1 = text_bytes_utf8.decode('unicode_escape')

    # Convert the string of latin-1 characters (which are actually
    # utf8 characters) into bytes.
    text_bytes_utf8 = text_str_latin1.encode('latin1')

    # Convert the utf8 bytes into a string.
    try:
        text_str = text_bytes_utf8.decode('utf-8', errors=errors_input)
    except UnicodeDecodeError as e:
        raise UnicodeEncodeError(
            'eutf8h',
            str(text_input),
            e.start,
            e.end,
            e.reason,
        )

    # Convert each character into a string of escaped utf8 hexadecimal.
    out_str: str = reduce(lambda a, b: f'{a}{b}', _each_utf8_hex(text_str))

    out_bytes = out_str.encode('utf-8')

    return out_bytes, len(text)


def decode(
        data: _ByteString,
        errors: _Str = 'strict'
) -> Tuple[str, int]:
    """Convert a bytes type of escaped utf8 hexadecimal to a string.

    Args:
        data (bytes or bytearray or memoryview): The escaped utf8
            hexadecimal bytes.
        errors (str or :obj:`~UserString`): The error checking level.

    Returns:
        str: The given ``data`` (of escaped utf8 hexadecimal bytes)
            converted into a :obj:`str`.
        int: The number of the given ``data`` bytes consumed.

    Raises:
         UnicodeDecodeError: if the given ``data`` contains escaped
            utf8 hexadecimal that references invalid utf8 bytes.


    """
    # Convert memoryview and bytearray objects to bytes.
    data_bytes = bytes(data)

    # Convert the given 'errors', that are of type UserString into a str.
    errors_input = str(errors)

    # Convert the utf8 bytes into a string of latin-1 characters.
    # This basically maps the exact utf8 bytes to the string. Also,
    # this converts any escaped hexadecimal sequences \\xHH into
    # \xHH bytes.
    text_str_latin1 = data_bytes.decode('unicode_escape')

    # Convert the string of latin-1 characters (which are actually
    # utf8 characters) into bytes.
    text_bytes_utf8 = text_str_latin1.encode('latin1')

    # Convert the utf8 bytes into a string.
    try:
        out = text_bytes_utf8.decode('utf-8', errors=errors_input)
    except UnicodeDecodeError as e:
        raise UnicodeDecodeError(
            'eutf8h',
            data_bytes,
            e.start,
            e.end,
            e.reason
        )
    return out, len(data)


NAME = __name__.split('.')[-1]


# noinspection PySameParameterValue
def _get_codec_info(name: str) -> Optional[codecs.CodecInfo]:
    if name == NAME:
        obj = codecs.CodecInfo(  # type: ignore
            name=NAME,
            encode=encode,  # type: ignore[arg-type]
            decode=decode,  # type: ignore[arg-type]
        )
        return obj
    return None


def register() -> None:
    try:
        codecs.getdecoder(NAME)
    except LookupError:
        codecs.register(_get_codec_info)   # type: ignore
