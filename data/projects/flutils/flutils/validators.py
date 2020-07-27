import keyword
from collections import UserString
from typing import Union


__all__ = ['validate_identifier']


_BUILTIN_NAMES = tuple(filter(
    lambda x: x.startswith('__') and x.endswith('__'),
    dir('__builtins__')
))


def validate_identifier(
        identifier: Union[str, UserString],
        allow_underscore: bool = True
) -> None:
    """Validate the given string is a proper identifier.

    This validator will also raise an error if the given identifier is a
    keyword or a builtin identifier.

    Args:
        identifier (:obj:`str` or :obj:`UserString <collections.UserString>`):
            The value to be tested.
        allow_underscore (:obj:`bool`, optional): A value of :obj:`False`
            will raise an error when the ``identifier`` has a value that starts
            with an underscore ``_``. (Use :obj:`False` when validating
            potential :obj:`namedtuple <collections.namedtuple>` keys)
            Defaults to: :obj:`True`.

    Raises:
        SyntaxError: If the given identifier is invalid.
        TypeError: If the given identifier is not a :obj:`str` or
            :obj:`UserString <collections.UserString>`.

    :rtype: :obj:`None`

    Example:
        >>> from flutils.validators import validate_identifier
        >>> validate_identifier('123')
        SyntaxError: The given 'identifier', '123', cannot start with a number
    """
    if isinstance(identifier, UserString):
        identifier = str(identifier)
    if not isinstance(identifier, str):
        raise TypeError(
            "The given 'identifier' must be a 'str'.  Got: %r"
            % type(identifier).__name__
        )
    identifier = identifier.strip()
    if not identifier:
        raise SyntaxError("The given 'identifier' cannot be empty")

    if allow_underscore is False and identifier[0:1] == '_':
        raise SyntaxError(
            f"The given 'identifier', {identifier!r}, cannot start with an "
            "underscore '_'"
        )

    if identifier[0:1].isdigit():
        raise SyntaxError(
            f"The given 'identifier', {identifier!r}, cannot start with a "
            "number"
        )

    if not identifier.isidentifier():
        raise SyntaxError(
            f"The given 'identifier', {identifier!r}, is invalid."
        )

    if keyword.iskeyword(identifier):
        raise SyntaxError(
            f"The given 'identifier', {identifier!r}, cannot be a keyword"
        )

    if identifier in _BUILTIN_NAMES:
        raise SyntaxError(
            f"The given 'identifier', {identifier!r}, cannot be a builtin name"
        )
