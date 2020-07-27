# -*- coding: utf-8 -*-

"""Compiler functions."""

from __future__ import annotations

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2020"
__license__ = "MIT"
__email__ = "pyslvs@gmail.com"

from typing import (cast, get_type_hints, Tuple, List, Set, Dict, Iterable,
                    Callable, Any)
from types import ModuleType
from sys import stdout, exc_info, modules as sys_modules
from os import listdir, mkdir
from os.path import join, isdir
from importlib import import_module
from traceback import extract_tb, FrameSummary
from pkgutil import walk_packages
from textwrap import dedent
from re import sub, search
from collections import defaultdict
from dataclasses import is_dataclass
from enum import Enum
from inspect import isfunction, isclass, isgenerator, getfullargspec
from logging import getLogger, basicConfig, DEBUG

unload_modules = set(sys_modules)
basicConfig(stream=stdout, level=DEBUG, format="%(message)s")
logger = getLogger()
loaded_path: Set[str] = set()
inner_links: Dict[str, str] = {}
self_doc: Dict[str, str] = {}


class StandardModule(ModuleType):
    __all__: List[str]
    __path__: List[str]


def full_name(parent: Any, obj: Any) -> str:
    """Get full name of a object.
    If m is not a module, return empty string.
    """
    return f"{get_name(parent)}.{get_name(obj)}"


def get_name(obj: Any) -> str:
    """Get a real name from an object."""
    if hasattr(obj, '__name__'):
        if hasattr(obj, '__module__') and not hasattr(obj, '__class__'):
            if obj.__module__ == 'builtins':
                name = obj.__name__
            else:
                name = f"{obj.__module__}.{obj.__name__}"
        else:
            name = obj.__name__
    elif type(obj) is str:
        name = obj
    else:
        name = repr(obj)
    return name.replace('[', r'\[')


def public(names: Iterable[str], init: bool = True) -> Iterable[str]:
    """Yield public names only."""
    for name in names:
        if init:
            init = name == '__init__'
        if not name.startswith('_') or init:
            yield name


def docstring(obj: object) -> str:
    """Remove first indent of the docstring."""
    doc = obj.__doc__
    if doc is None or obj.__class__.__doc__ == doc:
        return ""
    two_parts = doc.split('\n', maxsplit=1)
    if len(two_parts) == 2:
        doc = two_parts[0] + '\n' + dedent(two_parts[1])
    return doc.lstrip().rstrip()


def table_row(*items: Iterable[str]) -> str:
    """Make the rows to a pipe table."""

    def table(_items: Iterable[str], space: bool = True) -> str:
        s = " " if space else ""
        return '|' + s + (s + '|' + s).join(_items) + s + '|\n'

    if len(items) == 0:
        raise ValueError("the number of rows is not enough")
    doc = table(items[0])
    if len(items) == 1:
        return doc
    line = (':' + '-' * (len(s) if len(s) > 3 else 3) + ':' for s in items[0])
    doc += table(line, False)
    for item in items[1:]:
        doc += table(item)
    return doc


def make_table(obj: Callable) -> str:
    """Make an argument table for function or method."""
    args = getfullargspec(obj)
    hints = defaultdict(lambda: Any, get_type_hints(obj))
    hints['self'] = " "
    args_doc = []
    type_doc = []
    all_args = []
    # Positional arguments
    all_args.extend(args.args or [])
    # The name of '*'
    if args.varargs is not None:
        new_name = f'**{args.varargs}'
        hints[new_name] = hints.pop(args.varargs, Any)
        all_args.append(new_name)
    elif args.kwonlyargs:
        all_args.append('*')
    # Keyword only arguments
    all_args.extend(args.kwonlyargs or [])
    # The name of '**'
    if args.varkw is not None:
        new_name = f'**{args.varkw}'
        hints[new_name] = hints.pop(args.varkw, Any)
        all_args.append(new_name)
    all_args.append('return')
    for arg in all_args:  # type: str
        args_doc.append(arg)
        type_doc.append(get_name(hints[arg]))
    doc = table_row(args_doc, type_doc)
    df = []
    if args.defaults is not None:
        df.extend([" "] * (len(args.args) - len(args.defaults)))
        df.extend(args.defaults)
    if args.kwonlydefaults is not None:
        df.extend(args.kwonlydefaults.get(arg, " ") for arg in args.kwonlyargs)
    if df:
        df.append(" ")
        doc += table_row([f"{v}" for v in df])
    return doc + '\n'


def is_abstractmethod(obj: Any) -> bool:
    """Return True if it is a abstract method."""
    return hasattr(obj, '__isabstractmethod__')


def is_staticmethod(parent: type, obj: Any) -> bool:
    """Return True if it is a static method."""
    name = get_name(obj)
    if name in parent.__dict__:
        return type(parent.__dict__[name]) is staticmethod
    else:
        raise NotImplementedError(f"please implement abstract member {name}")


def is_classmethod(parent: type, obj: Any) -> bool:
    """Return True if it is a class method."""
    if not hasattr(obj, '__self__'):
        return False
    return obj.__self__ is parent


def is_property(obj: Any) -> bool:
    """Return True if it is a property."""
    return type(obj) is property


def is_enum(obj: Any) -> bool:
    """Return True if is enum class."""
    if not isclass(obj):
        return False
    return Enum in mro(obj)


def mro(obj: type) -> Tuple[type, ...]:
    """Return inherited class."""
    return obj.__mro__


def super_cls(obj: type) -> type:
    """Return super class."""
    return mro(obj)[1]


def linker(name: str) -> str:
    """Return inner link format."""
    return name.lower().replace('.', '')


def get_stub_doc(parent: Any, name: str, level: int, prefix: str = "") -> str:
    """Generate docstring by type."""
    obj = getattr(parent, name)
    if prefix:
        name = f"{prefix}.{name}"
    inner_links[name] = linker(name)
    doc = '#' * level + f" {name}"
    sub_doc = []
    if isfunction(obj) or isgenerator(obj):
        doc += "()\n\n" + make_table(obj) + '\n'
        if isclass(parent):
            if is_abstractmethod(obj):
                doc += "Is a abstract method.\n\n"
            if is_staticmethod(parent, obj):
                doc += "Is a static method.\n\n"
            if is_classmethod(parent, obj):
                doc += "Is a class method.\n\n"
    elif isclass(obj):
        doc += f"\n\nInherited from `{get_name(super_cls(obj))}`.\n\n"
        is_data_cls = is_dataclass(obj)
        if is_data_cls:
            doc += "Is a data class.\n\n"
        elif is_enum(obj):
            doc += "Is an enum class.\n\n"
            title_doc, value_doc = zip(*[
                (e.name, f"`{e.value!r}`") for e in obj
            ])
            doc += table_row(title_doc, value_doc) + '\n'
        hints = get_type_hints(obj)
        if hints:
            for attr in public(hints.keys()):
                inner_links[f"{name}.{attr}"] = linker(name)
            doc += table_row(
                hints.keys(),
                [get_name(v) for v in hints.values()]
            ) + '\n'
        for attr_name in public(dir(obj), not is_data_cls):
            if attr_name not in hints:
                sub_doc.append(get_stub_doc(obj, attr_name, level + 1, name))
    elif callable(obj):
        doc += '()\n\n' + make_table(obj)
    elif is_property(obj):
        doc += "\n\nIs a property.\n\n"
    else:
        return ""
    my_doc = docstring(obj)
    if my_doc:
        # Docstring in pyi
        doc += my_doc
    else:
        doc += self_doc.get(name, "")
    if sub_doc:
        doc += '\n\n' + '\n\n'.join(sub_doc)
    return doc


def get_orig_doc(parent: Any, name: str, prefix: str = "") -> None:
    """Preload original docstrings."""
    obj = getattr(parent, name)
    if prefix:
        name = f"{prefix}.{name}"
    doc = docstring(obj)
    if doc:
        self_doc[name] = doc
    if isclass(obj):
        hints = get_type_hints(obj)
        for attr_name in public(dir(obj), not is_dataclass(obj)):
            if attr_name not in hints:
                get_orig_doc(obj, attr_name, name)


def replace_keywords(doc: str, ignore_module: List[str]) -> str:
    """Replace keywords from docstring."""
    for name in reversed(ignore_module):
        doc = doc.replace(name + '.', "")
    for word, re_word in (
        ('NoneType', 'None'),
        ('Ellipsis', '...'),
    ):
        doc = doc.replace(word, re_word)
    return doc


def import_from(name: str) -> StandardModule:
    """Import the module from name."""
    try:
        return cast(StandardModule, import_module(name))
    except ImportError:
        logger.warn(f"load module failed: {name}")
        return StandardModule(name)


def load_file(code: str, mod: ModuleType) -> bool:
    """Load file into the module."""
    try:
        sys_modules[get_name(mod)] = mod
        exec(compile(code, '', 'exec',
                     flags=annotations.compiler_flag), mod.__dict__)
    except ImportError:
        return False
    except Exception as e:
        _, _, tb = exc_info()
        stack: FrameSummary = extract_tb(tb)[-1]
        line = code.splitlines()[int(stack.line)]
        raise RuntimeError(f"{line}\n{e}") from None
    return True


def load_stubs(m: StandardModule) -> None:
    """Load all pyi files."""
    modules = {}
    root = m.__path__[0]
    if root in loaded_path:
        return
    loaded_path.add(root)
    for file in listdir(root):
        if not file.endswith('.pyi'):
            continue
        with open(join(root, file), 'r', encoding='utf-8') as f:
            code = f.read()
        modules[get_name(m) + '.' + file[:-len('.pyi')]] = code
    module_names = list(modules)
    while module_names:
        name = module_names.pop()
        logger.debug(f"Load stub: {name}")
        code = modules[name]
        mod = ModuleType(name)
        if not load_file(code, mod):
            module_names.insert(0, name)
    # Reload root module
    name = get_name(m)
    with open(m.__file__, 'r', encoding='utf-8') as f:
        load_file(f.read(), m)
    sys_modules[name] = m


def get_level(name: str) -> int:
    """Return the level of the module name."""
    return name.count('.')


def load_root(root_name: str, root_module: str) -> str:
    """Root module docstring."""
    modules = {root_name: import_from(root_module)}
    root_path = modules[root_name].__path__
    ignore_module = ['typing', root_module]
    for info in walk_packages(root_path, root_module + '.'):
        m = import_from(info.name)
        name = get_name(m)
        ignore_module.append(name)
        if hasattr(m, '__all__'):
            modules[name] = m
    doc = f"# {root_name} API\n\n"
    module_names = sorted(modules, key=get_level)
    for n in reversed(module_names):
        m = modules[n]
        for name in public(m.__all__):
            get_orig_doc(m, name)
        load_stubs(m)
    for n in module_names:
        m = modules[n]
        doc += f"## Module `{get_name(m)}`\n\n{docstring(m)}\n\n"
        doc += replace_keywords('\n\n'.join(
            get_stub_doc(m, name, 3) for name in public(m.__all__)
        ), ignore_module) + '\n\n'
    return doc.rstrip() + '\n'


def basename(name: str) -> str:
    """Get base name."""
    sname = name.rsplit('.', maxsplit=1)
    if len(sname) == 1:
        return name
    else:
        return sname[1]


def ref_link(doc: str) -> str:
    """Create the reference and clear the links."""
    ref = ""
    for title, reformat in inner_links.items():
        if search(rf"(?<!\\)\[{title}]", doc):
            ref += f"[{title}]: #{reformat}\n"
            continue
        title = basename(title)
        if title in inner_links:
            continue
        if search(rf"(?<!\\)\[{title}]", doc):
            ref += f"[{title}]: #{reformat}\n"
    inner_links.clear()
    return ref


def gen_api(
    root_names: Dict[str, str],
    prefix: str = 'docs',
    dry: bool = False
) -> None:
    """Generate API.

    Module format:
    Parsing `__all__` list in each module, mark the public names.
    Other names and the module don't has `__all__` will be ignored.
    If an object has no docstring, the object will be ignored.
    Please try to pack into a class, a function or a generator.

    Inner links syntax:
    Use `[name]`, `[attribute]` or `[class.attribute]` syntax to link
    the name or attributes in the same module.
    """
    if not isdir(prefix):
        logger.debug(f"Create directory: {prefix}")
        mkdir(prefix)
    for name, module in root_names.items():
        path = join(prefix, f"{module.replace('_', '-')}-api.md")
        logger.debug(f"Load root: {module}")
        doc = sub(r"\n\n+", "\n\n", load_root(name, module))
        ref = ref_link(doc)
        if ref:
            doc += '\n' + ref
        if dry:
            logger.debug(doc)
        else:
            logger.debug(f"Write file: {path}")
            with open(path, 'w+', encoding='utf-8') as f:
                f.write(doc)
        # Unload modules
        for m_name in set(sys_modules) - unload_modules:
            del sys_modules[m_name]
