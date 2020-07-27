import unittest
from collections import UserString
from keyword import kwlist
from types import SimpleNamespace

from flutils.validators import validate_identifier


class TestValidateIdentifier(unittest.TestCase):

    def test_integration_validate_identifier(self):
        try:
            validate_identifier('foo')
        except TypeError as e:
            self.fail(
                "'validate_identifier()' raised TypeError unexpectedly! %s"
                % e
            )
        except SyntaxError as e:
            self.fail(
                "'validate_identifier()' raised SyntaxError unexpectedly! %s"
                % e
            )

    def test_integration_validate_identifier_user_string(self):
        try:
            validate_identifier(UserString('bar'))
        except TypeError as e:
            self.fail(
                "'validate_identifier()' raised TypeError unexpectedly! %s"
                % e
            )
        except SyntaxError as e:
            self.fail(
                "'validate_identifier()' raised SyntaxError unexpectedly! %s"
                % e
            )

    def test_integration_validate_identifier_invalid_type(self):
        vals = (
            None,
            33,
            33.33,
            list(),
            tuple(),
            SimpleNamespace(),
            dict(a=5),
        )
        for val in vals:
            with self.assertRaises(TypeError):
                validate_identifier(val)

    def test_integration_validate_identifier_underscore_raises(self):
        with self.assertRaises(SyntaxError):
            validate_identifier('_foo', allow_underscore=False)

    def test_integration_validate_identifier_keyword_raises(self):
        for val in kwlist:
            with self.assertRaises(SyntaxError):
                validate_identifier(val)

    def test_integration_validate_identifier_builtin_raises(self):
        names = tuple(filter(
            lambda x: x.startswith('__') and x.endswith('__'),
            dir('__builtins__')
        ))
        for val in names:
            with self.assertRaises(SyntaxError):
                validate_identifier(val)

    def test_integration_validate_identifier_empty_raises(self):
        vals = (
            '',
            ' ',
            '\t'
        )
        for val in vals:
            with self.assertRaises(SyntaxError):
                validate_identifier(val)

    def test_integration_validate_identifier_digit_raises(self):
        vals = (
            '0',
            '05g',
            '6foo'
        )
        for val in vals:
            with self.assertRaises(SyntaxError):
                validate_identifier(val)

    def test_integration_validate_identifier_invalid_raises(self):
        vals = (
            'a-b',
            'c.d',
            'e=f',
            'g+h',
            '{adf}',
            'j*k'
        )
        for val in vals:
            with self.assertRaises(SyntaxError):
                validate_identifier(val)
