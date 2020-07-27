import re

__all__ = [
    'as_escaped_unicode_literal',
    'as_escaped_utf8_literal',
    'camel_to_underscore',
    'convert_escaped_unicode_literal',
    'convert_escaped_utf8_literal',
    'underscore_to_camel',
]


def as_escaped_unicode_literal(
        text: str
) -> str:
    """Convert the given ``text``  into a string of escaped Unicode
    hexadecimal.

    Args:
         text (:obj:`str`): The string to convert.

    :rtype:
        :obj:`str`

            A string with each character of the given ``text`` converted
            into an escaped Python literal.

    Example:
        >>> from flutils.strutils import as_escaped_unicode_literal
        >>> t = '1.★ 🛑'
        >>> as_literal(t)
        '\\\\x31\\\\x2e\\\\u2605\\\\x20\\\\U0001f6d1'
    """
    out = ''
    for c in text:
        c_hex = hex(ord(c))[2:]
        c_len = len(c_hex)
        if c_len in (1, 2):
            out += '\\x{:0>2}'.format(c_hex)
        elif c_len in (3, 4):
            out += '\\u{:0>4}'.format(c_hex)
        else:
            out += '\\U{:0>8}'.format(c_hex)
    return out


def as_escaped_utf8_literal(
        text: str,
) -> str:
    """Convert the given ``text`` into a string of escaped UTF8 hexadecimal.

    Args:
         text (:obj:`str`): The string to convert.

    :rtype:
        :obj:`str`

            A string with each character of the given ``text`` converted
            into an escaped UTF8 hexadecimal.

    Example:
        >>> from flutils.strutils import as_literal_utf8
        >>> t = '1.★ 🛑'
        >>> as_escaped_utf8_literal(t)
        '\\\\x31\\\\x2e\\\\xe2\\\\x98\\\\x85\\\\x20\\\\xf0\\\\x9f\\\\x9b
        \\\\x91'
    """
    out = ''
    text_bytes = text.encode('utf8')
    for c in text_bytes:
        out += '\\%s' % hex(c)[1:]
    return out


_CAMEL_TO_UNDERSCORE_RE = re.compile(
    '((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))'
)


# noinspection PySameParameterValue
def camel_to_underscore(
        text: str
) -> str:
    """Convert a camel-cased string to a string containing words separated
    with underscores.

    Args:
        text (str): The camel-cased string to convert.

    :rtype: :obj:`str`

    Example:
        >>> from flutils.strutils import camel_to_underscore
        >>> camel_to_underscore('FooBar')
        'foo_bar'
    """
    return _CAMEL_TO_UNDERSCORE_RE.sub(r'_\1', text).lower()


def convert_escaped_unicode_literal(
        text: str
) -> str:
    """Convert any escaped Unicode literal hexadecimal character(s) to the
    proper character(s).

    This function will convert a string, that may contain escaped Unicode
    literal hexadecimal characters, into a string with the proper characters.

    Args:
        text (:obj:`str`): The string that may have escaped Unicode
            hexadecimal.

    :rtype:
        :obj:`str`

            A string with each escaped Unicode hexadecimal character converted
            into the proper character.


    The following Unicode literal formats are supported::

        \\x31
        \\u0031
        \\U00000031

    Examples:

        Basic usage::

            >>> from flutils.strutils import convert_escaped_unicode_literal
            >>> a = '\\\\x31\\\\x2e\\\\u2605\\\\x20\\\\U0001f6d1'
            >>> convert_escaped_unicode_literal(a)
            '1.★ 🛑'

        This function is intended for cases when the value of an environment
        variable contains escaped Unicode literal characters that need to be
        converted to proper characters::

            $ export TEST='\\x31\\x2e\\u2605\\x20\\U0001f6d1'
            $ python

        ::

            >>> import os
            >>> from flutils.strutils import convert_escaped_unicode_literal
            >>> a = os.getenv('TEST')
            >>> a
            '\\\\x31\\\\x2e\\\\u2605\\\\x20\\\\U0001f6d1'
            >>> convert_escaped_unicode_literal(a)
            '1.★ 🛑'

    """
    text_bytes = text.encode()
    return text_bytes.decode('unicode_escape')


def convert_escaped_utf8_literal(
        text: str
) -> str:
    """Convert any escaped UTF-8 hexadecimal character bytes into the proper
    string characters(s).

    This function will convert a string, that may contain escaped UTF-8
    literal hexadecimal bytes, into a string with the proper characters.

    Args:
        text (:obj:`str`): The string that may have escaped UTF8 hexadecimal.

    Raises:
         UnicodeDecodeError: if any of the escaped hexadecimal characters
            are not proper UTF8 bytes.

    :rtype:
        :obj:`str`

            A string with each escaped UTF8 hexadecimal character converted
            into the proper character.

    Examples:

        Basic usage:

            >>> from flutils.strutils import convert_raw_utf8_escape
            >>> a = 'test\\\\xc2\\\\xa9'
            >>> convert_escaped_utf8_literal(a)
            'test©'

        This function is intended for cases when the value of an environment
        variable contains escaped UTF-8 literal characters (bytes) that need
        to be converted to proper characters::

            $ export TEST='test\\\\xc2\\\\xa9'
            $ python

        ::

            >>> import os
            >>> from flutils.strutils import convert_raw_utf8_escape
            >>> a = os.getenv('TEST')
            >>> a
            'test\\\\xc2\\\\xa9'
            >>> convert_escaped_utf8_literal(a)
            'test©'
    """
    from flutils.codecs import register_codecs  # pylint:disable=C0415
    register_codecs()
    text_bytes = text.encode('utf-8')
    text = text_bytes.decode('raw_utf8_escape')
    return text


def underscore_to_camel(
        text: str,
        lower_first: bool = True
) -> str:
    """Convert a string with words separated by underscores to a camel-cased
    string.

    Args:
        text (:obj:`str`): The camel-cased string to convert.
        lower_first (:obj:`bool`, optional): Lowercase the first character.
            Defaults to :obj:`True`.

    :rtype: :obj:`str`

    Examples:
        >>> from flutils.strutils import underscore_to_camel
        >>> underscore_to_camel('foo_bar')
        'fooBar'
        >>> underscore_to_camel('_one__two___',lower_first=False)
        'OneTwo'
    """
    out = ''.join([x.capitalize() or '' for x in text.split('_')])
    if lower_first is True:
        return out[:1].lower() + out[1:]
    return out
