import keyword
import unittest
from unittest.mock import (
    Mock,
    patch,
)

from flutils.moduleutils import _validate_attr_identifier


class TestValidateAttrIdentifier(unittest.TestCase):

    def test_validate_attr_identifier__00(self) -> None:
        arg = ''
        line = ''
        exp = ''
        ret = _validate_attr_identifier(arg, line)
        self.assertEqual(
            ret,
            exp,
            msg=(
                f'\n\n'
                f'_validate_attr_identifier({arg!r}, {line!r})\n'
                f'expected: {exp!r}\n'
                f'     got: {ret!r}\n'
            )
        )

    def test_validate_attr_identifier__01(self) -> None:
        arg = 'a_name'
        line = ''
        exp = 'a_name'
        ret = _validate_attr_identifier(arg, line)
        self.assertEqual(
            ret,
            exp,
            msg=(
                f'\n\n'
                f'_validate_attr_identifier({arg!r}, {line!r})\n'
                f'expected: {exp!r}\n'
                f'     got: {ret!r}\n'
            )
        )

    def test_validate_attr_identifier__02(self) -> None:
        arg = '-arg'
        line = ''
        with self.assertRaises(AttributeError):
            _validate_attr_identifier(arg, line)

    def test_validate_attr_identifier__03(self) -> None:
        patcher = patch(
            'flutils.moduleutils.keyword.iskeyword',
            return_value=True
        )
        iskeyword = patcher.start()
        self.addCleanup(patcher.stop)
        with self.assertRaises(AttributeError):
            _validate_attr_identifier('try', '')
        iskeyword.assert_called_once_with('try')

    def test_validate_attr_identifier__04(self) -> None:
        patcher = patch(
            'flutils.moduleutils.keyword.iskeyword',
            return_value=False
        )
        iskeyword = patcher.start()
        self.addCleanup(patcher.stop)
        patcher = patch(
            'flutils.moduleutils._BUILTIN_NAMES',
            new=['__a_builtin_name__']
        )
        patcher.start()
        self.addCleanup(patcher.stop)

        with self.assertRaises(AttributeError):
            _validate_attr_identifier('__a_builtin_name__', '')
        iskeyword.assert_called_once_with('__a_builtin_name__')

    def test_validate_attr_identifier__05(self) -> None:
        patcher = patch(
            'flutils.moduleutils.keyword.iskeyword',
            return_value=False
        )
        iskeyword = patcher.start()
        self.addCleanup(patcher.stop)
        patcher = patch(
            'flutils.moduleutils._BUILTIN_NAMES',
            new=['__a_builtin_name__']
        )
        patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.moduleutils._DUNDERS',
            new=['__version__']
        )
        patcher.start()
        self.addCleanup(patcher.stop)

        with self.assertRaises(AttributeError):
            _validate_attr_identifier('__version__', '')
        iskeyword.assert_called_once_with('__version__')
