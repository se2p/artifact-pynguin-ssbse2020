import unittest
from collections import (
    ChainMap,
    Counter,
    KeysView,
    OrderedDict,
    UserDict,
    UserList,
    UserString,
    ValuesView,
    defaultdict,
    deque,
    namedtuple,
)
from datetime import (
    date,
    datetime,
)
from decimal import Decimal
from types import SimpleNamespace

from flutils.objutils import (
    has_any_attrs,
    has_any_callables,
    has_attrs,
    has_callables,
    is_list_like,
    is_subclass_of_any,
)


class MockIterable:

    def __init__(self, low, high):
        self.current = low
        self.high = high

    def __iter__(self):
        return self

    def __next__(self):
        if self.current > self.high:
            raise StopIteration
        else:
            self.current += 1
            return self.current


class MockObject:
    pass


class TestHasAttrs(unittest.TestCase):

    def test_integration_has_attrs_true(self):
        obj = dict(a=1, b=2)
        self.assertTrue(has_attrs(obj, 'get', 'items', 'values', 'keys'))

    def test_integration_has_attrs_false(self):
        obj = dict(a=1, b=2)
        self.assertFalse(has_attrs(obj, 'get', 'items', 'vals', 'keys'))


class TestHasAnyAttrs(unittest.TestCase):

    def test_integration_has_any_attrs_true(self):
        obj = dict(a=1, b=2)
        self.assertTrue(has_any_attrs(obj, 'get', 'items', 'values', 'keys'))

    def test_integration_has_any_attrs_false(self):
        obj = dict(a=1, b=2)
        self.assertFalse(has_any_attrs(obj, 'foo', 'vals'))


class TestHasCallables(unittest.TestCase):

    def test_integration_has_callables_true(self):
        obj = dict(a=1, b=2)
        self.assertTrue(has_callables(obj, 'get', 'keys', 'items', 'values'))

    def test_integration_has_callables_false(self):
        obj = dict(a=1, b=2)
        self.assertFalse(has_callables(obj, 'get', 'vals'))

    def test_integration_has_callables_non_callable(self):
        obj = SimpleNamespace()
        obj.test = 5
        self.assertFalse(has_callables(obj, 'test'))


class TestHasAnyCallables(unittest.TestCase):

    def test_integration_has_any_callables_true(self):
        obj = dict(a=1, b=2)
        self.assertTrue(has_any_callables(
            obj, 'get', 'foo', 'items', 'values'))

    def test_integration_has_any_callables_false(self):
        obj = dict(a=1, b=2)
        self.assertFalse(has_any_callables(obj, 'foo', 'bar'))


class TestIsSubclassOfAny(unittest.TestCase):

    def test_integration_is_subclass_of_any_true(self):
        obj = dict(a=1, b=2)
        self.assertTrue(
            is_subclass_of_any(obj.keys(), ValuesView, KeysView, UserList)
        )

    def test_integration_is_subclass_of_any_false(self):
        obj = dict(a=1, b=2)
        self.assertFalse(
            is_subclass_of_any(obj.keys(), ValuesView, UserList)
        )


class TestIslistlike(unittest.TestCase):

    def test_integration_is_list_like_list_true(self):
        obj = [1, 2, 3]
        self.assertTrue(is_list_like(obj))

    def test_integration_is_list_like_tuple_true(self):
        obj = (1, 2, 3)
        self.assertTrue(is_list_like(obj))

    def test_integration_is_list_like_namedtuple_true(self):
        build = namedtuple('test', 'a, b, c')
        obj = build(1, 2, 3)
        self.assertTrue(is_list_like(obj))

    def test_integration_is_list_like_set_true(self):
        obj = set((1, 2, 3))
        self.assertTrue(is_list_like(obj))

    def test_integration_is_list_like_frozenset_true(self):
        obj = frozenset((1, 2, 3))
        self.assertTrue(is_list_like(obj))

    def test_integration_is_list_like_deque_true(self):
        obj = deque((1, 2, 3))
        self.assertTrue(is_list_like(obj))

    def test_integration_is_list_like_iterator_true(self):
        obj = MockIterable(5, 10)
        self.assertTrue(is_list_like(obj))

    def test_integration_is_list_like_values_view_true(self):
        obj = dict(a=1, b=2)
        self.assertTrue(is_list_like(obj.values()))

    def test_integration_is_list_like_keys_view_true(self):
        obj = dict(a=1, b=2)
        self.assertTrue(is_list_like(obj.keys()))

    def test_integration_is_list_like_user_list_true(self):
        obj = UserList((1, 2, 3))
        self.assertTrue(is_list_like(obj))

    def test_integration_is_list_like_dict_false(self):
        obj = dict(a=1, b=2)
        self.assertFalse(is_list_like(obj))

    def test_integration_is_list_like_str_false(self):
        obj = 'test'
        self.assertFalse(is_list_like(obj))

    def test_integration_is_list_like_bytes_false(self):
        obj = b'test'
        self.assertFalse(is_list_like(obj))

    def test_integration_is_list_like_int_false(self):
        obj = 55
        self.assertFalse(is_list_like(obj))

    def test_integration_is_list_like_float_false(self):
        obj = 55.553
        self.assertFalse(is_list_like(obj))

    def test_integration_is_list_like_decimal_false(self):
        obj = Decimal('55.23')
        self.assertFalse(is_list_like(obj))

    def test_integration_is_list_like_datetime_false(self):
        obj = datetime.now()
        self.assertFalse(is_list_like(obj))

    def test_integration_is_list_like_date_false(self):
        obj = datetime.now()
        obj = date(obj.year, obj.month, obj.day)
        self.assertFalse(is_list_like(obj))

    def test_integration_is_list_like_bool_false(self):
        obj = True
        self.assertFalse(is_list_like(obj))

    def test_integration_is_list_like_none_false(self):
        obj = None
        self.assertFalse(is_list_like(obj))

    def test_integration_is_list_like_object_false(self):
        obj = MockObject()
        self.assertFalse(is_list_like(obj))

    def test_integration_is_list_like_chain_map_false(self):
        dict_a = dict(a=1, b=2)
        dict_b = dict(b=40, c=3, d=4, e=5)
        obj = ChainMap(dict_a, dict_b)
        self.assertFalse(is_list_like(obj))

    def test_integration_is_list_like_counter_false(self):
        obj = dict(b=40, c=3, d=4, e=5)
        obj = Counter(obj)
        self.assertFalse(is_list_like(obj))

    def test_integration_is_list_like_defaultdict_false(self):
        s = [('yellow', 1), ('blue', 2), ('yellow', 3), ('blue', 4), ('red', 1)]
        obj = defaultdict(list)
        for k, v in s:
            obj[k].append(v)
        self.assertFalse(is_list_like(obj))

    def test_integration_is_list_like_ordered_dict_false(self):
        obj = dict(b=40, c=3, d=4, e=5)
        obj = OrderedDict(obj.items())
        self.assertFalse(is_list_like(obj))

    def test_integration_is_list_like_user_dict_false(self):
        obj = dict(b=40, c=3, d=4, e=5)
        obj = UserDict(obj.items())
        self.assertFalse(is_list_like(obj))

    def test_integration_is_list_like_user_string_false(self):
        obj = UserString('testing')
        self.assertFalse(is_list_like(obj))
