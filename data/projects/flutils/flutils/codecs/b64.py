import base64
import codecs
from binascii import Error
from collections import UserString
from typing import ByteString as _ByteString
from typing import (
    Optional,
    Tuple,
    Union,
)

_STR = Union[str, UserString]


# pylint: disable=W0613
# noinspection PyUnusedLocal
def encode(
        text: _STR,
        errors: _STR = 'strict'
) -> Tuple[bytes, int]:
    """Convert the given ``text`` of base64 characters into the base64
    decoded bytes.

    Args:
        text (str): The string input.  The given string input can span
            across many lines and be indented any number of spaces.
        errors (str): Not used.  This argument exists to meet the
            interface requirements.  Any value given to this argument
            is ignored.

    Returns:
        bytes: The given ``text`` converted into base64 bytes.
        int: The length of the returned bytes.
    """
    # Convert the given 'text', that are of type UserString into a str.
    text_input = str(text)

    # Cleanup whitespace.
    text_str = text_input.strip()
    text_str = '\n'.join(
        filter(
            lambda x: len(x) > 0,
            map(lambda x: x.strip(), text_str.strip().splitlines())
        )
    )

    # Convert the cleaned text into utf8 bytes
    text_bytes = text_str.encode('utf-8')
    try:
        out = base64.decodebytes(text_bytes)
    except Error as e:
        raise UnicodeEncodeError(
            'b64',
            text_input,
            0,
            len(text),
            (
                f'{text_str!r} is not a proper bas64 character string: '
                f'{e}'
            )
        )
    return out, len(text)


# noinspection PyUnusedLocal
def decode(
        data: _ByteString,
        errors: _STR = 'strict'
) -> Tuple[str, int]:
    """Convert the given ``data`` into base64 Characters.

    Args:
        data (bytes or bytearray or memoryview): Bytes to be converted
            to a string of base64 characters.
        errors (str or :obj:`~UserString`): Not used.  This argument exists
            to meet the interface requirements.  Any value given to this
            argument is ignored.

    Returns:
        str: of base64 Characters
        int: the number of the given ``data`` bytes consumed.
    """
    # Convert memoryview and bytearray objects to bytes.
    data_bytes = bytes(data)

    # Encode the 'data_bytes' into base64 bytes.
    encoded_bytes = base64.b64encode(data_bytes)

    # Decode the 'base64_bytes' as utf8 into a string.
    encoded_str = encoded_bytes.decode('utf-8')

    return encoded_str, len(data)


NAME = __name__.split('.')[-1]


# noinspection PySameParameterValue
def _get_codec_info(name: str) -> Optional[codecs.CodecInfo]:
    if name == NAME:
        obj = codecs.CodecInfo(  # type: ignore
            name=NAME,
            decode=decode,  # type: ignore[arg-type]
            encode=encode,  # type: ignore[arg-type]
        )
        return obj
    return None


def register() -> None:
    """Register the ``b64`` codec with Python."""
    try:
        codecs.getdecoder(NAME)
    except LookupError:
        codecs.register(_get_codec_info)   # type: ignore
