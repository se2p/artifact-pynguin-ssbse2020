import importlib
import keyword
import sys
from collections import defaultdict
from importlib import util
from importlib.abc import Loader
from importlib.machinery import ModuleSpec
# noinspection PyUnresolvedReferences
from types import ModuleType
from typing import (
    Any,
    DefaultDict,
    Dict,
    Generator,
    List,
    NamedTuple,
    Optional,
    Set,
    Tuple,
    Union,
    cast,
)

__all__ = ['cherry_pick', 'lazy_import_module']

_STRIPPED_DUNDERS = (
    'author',
    'author_email',
    'description',
    'doc',
    'download_url',
    'file',
    'license',
    'loader'
    'maintainer',
    'maintainer_email',
    'path',
    'python_requires',
    'test_suite',
    'url',
    'version'
)

_DUNDERS = tuple(('__%s__' % x for x in _STRIPPED_DUNDERS))
_BUILTIN_NAMES = tuple(filter(
    lambda x: x.startswith('__') and x.endswith('__'),
    dir('__builtins__')
))


def _validate_attr_identifier(
        identifier: str,
        line: str
) -> str:
    identifier = identifier.strip()
    if identifier == '':
        return identifier

    error: str = ''
    # Test if the given 'identifier' is valid to be
    # used as an identifier.
    is_valid: bool = identifier.isidentifier()

    if is_valid is True and keyword.iskeyword(identifier):
        is_valid = False
        error = ' Cannot be a keyword.'

    if is_valid is True and identifier in _BUILTIN_NAMES:
        is_valid = False
        error = ' Cannot be a builtin name.'

    if is_valid is True and identifier in _DUNDERS:
        is_valid = False
        error = ' Cannot be a special dunder.'

    if is_valid is False:
        raise AttributeError(
            f"__attr_map__ contains an invalid item of: {line!r}. "
            f"The identifier, {identifier!r}, is invalid.{error}"
        )
    return identifier


class _AttrMapping(NamedTuple):
    """Typing definition for a namedtuple holding a single attribute map."""

    """The name of the cherry-picking module attribute."""
    attr_name: str

    """The name of the cherry-picked module."""
    mod_name: str

    """The name of the cherry-picked module attribute; can be an empty str."""
    mod_attr_name: str

    """The pre-expanded __attr_map__ item (aka the foreign-name)"""
    item: str


def _expand_attr_map_item(
        foreign_name: str
) -> _AttrMapping:
    """Used with map() to expand foreign-names into a named tuple.

    See the :term:`foreign-name` documentation for the format of this string.

    The tuple contains three parts:

    - attr_name: If applicable, the attribute identifier that will be
      set on the cherry-picking module.
    - mod_name: The fullname of the module to be cherry-picked.
    - mod_attr_name: If applicable the attribute identifier on the
        cherry-picked module that will be bound to the ``attr_name``.
        An empty str value indicates that the entire module will be used.
    """
    if not isinstance(foreign_name, str):
        raise AttributeError(
            '__attr_map__ must be a tuple containing strings.'
        )
    mod, _, attr_name = foreign_name.partition(',')
    mod_name, _, mod_attr_name = mod.strip().partition(':')
    attr_name = _validate_attr_identifier(attr_name, foreign_name)
    mod_name = mod_name.strip()
    mod_attr_name = _validate_attr_identifier(mod_attr_name, foreign_name)
    if attr_name == '':
        if mod_attr_name != '':
            attr_name = mod_attr_name
        else:
            attr_name = mod_name.split('.')[-1]
    return _AttrMapping(
        attr_name,
        mod_name,
        mod_attr_name,
        foreign_name
    )


def _expand_attr_map(
        attr_map: Tuple[str, ...]
) -> Generator[_AttrMapping, None, None]:
    """Generator that expands the given attr_map and yields an _AttrMapping
    named tuple.

    An attr_map is a tuple with each row containing a :term:`foreign-name`
    which is a specially formatted string.
    """
    hold: Set = set()
    for attr_mapping in map(_expand_attr_map_item, attr_map):
        # Do not yield duplicates
        if attr_mapping not in hold:
            hold.add(attr_mapping)
            yield attr_mapping


class _CherryPickMap(NamedTuple):
    """The modules to be cherry picked as the key.  And the value is
    a list of mapping details.
    """
    modules: DefaultDict[str, List[_AttrMapping]]

    """The cherry-picking module attribute identifiers as the key. And the
    value is the module name, which should be the key in ``modules``
    """
    identifiers: Dict[str, str]


class CherryPickError(ImportError):

    def __init__(self, fullname, msg):
        msg = '%s.%s' % (fullname, msg)
        super().__init__(msg)


def _parse_attr_map(
        attr_map: Tuple[str, ...],
        fullname: str
) -> _CherryPickMap:
    """Parse the given tuple, with each row containing a :term:`foreign-name`
    and return info needed for the cherry-picking-module.
    """
    if not isinstance(attr_map, tuple):
        raise CherryPickError(
            fullname,
            '__attr_map__ must be a tuple not %r'
            % type(attr_map).__name__
        )

    modules: DefaultDict = defaultdict(list)
    identifiers: Dict = dict()
    # Catch any AttributeErrors (thrown in the generator) so that
    # more information can be added to the error message.
    try:
        for attr_mapping in _expand_attr_map(attr_map):
            modules[attr_mapping.mod_name].append(attr_mapping)
            if attr_mapping.attr_name in identifiers:
                raise CherryPickError(
                    fullname,
                    '__attr_map__ has the attribute %r defined multiple '
                    'times' % attr_mapping.attr_name
                )
            identifiers[attr_mapping.attr_name] = attr_mapping.mod_name
    except AttributeError as err:
        raise CherryPickError(fullname, '%s' % err)

    return _CherryPickMap(modules, identifiers)


_CHERRY_PICK: str = '__cherry_pick__'

_EMPTY_CHERRY_PICK_MAP = _CherryPickMap(defaultdict(list), dict())


# noinspection PyUnresolvedReferences
class _CherryPickingModule(ModuleType):
    """A module that manages attributes pointing to lazy-loaded-modules
    and lazy-loaded-module-attributes.
    """

    # noinspection PyCallByClass
    def __getattribute__(self, attr: str) -> Any:
        _dict_ = object.__getattribute__(self, '__dict__')
        _cherry_pick_map_: _CherryPickMap = _dict_.get(
            '__cherry_pick_map__',
            _EMPTY_CHERRY_PICK_MAP
        )
        if attr in _cherry_pick_map_.identifiers:
            if _dict_[attr] == _CHERRY_PICK:
                mod_name = _cherry_pick_map_.identifiers[attr]
                module = importlib.import_module(mod_name)
                for attr_mapping in _cherry_pick_map_.modules[mod_name]:
                    if attr_mapping.mod_attr_name:
                        object.__setattr__(
                            self,
                            attr_mapping.attr_name,
                            getattr(module, attr_mapping.mod_attr_name)
                        )
                    else:
                        object.__setattr__(
                            self,
                            attr_mapping.attr_name,
                            module
                        )
        return object.__getattribute__(self, attr)


# noinspection PyAbstractClass,PyUnresolvedReferences
class _CherryPickingLoader(Loader):
    """A custom :obj:`loader <importlib.abc.Loader>` that is used in the
    execution of cherry-picking-modules.
    """

    def create_module(self, spec):
        mod = ModuleType(spec.name)
        mod.__spec__ = spec
        return mod

    # noinspection PyMethodMayBeStatic
    def exec_module(  # pylint: disable=no-self-use
            self,
            module: ModuleType
    ) -> None:
        """Execute the given module in its own namespace."""
        spec = module.__spec__

        # add the parsed attr_map info to the module.
        module.__cherry_pick_map__ = _parse_attr_map(  # type: ignore
            # The attr_map must be in spec.loader_state.
            # It's okay for it to error here.  If it does
            # error then _CherryPickFinder.add was not called.
            spec.loader_state['attr_map'],  # type: ignore
            module.__name__
        )
        # add the un-parsed attr_map to the module
        module.__attr_map__ = spec.loader_state['attr_map']  # type: ignore

        # This variable is used to set module.__all__
        _all_ = list()

        # loop through each attribute name to set the module
        # attribute (of the same name) to a sentinel.
        iden_keys = module.__cherry_pick_map__.identifiers.keys  # type: ignore
        for attr in iden_keys():
            _all_.append(attr)
            setattr(module, attr, _CHERRY_PICK)

        # loop through the additional attributes (set in cherry_pick())
        # and set the module attribute (of the same name) to the value.
        state_items = spec.loader_state['addtl_attrs'].items  # type: ignore
        for key, val in state_items():
            if not key.startswith('_'):
                _all_.append(key)
            setattr(module, key, val)

        module.__all__ = list(sorted(_all_))  # type: ignore

        # Change the module class so that __getattribute__ can be overridden.
        module.__class__ = _CherryPickingModule


class _CherryPickFinder:
    """A Finder that is used by Python's import to provide a
    :obj:`ModuleSpec <importlib.machinery.ModuleSpec>` for a cherry-picking
    module package.

    This finder is a singleton, in that, on first use of
    :obj:`~flutils.cherry_pick` this finder object is added to the top of
    :obj:`sys.meta_path`.  Each subsequent use of :obj:`~flutils.cherry_pick`
    will use the same object.

    This object is used to cache a cherry-picking-module's data from a
    module-package that is using the :obj:`~flutils.cherry_pick` function.

    The :obj:`ModuleSpec <importlib.machinery.ModuleSpec>` created in this
    finder's ``find_spec()`` method, will be set to use the custom
    :obj:`~_CherryPicker <flutils.moduleutils._CherryPick>` loader.
    Additionally, the cached data will be added to the spec's loader_state.
    The loader_state (cached cherry-picking-module data) will be used by
    :obj:`~_CherryPicker <flutils.moduleutils._CherryPick>` loader to create
    the cherry-picked-module.
    """

    def __init__(self):
        self._cache = dict()

    def __repr__(self):
        return "%s.%s" % (__name__, self.__class__.__name__)

    @classmethod
    def load(cls):
        """Make sure this finder is at the top of sys.meta_path."""
        for obj in sys.meta_path:
            if type(obj).__name__ == cls.__name__:
                return obj
        obj = cls()
        sys.meta_path.insert(0, obj)
        return obj

    @classmethod
    def add(
            cls,
            fullname: str,
            origin: str,
            path: Union[str, List],
            attr_map: Tuple[str, ...],
            **addtl_attrs: Any
    ) -> None:
        """Add cherry-picking-module data to the cache."""
        obj = cls.load()
        obj._cache[fullname] = dict(
            fullname=fullname,
            origin=origin,
            path=path,
            attr_map=attr_map,
            addtl_attrs=addtl_attrs
        )

    # noinspection PyUnusedLocal
    def find_spec(
            self,
            fullname: str,
            path: str,  # pylint: disable=unused-argument
            target: str = None  # pylint: disable=unused-argument
    ) -> Union[ModuleSpec, None]:
        """Return a spec for a cherry-picking-module."""
        if fullname in self._cache:
            loader_state = self._cache[fullname]
            kwargs = dict(
                origin=loader_state['origin'],
                loader_state=loader_state,
            )
            loader = _CherryPickingLoader()
            if loader_state['path']:
                kwargs['is_package'] = True

            # ModuleSpec docs: https://bit.ly/2Hlz1dv
            return ModuleSpec(fullname, loader, **kwargs)
        return None


def cherry_pick(
        namespace: dict
) -> None:
    """Replace the calling :term:`cherry-pick-definition package module` with
    a :term:`cherry-picking module`.

    Use this function when there is a need to :term:`cherry-pick` modules.
    This means the loading and executing, of a module, will be postponed
    until an attribute is accessed.

    Args:
        namespace (:obj:`dict`): This should always be set to
            :obj:`globals() <globals>`

    :rtype: :obj:`None`

    .. Warning:: For projects where startup time is critical, this function
        allows for potentially minimizing the cost of loading a module if it
        is never used. For projects where startup time is not essential, the
        use of this function is heavily discouraged due to error messages
        created during loading being postponed and thus occurring out of
        context.

    Example:
        It is recommended to first build the root package (``__init__.py``)
        as a normally desired root package. (Make sure that no functions
        or classes are defined.  If needed, define these in a submodule).  For
        example (``mymodule/__init__.py``)::

            \"""This is the mymodule docstring.\"""

            from mymodule import mysubmoduleone
            import mymodule.mysubmoduletwo as two
            from mymodule.mysubmodulethree import afunction
            from mymodule.mysubmodulethree import anotherfunction as anotherfuc

            MYVAL = 123

        To use the ``cherry_pick`` function, the root package module
        (``__init__.py``) must be converted to a
        :term:`cherry-pick-definition package module`. This example is the
        result of rewriting the root package (above)::

            \"""This is the mymodule docstring.\"""

            from flutils.moduleutils import cherry_pick

            MYVAL = 123

            __attr_map__ = (
                'mymodule.mysubmoduleone',
                'mymodule.mysubmoduletwo,two',
                'mymodule.mysubmodulethree:afunction',
                'mymodule.mysubmodulethree:anotherfunction,anotherfuc'
            )
            __additional_attrs__ = dict(
                MYVAL=MYVAL
            )

            cherry_pick(globals())

        As you can see, the imports were each rewritten to a
        :term:`foreign-name` and placed in the ``__attr_map__`` :obj:`tuple`.

        Then, ``MYVAL`` was put in the ``__additional_attrs__`` dictionary.
        Use this dictionary to pass any values to
        :term:`cherry-picking module`.

        And finally the ``cherry_pick`` function was called with
        :obj:`globals() <globals>` as the only argument.

        The result is the expected usage of ``mymodule``::

            >> import mymodule
            >> mymodule.anotherfunc()
            foo bar

        To test if a cherry-picked module has been loaded, or not::

            >> import sys
            >> sys.modules.get('mymodule.mysubmodulethree')

        If you get nothing back, it means the cherry-picked module has not been
        loaded.

        Please be aware that there are some cases when all of the
        cherry-picked modules will be loaded automatically. Using any
        program that automatically inspects the cherry-picking module
        will cause the all of the cherry-picked modules to be loaded.
        Programs such as ipython and pycharm will do this.
    """
    # Extract data from the namespace that will be cached and used in the
    # creation of the cherry-picking module.
    fullname = namespace.get('__name__')
    fullname = cast(str, fullname)
    origin = namespace.get('__file__', '')
    origin = cast(str, origin)
    path = namespace.get('__path__')
    path = cast(List, path)

    attr_map: Tuple[str, ...] = namespace.get('__attr_map__', tuple())
    if not attr_map or not isinstance(attr_map, tuple):
        raise ImportError(
            '__attr_map__ must be defined as a tuple of strings in %r.'
            % fullname
        )

    # variable to hold any additional attributes to be set on the
    # cherry-picking module.
    addtl_attrs = dict()

    # Extract any relevant dunder values.  The most important value is 'loader'
    # which must be passed through to 'module.__loader__' so that the
    # 'pkg_resources' module can work as intended.  This is not to be confused
    # with 'module.__spec__.loader' which is set to an instance of
    # '_CherryPickingLoader' in the '_CherryPickFinder' class.
    for key in _DUNDERS:
        val: Any = namespace.get(key)
        if val:
            addtl_attrs[key] = val

    spec = util.find_spec(fullname)
    if spec is None:
        raise ImportError(f'Unable to find the spec for {fullname!r}')
    addtl_attrs['__loader__'] = spec.loader

    # Add any additional attributes to be passed to the cherry-picking module.
    additional: Dict[str, Any] = namespace.get(
        '__additional_attrs__',
        dict()
    )
    if not isinstance(additional, dict):
        raise ImportError(
            '__additional_attrs__ must be a dict in %r'
            % fullname
        )
    for key, val in additional.items():
        if not isinstance(key, str):
            raise ImportError(
                '__additional_attrs__ keys must be strings. in %r'
                % fullname
            )
        addtl_attrs[key] = val

    # Add all of the extracted data to the _CherryPickFinder which will be
    # used in the creation and execution of the cherry-picking module.
    _CherryPickFinder.add(
        fullname,
        origin,
        path,
        attr_map,
        **addtl_attrs
    )

    # Reload the module.
    if fullname in sys.modules:
        importlib.reload(sys.modules[fullname])
    else:
        importlib.import_module(fullname)


# noinspection PyUnresolvedReferences
class _LazyModule(ModuleType):
    """A subclass of the module type which triggers loading upon attribute
    access.

    This class is a "derivative work" of the Python
    `importlib.util._LazyModule <https://bit.ly/2EBPI1g>`_, and is:

    `Copyright © 2001-2018 Python Software Foundation; All Rights Reserved
    <https://bit.ly/2JzG17l>`_

    This differs from the ``importlib.util._LazyModule`` in that it tracks
    the state of the Lazy Loaded module and has had some
    `unused code <https://bit.ly/2EARVu6>` removed.
    """

    is_loaded: bool = False

    # noinspection PyCallByClass
    def __getattribute__(self, attr: str) -> Any:
        """Trigger the load of the module and return the attribute."""
        # allow access to is_loaded without triggering the rest of this method.
        if attr == 'is_loaded':
            return object.__getattribute__(self, 'is_loaded')
        # All module metadata must be garnered from __spec__ in order to avoid
        # using mutated values.

        # Stop triggering this method.
        self.__class__ = ModuleType  # type: ignore

        # Get the original name to make sure no object substitution occurred
        # in sys.modules.
        original_name = self.__spec__.name  # type: ignore

        # Figure out exactly what attributes were mutated between the creation
        # of the module and now.
        attrs_then = self.__spec__.loader_state['__dict__']  # type: ignore
        attrs_now = self.__dict__
        attrs_updated = {}

        for key, value in attrs_now.items():

            # Code that set the attribute may have kept a reference to the
            # assigned object, making identity more important than equality.
            if key not in attrs_then:
                attrs_updated[key] = value
            elif id(attrs_now[key]) != id(attrs_then[key]):
                attrs_updated[key] = value  # pragma: no cover
        self.__spec__.loader.exec_module(self)  # type: ignore

        # Indicate that the module is now loaded.
        self.is_loaded = True

        # If exec_module() was used directly there is no guarantee the module
        # object was put into sys.modules.
        if original_name in sys.modules:
            if id(self) != id(sys.modules[original_name]):
                raise ValueError(  # pragma: no cover
                    f"module object for {original_name!r} substituted in "
                    "sys.modules during a lazy load"
                )
        # Update after loading since that's what would happen in an eager
        # loading situation.
        self.__dict__.update(attrs_updated)
        return getattr(self, attr)

    def __delattr__(self, attr: str) -> None:
        """Trigger the load and then perform the deletion."""
        # To trigger the load and raise an exception if the attribute
        # doesn't exist.
        self.__getattribute__(attr)
        delattr(self, attr)


# noinspection PyAbstractClass
class _LazyLoader(Loader):
    """A loader that creates a module which defers loading until attribute
    access.

    This class is a "derivative work" of the Python
    :obj:`importlib.util.LazyLoader`, and is:

    `Copyright © 2001-2018 Python Software Foundation; All Rights Reserved
    <https://bit.ly/2JzG17l>.`_

    This class differs from :obj:`importlib.util.LazyLoader` in that it
    uses the :obj:`~flutils.moduleutils._LazyModule` class and the
    ``factory`` class method was removed.
    """

    @staticmethod
    def __check_eager_loader(loader: Loader) -> None:
        if not hasattr(loader, 'exec_module'):
            raise TypeError(  # pragma: no cover
                'loader must define exec_module()'
            )

    def __init__(self, loader: Loader) -> None:
        self.__check_eager_loader(loader)
        self.loader = loader

    # noinspection PyUnresolvedReferences
    def create_module(self, spec: ModuleSpec) -> Optional[ModuleType]:
        return self.loader.create_module(spec)

    # noinspection PyUnresolvedReferences
    def exec_module(self, module: ModuleType):
        """Make the module load lazily."""
        module.__spec__.loader = self.loader  # type: ignore
        module.__loader__ = self.loader

        # Don't need to worry about deep-copying as trying to set an attribute
        # on an object would have triggered the load,
        # e.g. ``module.__spec__.loader = None`` would trigger a load from
        # trying to access module.__spec__.
        loader_state = dict()
        loader_state['__dict__'] = module.__dict__.copy()
        loader_state['__class__'] = module.__class__  # type: ignore
        module.__spec__.loader_state = loader_state  # type: ignore
        module.__class__ = _LazyModule


# noinspection PyUnresolvedReferences,PyUnusedFunction
def lazy_import_module(
        name: str,
        package: Optional[str] = None
) -> ModuleType:
    """Lazy import a python module.

    Args:
        name (:obj:`str`): specifies what module to import in absolute or
            relative terms (e.g. either ``pkg.mod`` or ``..mod``).
        package (:obj:`str`, optional): If ``name`` is specified in relative
            terms, then the ``package`` argument must be set to the name of the
            package which is to act as the anchor for resolving the package
            name.  Defaults to ``None``.

    Raises:
        ImportError: if the given ``name`` and ``package`` can not be loaded.

    :rtype:
        :obj:`Module <types.ModuleType>`

        * The lazy imported module with the execution of it's loader postponed
          until an attribute accessed.

    .. Warning:: For projects where startup time is critical, this function
        allows for potentially minimizing the cost of loading a module if it
        is never used. For projects where startup time is not essential then
        use of this function is heavily discouraged due to error messages
        created during loading being postponed and thus occurring out of
        context.

    Examples:

        >>> from flutils.moduleutils import lazy_import_module
        >>> module = lazy_import_module('mymodule')

        Relative import:

        >>> module = lazy_import_module('.mysubmodule', package='mymodule')
    """
    if isinstance(package, str) and package:
        package = cast(str, package)
        fullname = util.resolve_name(name, package=package)
    else:
        fullname = util.resolve_name(name, package='')

    # Return the module if it's already been imported.
    if fullname in sys.modules:
        return sys.modules[fullname]

    # Find the spec for the desired module
    spec = util.find_spec(fullname)
    if spec is None:
        raise ImportError("name=%r package=%r" % (name, package))

    # Use the _LazyLoader to wrap the real loader. The _LazyLoader
    # will only load and execute the module when an attribute is
    # accessed.
    loader = spec.loader
    loader = cast(Loader, loader)
    lazy_loader = _LazyLoader(loader)

    # Within a Python import there is the process of module
    # creation.  This is basically a two step process that
    # is handled by the loaders <https://bit.ly/2Jz8E4C>:
    #   1. Create a module namespace from a spec.
    #      (see types.ModuleType <https://bit.ly/2qlJyyf>)
    #   2. Execute the module in it's own namespace.
    #
    # All loaders SHOULD have a create_module(spec) which
    # creates the namespace.  Additionally, all loaders
    # should have the exec_module(module) which executes
    # the module.
    #
    # In the case of any file loader the creation of a
    # module namespace would require the loading of the.
    # file.  Which would defeat the purpose of lazy loading.
    # in this case the create_module(spec) method will
    # return None.
    #
    # These two methods were added to the loaders
    # in Python (version 3.4) and some of the loaders will
    # not make use of these methods.  These loaders still
    # use the load_module(fullname) method, which combines
    # the two steps (mentioned above) into one method. In
    # this case the create_module(spec) may not exist or
    # will return None.

    # Create a module namespace.
    if hasattr(spec.loader, 'create_module'):
        module = lazy_loader.create_module(spec)
    else:
        module = None

    # If the loader doesn't make use of the create_module
    # method, then create a very simple module namespace.
    if module is None:
        # create a dummy module to work with
        module = ModuleType(fullname)

    module.__spec__ = spec

    # Have the _LazyLoader execute the module.  This
    # preps the module namespace to be lazy loaded
    # and makes the module a _LazyModule namespace.
    lazy_loader.exec_module(module)

    # Add the module to the python module map.
    sys.modules[fullname] = module
    return module
