# Stubs for flutils (Python 3)
import grp
import grp as _grp
import pwd
import pwd as _pwd
from collections import (
    Mapping as _Mapping,
    UserString as _UserString,
)
# noinspection PyShadowingBuiltins
from os import PathLike as _PathLike
from pathlib import Path as _Path
from types import (
    ModuleType as _ModuleType,
    SimpleNamespace as _SimpleNamespace
)
from typing import (
    Any as _Any,
    Dict as _Dict,
    Generator as _Generator,
    IO as _IO,
    List as _List,
    NamedTuple as _NamedTuple,
    Optional as _Optional,
    Pattern as _Pattern,
    Sequence as _Sequence,
    Tuple as _Tuple,
    Union as _Union,
)
from flutils import (
    cmdutils,
    codecs,
    decorators,
    moduleutils,
    moduleutils,
    namedtupleutils,
    objutils,
    packages,
    pathutils,
    setuputils,
    strutils,
    txtutils,
    validators,
)

_PATH = _Union[_PathLike, str]
_STR_OR_INT_OR_NONE = _Union[str, int, None]
_STR = _Union[str, _UserString]


# noinspection PyUnusedClass,PyUnusedName,DuplicatedCode
class AnsiTextWrapper:
    width: int = ...
    initial_indent: str = ...
    subsequent_indent: str = ...
    expand_tabs: bool = ...
    replace_whitespace: bool = ...
    fix_sentence_endings: bool = ...
    break_long_words: bool = ...
    drop_whitespace: bool = ...
    break_on_hyphens: bool = ...
    tabsize: int = ...
    max_lines: _Optional[int] = ...
    placeholder: str = ...

    # Attributes not present in documentation
    sentence_end_re: _Pattern[str] = ...
    wordsep_re: _Pattern[str] = ...
    wordsep_simple_re: _Pattern[str] = ...
    whitespace_trans: str = ...
    unicode_whitespace_trans: _Dict[int, int] = ...
    uspace: int = ...
    x: str = ...  # leaked loop variable

    def __init__(
            self,
            width: int = ...,
            initial_indent: str = ...,
            subsequent_indent: str = ...,
            expand_tabs: bool = ...,
            replace_whitespace: bool = ...,
            fix_sentence_endings: bool = ...,
            break_long_words: bool = ...,
            drop_whitespace: bool = ...,
            break_on_hyphens: bool = ...,
            tabsize: int = ...,
            *,
            max_lines: _Optional[int] = ...,
            placeholder: str = ...
    ) -> None: ...

    # Private methods *are* part of the documented API for subclasses.
    # noinspection PyUnusedFunction
    def _munge_whitespace(self, text: str) -> str: ...
    # noinspection PyUnusedFunction
    def _split(self, text: str) -> _List[str]: ...
    # noinspection PyUnusedFunction
    def _fix_sentence_endings(self, chunks: _List[str]) -> None: ...
    # noinspection PyUnusedFunction
    def _handle_long_word(
            self,
            reversed_chunks: _List[str],
            cur_line: _List[str],
            cur_len: int, width: int
    ) -> None: ...
    # noinspection PyUnusedFunction
    def _wrap_chunks(self, chunks: _List[str]) -> _List[str]: ...
    # noinspection PyUnusedFunction
    def _split_chunks(self, text: str) -> _List[str]: ...

    # noinspection PyUnusedFunction
    def wrap(self, text: str) -> _List[str]: ...
    # noinspection PyUnusedFunction
    def fill(self, text: str) -> str:...

# see flutils.setuputils.add_setup_cfg_commands
# noinspection PyUnusedFunction
def add_setup_cfg_commands(
        setup_kwargs: _Dict[str, _Any],
        setup_dir: _Optional[_Union[_PathLike, str]] = ...
) -> None: ...


# noinspection PyUnusedFunction
def as_literal_unicode(text: str) -> str: ...

# noinspection PyUnusedFunction
def as_literal_utf8(text: str) -> str: ...

# noinspection PyUnusedFunction
def bump_version(
        version: _STR,
        position: int=...,
        pre_release: _Optional[str]=...
) -> str: ...


# noinspection PyUnusedClass,PyUnusedName,PyPep8Naming
class cached_property:
    __doc__: _Any = ...
    func: _Any = ...
    def __init__(self, func: _Any) -> None: ...
    def __get__(self, obj: _Any, cls: _Any) -> _Any: ...


# noinspection PyUnusedFunction
def camel_to_underscore(text: str) -> str: ...

# noinspection PyUnusedFunction
def chmod(
        path: _PATH,
        mode_file: _Optional[int]=...,
        mode_dir: _Optional[int]=...,
        include_parent: bool=...
) -> None: ...

# noinspection PyUnusedFunction
def chown(
        path: _PATH,
        user: _Optional[_STR]=...,
        group: _Optional[_STR]=...,
        include_parent: bool=...
) -> None: ...

# noinspection PyUnusedFunction
def cherry_pick(namespace: dict) -> None: ...

# noinspection PyUnusedFunction
def convert_raw_utf8_escape(text: str) -> str: ...

# noinspection PyUnusedFunction
def directory_present(
        path: _PATH,
        mode: _Optional[int]=...,
        user: _Optional[_STR]=...,
        group: _Optional[_STR]=...
) -> _Path: ...

# noinspection PyUnusedFunction
def exists_as(path: _PATH) -> str: ...

# noinspection PyUnusedFunction
def find_paths(pattern: _PATH) -> _Generator[_Path, None, None]: ...

# noinspection PyUnusedFunction
def get_os_group(name: _STR_OR_INT_OR_NONE=...) -> _grp.struct_group: ...

# noinspection PyUnusedFunction
def get_os_user(name: _STR_OR_INT_OR_NONE=...) -> _pwd.struct_passwd: ...

# noinspection PyUnusedFunction
def has_any_attrs(obj: _Any, *attrs: _STR) -> bool: ...

# noinspection PyUnusedFunction
def has_any_callables(obj: _Any, *attrs: _STR) -> bool: ...

# noinspection PyUnusedFunction
def has_attrs(obj: _Any, *attrs: _STR) -> bool: ...

# noinspection PyUnusedFunction
def has_callables(obj: _Any, *attrs: _STR) -> bool: ...

# noinspection PyUnusedFunction
def is_list_like(obj: _Any) -> bool: ...

# noinspection PyUnusedFunction
def is_subclass_of_any(obj: _Any, *classes: _Any) -> bool: ...

# noinspection PyUnusedFunction
def lazy_import_module(
        name: _STR,
        package: _Optional[_STR]=...
) -> _ModuleType: ...

# noinspection PyUnusedFunction
def len_without_ansi(seq: _Sequence) -> int: ...

# noinspection PyUnusedFunction
def normalize_path(path: _PATH) -> _Path: ...

# noinspection PyUnusedFunction
def path_absent(path: _PATH) -> None: ...

# noinspection PyUnusedFunction
def register_codecs() -> None: ...

# noinspection PyUnusedFunction
def run(
        command: _Sequence,
        stdout: _Optional[_IO] = ...,
        stderr: _Optional[_IO] = ...,
        columns: int =...,
        lines: int = ...,
        force_dimensions: bool = ...,
        interactive: bool = ...,
        **kwargs: _Any
) -> int: ...


_AllowedTypes = _Union[
    _List,
    _Mapping,
    _NamedTuple,
    _SimpleNamespace,
    _Tuple,
]

# noinspection PyUnusedFunction
def to_namedtuple(
        obj: _AllowedTypes
) -> _Union[_NamedTuple, _Tuple, _List]: ...

# noinspection PyUnusedFunction
def underscore_to_camel(text: _STR, lower_first: bool=...) -> str: ...

# noinspection PyUnusedFunction
def validate_identifier(
        identifier: _STR,
        allow_underscore: bool=...
) -> None: ...
