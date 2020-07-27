from collections import (
    OrderedDict,
    namedtuple,
)
from collections.abc import (
    Mapping,
    Sequence,
)
from functools import singledispatch
from types import SimpleNamespace
from typing import (
    Any,
    List,
    NamedTuple,
    Tuple,
    Union,
    cast,
)
from flutils.validators import validate_identifier

__all__ = ['to_namedtuple']

_AllowedTypes = Union[
    List,
    Mapping,
    NamedTuple,
    SimpleNamespace,
    Tuple,
]


def to_namedtuple(obj: _AllowedTypes) -> Union[NamedTuple, Tuple, List]:
    """Convert particular objects into a namedtuple.

    Args:
        obj: The object to be converted (or have it's contents converted) to
            a :obj:`NamedTuple <collections.namedtuple>`.

    If the given type is of :obj:`list` or :obj:`tuple`, each item will be
    recursively converted to a :obj:`NamedTuple <collections.namedtuple>`
    provided the items can be converted. Items that cannot be converted
    will still exist in the returned object.

    If the given type is of :obj:`list` the return value will be a new
    :obj:`list`.  This means the items are not changed in the given
    ``obj``.

    If the given type is of :obj:`Mapping <collections.abc.Mapping>`
    (:obj:`dict`), keys that can be proper identifiers will become attributes
    on the returned :obj:`NamedTuple <collections.namedtuple>`.  Additionally,
    the attributes of the returned :obj:`NamedTuple <collections.namedtuple>`
    are sorted alphabetically.

    If the given type is of :obj:`OrderedDict <collections.OrderedDict>`,
    the attributes of the returned :obj:`NamedTuple <collections.namedtuple>`
    keep the same order as the given
    :obj:`OrderedDict <collections.OrderedDict>` keys.

    If the given type is of :obj:`SimpleNamespace <types.SimpleNamespace>`,
    The attributes are sorted alphabetically in the returned
    :obj:`NamedTuple <collections.NamedTuple>`.

    Any identifier (key or attribute name) that starts with an underscore
    cannot be used as a :obj:`NamedTuple <collections.namedtuple>` attribute.

    All values are recursively converted.  This means a dictionary that
    contains another dictionary, as one of it's values, will be converted
    to a :obj:`NamedTuple <collections.namedtuple>` with the attribute's
    value also converted to a :obj:`NamedTuple <collections.namedtuple>`.

    :rtype:
        :obj:`list`

            A list with any of it's values converted to a
            :obj:`NamedTuple <collections.namedtuple>`.

        :obj:`tuple`

            A tuple with any of it's values converted to a
            :obj:`NamedTuple <collections.namedtuple>`.

        :obj:`NamedTuple <collections.namedtuple>`.

    Example:
        >>> from flutils.namedtupleutils import to_namedtuple
        >>> dic = {'a': 1, 'b': 2}
        >>> to_namedtuple(dic)
        NamedTuple(a=1, b=2)
    """
    return _to_namedtuple(obj)


@singledispatch
def _to_namedtuple(
        obj: Any,
        _started: bool = False
) -> Any:
    if _started is False:
        raise TypeError(
            "Can convert only 'list', 'tuple', 'dict' to a NamedTuple; "
            "got: (%r) %s" % (type(obj).__name__, obj)
        )
    return obj


# noinspection PyUnusedFunction,Mypy
@_to_namedtuple.register(Mapping)
def _(
        obj: Mapping,
        _started: bool = False
) -> Union[NamedTuple, Tuple]:
    keys = []
    for key in obj.keys():
        if hasattr(key, 'capitalize'):
            key = cast(str, key)
            try:
                validate_identifier(key, allow_underscore=False)
            except SyntaxError:
                continue
            if key.isidentifier():
                keys.append(key)
    if not isinstance(obj, OrderedDict):
        keys = tuple(sorted(keys))
    args = []
    for key in keys:
        val: Any = obj[key]
        val = _to_namedtuple(val, _started=True)
        args.append(val)
    if args:
        # noinspection Mypy
        make = namedtuple('NamedTuple', keys)  # type: ignore[misc]
        # noinspection PyTypeChecker,PyArgumentList
        out: NamedTuple = make(*args)
        return out
    make_empty = namedtuple('NamedTuple', '')
    out = make_empty()
    return out


# noinspection PyUnusedFunction,PyProtectedMember,Mypy
@_to_namedtuple.register(Sequence)  # type: ignore[no-redef]
def _(
        obj: Sequence,
        _started: bool = False
) -> Union[List[Any], Tuple[Any, ...], NamedTuple, str]:
    if hasattr(obj, 'capitalize'):
        obj = cast(str, obj)
        if _started is False:
            raise TypeError(
                "Can convert only 'list', 'tuple', 'dict' to a NamedTuple; "
                "got: (%r) %s" % (type(obj).__name__, obj)
            )
        return obj
    if hasattr(obj, '_fields'):
        fields: List[str] = list(obj._fields)
        if fields:
            obj = cast(NamedTuple, obj)
            args = []
            for attr in obj._fields:
                val: Any = getattr(obj, attr)
                val = _to_namedtuple(val, _started=True)
                args.append(val)
            if args:
                # noinspection Mypy
                make = namedtuple('NamedTuple', fields)  # type: ignore[misc]
                # noinspection PyTypeChecker,PyArgumentList
                out: NamedTuple = make(*args)
                return out
        return obj
    # noinspection PyTypeChecker
    out = []
    for item in obj:
        val = _to_namedtuple(item, _started=True)
        out.append(val)
    if not hasattr(obj, 'append'):
        return tuple(out)
    return out


# noinspection PyUnusedFunction,PyProtectedMember,Mypy
@_to_namedtuple.register(SimpleNamespace)  # type: ignore[no-redef]
def _(
        obj: SimpleNamespace,
        _started: bool = False
) -> NamedTuple:
    return _to_namedtuple(obj.__dict__)
