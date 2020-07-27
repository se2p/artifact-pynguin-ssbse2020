from . import (
    b64,
    raw_utf8_escape,
)


def register_codecs() -> None:
    """Register additional codecs.

    *New in version 0.4.*

    :rtype: :obj:`None`

    Examples:

        >>> from flutils.codecs import register_codecs
        >>> register_codecs()
        >>> 'test©'.encode('raw_utf8_escape')
        b'test\\\\xc2\\\\xa9'
        >>> b'test\\\\xc2\\\\xa9'.decode('raw_utf8_escape')
        'test©'
        >>> 'dGVzdA=='.encode('b64')
        b'test'
        >>> b'test'.decode('b64')
        'dGVzdA=='

    """
    raw_utf8_escape.register()
    b64.register()
