import unittest
from collections import (
    OrderedDict,
    UserList,
    namedtuple,
)
from types import SimpleNamespace

from flutils.namedtupleutils import to_namedtuple


class TestToNamedTuple(unittest.TestCase):

    def test_raises(self) -> None:
        items = (
            'test',
            1,
            1.5,
            True,
            None,
        )
        for item in items:
            with self.assertRaises(TypeError):
                to_namedtuple(item)

    def test_namedtuple(self) -> None:
        make = namedtuple('NamedTuple', ('a', 'b'))
        val = make(1, 2)
        res = to_namedtuple(val)
        self.assertEqual(res, val)

    def test_simplenamespace(self) -> None:
        arg = SimpleNamespace()
        arg.a = 1
        arg.b = 2
        make = namedtuple('NamedTuple', ('a', 'b'))
        exp = make(1, 2)
        res = to_namedtuple(arg)
        self.assertEqual(res, exp)

    def test_empty_namedtuple(self) -> None:
        make = namedtuple('NamedTuple', '')
        exp = make()
        arg = make()
        res = to_namedtuple(arg)
        self.assertEqual(res, exp)

    def test_dict(self) -> None:
        obj = {
            'b': 2,
            'a': 1,
            152: 7,
            '_c': 8
        }
        make = namedtuple('NamedTuple', ('a', 'b'))
        val = make(1, 2)
        res = to_namedtuple(obj)
        self.assertEqual(res, val)

    def test_ordereddict(self) -> None:
        arg = OrderedDict()
        arg['c'] = 1
        arg['b'] = 2
        arg['a'] = 3
        make = namedtuple('NamedTuple', ('c', 'b', 'a'))
        exp = make(1, 2, 3)
        res = to_namedtuple(arg)
        msg = (
            "\n\n"
            "to_namedtuple(%r)\n\n"
            "res=%r\n\n"
            "exp=%r\n\n"
            % (arg, res, exp)
        )
        self.assertEqual(res, exp, msg=msg)

    def test_empty_dict(self) -> None:
        arg = {}
        make = namedtuple('NamedTuple', '')
        exp = make()
        res = to_namedtuple(arg)
        self.assertEqual(res, exp)

    def test_list(self) -> None:
        obj_dict = {
            'b': 2,
            'a': 1,
        }
        obj_list = [
            obj_dict,
            3,
            obj_dict
        ]
        make = namedtuple('NamedTuple', ('a', 'b'))
        obj_ntup = make(1, 2)
        val = [
            obj_ntup,
            3,
            obj_ntup
        ]
        res = to_namedtuple(obj_list)
        self.assertEqual(res, val)

    def test_user_list(self) -> None:
        arg = UserList()
        arg.append({'a': 1, 'b': 2})
        arg.append(None)
        arg.append({'a': 1, 'b': 2})

        make = namedtuple('NamedTuple', ('a', 'b'))
        tup = make(1, 2)
        exp = [
            tup,
            None,
            tup,
        ]
        res = to_namedtuple(arg)
        self.assertEqual(res, exp)

    def test_tuple(self) -> None:
        obj_dict = {
            'b': 2,
            'a': 1,
        }
        obj_list = (
            obj_dict,
            'test',
            obj_dict
        )
        make = namedtuple('NamedTuple', ('a', 'b'))
        obj_ntup = make(1, 2)
        val = (
            obj_ntup,
            'test',
            obj_ntup
        )
        res = to_namedtuple(obj_list)
        self.assertEqual(res, val)

    def test_complex(self) -> None:
        arg = {
            'b': 2,
            'a': 1,
            'c': {
                'a': 1,
                'b': 2,
            },
            'd': [
                (
                    {
                        'a': 1,
                        'b': 2,
                    },
                    {
                        'a': 1,
                        'b': 2,
                    },

                ),
                {
                    'a': 1,
                    'b': 2,
                },
                'test',
            ]
        }
        make = namedtuple('NamedTuple', ('a', 'b'))
        obj_ntup = make(1, 2)
        exp_list = [
            (
                obj_ntup,
                obj_ntup,
            ),
            obj_ntup,
            'test'
        ]

        make = namedtuple('NamedTuple', ('a', 'b', 'c', 'd'))
        exp = make(
            1,
            2,
            obj_ntup,
            exp_list
        )
        res = to_namedtuple(arg)
        self.assertEqual(res, exp)
