import asyncio
from typing import Any

__all__ = ['cached_property']


# noinspection PyPep8Naming
class cached_property:
    """A property decorator that is only computed once per instance and then
    replaces itself with an ordinary attribute.

    Deleting the attribute resets the property.

    Note:
        In Python 3.8 the :obj:`functools.cached_property` decorator was
        added. It is recommended to use the built-in
        :obj:`functools.cached_property`; provided you're using
        Python >= 3.8.  :obj:`~flutils.decorators.cached_property` remains
        for use with Python 3.6 and 3.7.

    Example:

        Code::

            from flutils.decorators import cached_property

            class MyClass:

                def __init__(self):
                    self.x = 5

                @cached_property
                def y(self):
                    return self.x + 1

        Usage:

            >>> obj = MyClass()
            >>> obj.y
            6

    *New in version 0.2.0*

    This decorator is a derivative work of
    `cached_property <https://bit.ly/2R9U3Qa>`__ and is:

    `Copyright © 2015 Daniel Greenfeld; All Rights Reserved
    <https://bit.ly/2CwtJM1>`__

    Also this decorator is a derivative work of
    `cached_property  <https://bit.ly/2JbYB5L>`__ and is:

    `Copyright © 2011 Marcel Hellkamp <https://bit.ly/2ECEO0M>`__

    """

    def __init__(self, func):
        self.__doc__ = getattr(func, "__doc__")
        self.func = func

    def __get__(self, obj: Any, cls):
        if obj is None:
            return self

        if asyncio.iscoroutinefunction(self.func):
            return self._wrap_in_coroutine(obj)

        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value

    def _wrap_in_coroutine(self, obj):

        @asyncio.coroutine
        def wrapper():
            future = asyncio.ensure_future(self.func(obj))
            obj.__dict__[self.func.__name__] = future
            return future

        return wrapper()
