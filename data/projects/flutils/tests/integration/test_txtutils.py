import unittest

# noinspection PyProtectedMember
from flutils.txtutils import (
    AnsiTextWrapper,
    len_without_ansi,
)


def _build_msg(expected: str, got: str) -> str:
    return '\n\n<Expected:>\n%s\n<Got:>\n%s\n<End>\n' % (expected, got)


class TestTextUtilsLenWithoutAnsi(unittest.TestCase):

    def test_list_with_ansi(self) -> None:
        chunks = ['foo', ' ', '\x1b[31m', 'bar', '\x1b[0m']
        res = len_without_ansi(chunks)
        self.assertEqual(res, 7)

    def test_list_without_ansi(self) -> None:
        chunks = ['foo']
        res = len_without_ansi(chunks)
        self.assertEqual(res, 3)

    def test_string_with_ansi(self) -> None:
        chunks = '\x1b[38;5;209mfoobar\x1b[0m'
        res = len_without_ansi(chunks)
        self.assertEqual(res, 6)

    def test_string_without_ansi(self) -> None:
        chunks = 'foo bar'
        res = len_without_ansi(chunks)
        self.assertEqual(res, 7)


class TestTextUtilsAnsiTextWrapper(unittest.TestCase):

    def test_instantiation(self) -> None:
        kwargs = {
            'width': 80,
            'initial_indent': 'foo: ',
            'subsequent_indent': '     ',
            'expand_tabs': False,
            'replace_whitespace': False,
            'fix_sentence_endings': True,
            'break_long_words': False,
            'drop_whitespace': False,
            'break_on_hyphens': True,
            'tabsize': 6,
            'max_lines': 5,
            'placeholder': ' [....]'
        }
        obj = AnsiTextWrapper(**kwargs)
        for key, exp in kwargs.items():
            val = getattr(obj, key)
            msg = '\n\n attribute %r is set to %r expected %r' % (
                key,
                val,
                exp,
            )
            self.assertEqual(exp, val, msg=msg)

    def test_initial_indent_len_with_ansi(self) -> None:
        kwargs = {
            'initial_indent': '\x1b[31mfoo: bar\x1b[0m',
        }
        obj = AnsiTextWrapper(**kwargs)
        self.assertEqual(obj.initial_indent_len, 8)

    def test_initial_indent_len_without_ansi(self) -> None:
        kwargs = {
            'initial_indent': 'foo: ',
        }
        obj = AnsiTextWrapper(**kwargs)
        self.assertEqual(obj.initial_indent_len, 5)

    def test_initial_indent_attribute_change(self) -> None:
        kwargs = {
            'initial_indent': '\x1b[31mfoo: bar\x1b[0m',
        }
        obj = AnsiTextWrapper(**kwargs)
        self.assertEqual(obj.initial_indent_len, 8)
        obj.initial_indent = 'foo: '
        self.assertEqual(obj.initial_indent_len, 5)

    def test_initial_indent_empty(self) -> None:
        obj = AnsiTextWrapper()
        self.assertEqual(obj.initial_indent_len, 0)

    def test_subsequent_indent_len_with_ansi(self) -> None:
        kwargs = {
            'subsequent_indent': '\x1b[31mfoo: bar\x1b[0m',
        }
        obj = AnsiTextWrapper(**kwargs)
        self.assertEqual(obj.subsequent_indent_len, 8)

    def test_subsequent_indent_len_without_ansi(self) -> None:
        kwargs = {
            'subsequent_indent': 'foo: ',
        }
        obj = AnsiTextWrapper(**kwargs)
        self.assertEqual(obj.subsequent_indent_len, 5)

    def test_subsequent_indent_attribute_change(self) -> None:
        kwargs = {
            'subsequent_indent': '\x1b[31mfoo: bar\x1b[0m',
        }
        obj = AnsiTextWrapper(**kwargs)
        self.assertEqual(obj.subsequent_indent_len, 8)
        obj.subsequent_indent = 'foo: '
        self.assertEqual(obj.subsequent_indent_len, 5)

    def test_subsequent_indent_empty(self) -> None:
        obj = AnsiTextWrapper()
        self.assertEqual(obj.subsequent_indent_len, 0)

    def test_placeholder_len_with_ansi(self) -> None:
        kwargs = {
            'placeholder': '\x1b[31mfoo: bar\x1b[0m',
        }
        obj = AnsiTextWrapper(**kwargs)
        self.assertEqual(obj.placeholder_len, 8)

    def test_placeholder_len_without_ansi(self) -> None:
        kwargs = {
            'placeholder': 'foo: ',
        }
        obj = AnsiTextWrapper(**kwargs)
        self.assertEqual(obj.placeholder_len, 5)

    def test_placeholder_attribute_change(self) -> None:
        kwargs = {
            'placeholder': '\x1b[31mfoo: bar\x1b[0m',
        }
        obj = AnsiTextWrapper(**kwargs)
        self.assertEqual(obj.placeholder_len, 8)
        obj.placeholder = 'foo: '
        self.assertEqual(obj.placeholder_len, 5)

    def test_placeholder_empty(self) -> None:
        obj = AnsiTextWrapper(placeholder='')
        self.assertEqual(obj.placeholder_len, 0)

    def test_width_40(self) -> None:
        # The expected result wrapped at 40 columns.
        exp = (
            'Lorem ipsum dolor sit amet, consectetur\n'
            'adipiscing elit. Cras fermentum maximus\n'
            'auctor. Cras a varius ligula. Phasellus\n'
            'ut ipsum eu erat consequat posuere.\n'
            'Pellentesque habitant morbi tristique\n'
            'senectus et netus et malesuada fames ac\n'
            'turpis egestas. Maecenas ultricies lacus\n'
            'id massa interdum dignissim. Curabitur\n'
            'efficitur ante sit amet nibh\n'
            'consectetur, consequat rutrum nunc\n'
            'egestas. Duis mattis arcu eget orci\n'
            'euismod, sit amet vulputate ante\n'
            'scelerisque. Aliquam ultrices, turpis id\n'
            'gravida vestibulum, tortor ipsum\n'
            'consequat mauris, eu cursus nisi felis\n'
            'at felis. Quisque blandit lacus nec\n'
            'mattis suscipit. Proin sed tortor ante.\n'
            'Praesent fermentum orci id dolor\n'
            'euismod, quis auctor nisl sodales.'
        )
        # Copy exp and replace newlines with a space to create the
        # argument for wrapper.fill
        arg = exp.replace('\n', ' ')
        wrapper = AnsiTextWrapper(width=40)
        res = wrapper.fill(arg)
        msg = _build_msg(exp, res)
        self.assertEqual(exp, res, msg=msg)

    def test_width_44_with_indent(self) -> None:
        # The expected result wrapped at 44 columns
        exp = (
            '   Lorem ipsum dolor sit amet, consectetur\n'
            '  adipiscing elit.Cras fermentum maximus\n'
            '  auctor.Cras a varius ligula.Phasellus ut\n'
            '  ipsum eu erat consequat posuere.\n'
            '  Pellentesque habitant morbi tristique\n'
            '  senectus et netus et malesuada fames ac\n'
            '  turpis egestas.Maecenas ultricies lacus id\n'
            '  massa interdum dignissim.Curabitur\n'
            '  efficitur ante sit amet nibh consectetur,\n'
            '  consequat rutrum nunc egestas.Duis mattis\n'
            '  arcu eget orci euismod, sit amet vulputate\n'
            '  ante scelerisque.Aliquam ultrices, turpis\n'
            '  id gravida vestibulum, tortor ipsum\n'
            '  consequat mauris, eu cursus nisi felis at\n'
            '  felis.Quisque blandit lacus nec mattis\n'
            '  suscipit.Proin sed tortor ante.Praesent\n'
            '  fermentum orci id dolor euismod, quis\n'
            '  auctor nisl sodales.'
        )
        # Copy exp and remove the indents on each line to create the
        # argument for wrapper.fill
        arg = '\n'.join(map(lambda x: x.lstrip(), exp.splitlines()))
        arg = arg.replace('\n', ' ')
        wrapper = AnsiTextWrapper(
            width=44,
            initial_indent='   ',
            subsequent_indent='  '
        )
        res = wrapper.fill(arg)
        msg = _build_msg(exp, res)
        self.assertEqual(exp, res, msg=msg)

    def test_width_0_raises(self) -> None:
        with self.assertRaises(ValueError):
            wrapper = AnsiTextWrapper(width=0)
            wrapper.fill('foo bar foo bar')

    def test_width_3_with_indent_raises(self) -> None:
        with self.assertRaises(ValueError):
            wrapper = AnsiTextWrapper(
                width=3,
                initial_indent=' ' * 10,
                max_lines=1
            )
            wrapper.fill('foo bar foo bar')

    def test_max_lines_of_5(self) -> None:
        # The expected result wrapped at 40 columns.
        exp = (
            'Lorem ipsum dolor sit amet, consectetur\n'
            'adipiscing elit. Cras fermentum maximus\n'
            'auctor. Cras a varius ligula. Phasellus\n'
            'ut ipsum eu erat consequat posuere.\n'
            'Pellentesque habitant morbi tristique'
        )
        arg = exp.replace('\n', ' ')
        wrapper = AnsiTextWrapper(width=40, max_lines=5)
        res = wrapper.fill(arg)
        msg = _build_msg(exp, res)
        self.assertEqual(exp, res, msg=msg)

    def test_max_lines_of_3_with_placeholder(self) -> None:
        # This tests the last 'while-else' in _wrap_chunks
        text = (
            'Lorem ipsum dolor sit amet, consectetur\n'
            'adipiscing elit. Cras fermentum maximus\n'
            'auctor. Cras a varius ligula. Phasellus\n'
            'ut ipsum eu erat consequat posuere.\n'
            'Pellentesque habitant morbi tristique\n'
            'senectus et netus et malesuada fames ac\n'
            'turpis egestas. Maecenas ultricies lacus\n'
            'id massa interdum dignissim. Curabitur\n'
            'efficitur ante sit amet nibh\n'
            'consectetur, consequat rutrum nunc\n'
            'egestas. Duis mattis arcu eget orci\n'
            'euismod, sit amet vulputate ante\n'
            'scelerisque. Aliquam ultrices, turpis id\n'
            'gravida vestibulum, tortor ipsum\n'
            'consequat mauris, eu cursus nisi felis\n'
            'at felis. Quisque blandit lacus nec\n'
            'mattis suscipit. Proin sed tortor ante.\n'
            'Praesent fermentum orci id dolor\n'
            'euismod, quis auctor nisl sodales.'
        )

        arg = text.replace('\n', ' ')
        exp = (
            'Lorem ipsum dolor sit amet, consectetur\n'
            'adipiscing elit. Cras fermentum maximus\n'
            '..................................'
        )
        wrapper = AnsiTextWrapper(width=40, max_lines=3, placeholder='.' * 34)
        res = wrapper.fill(arg)
        msg = _build_msg(exp, res)
        self.assertEqual(exp, res, msg=msg)

    def test_max_lines_of_3_placeholder_with_long_word(self) -> None:
        # This tests the very last 'if' statement in _wrap_chunks
        text = (
            'Lorem ipsum dolor sit amet, consectetur\n'
            'adipiscing elit. Cras fermentum\n'
            '1234567890123456789012345678901234567890\n'
            'senectus et netus et malesuada fames ac'
        )
        arg = text.replace('\n', ' ')
        exp = (
            'Lorem ipsum dolor sit amet, consectetur\n'
            'adipiscing elit. Cras fermentum [...]'
        )
        wrapper = AnsiTextWrapper(width=40, max_lines=3)
        res = wrapper.fill(arg)
        msg = _build_msg(exp, res)
        self.assertEqual(exp, res, msg=msg)

    def test_max_lines_of_five_with_placeholder(self) -> None:
        text = (
            'Lorem ipsum dolor sit amet, consectetur\n'
            'adipiscing elit. Cras fermentum maximus\n'
            'auctor. Cras a varius ligula. Phasellus\n'
            'ut ipsum eu erat consequat posuere.\n'
            'Pellentesque habitant morbi tristique\n'
            'senectus et netus et malesuada fames ac\n'
            'turpis egestas. Maecenas ultricies lacus\n'
            'id massa interdum dignissim. Curabitur\n'
            'efficitur ante sit amet nibh\n'
            'consectetur, consequat rutrum nunc\n'
            'egestas. Duis mattis arcu eget orci\n'
            'euismod, sit amet vulputate ante\n'
            'scelerisque. Aliquam ultrices, turpis id\n'
            'gravida vestibulum, tortor ipsum\n'
            'consequat mauris, eu cursus nisi felis\n'
            'at felis. Quisque blandit lacus nec\n'
            'mattis suscipit. Proin sed tortor ante.\n'
            'Praesent fermentum orci id dolor\n'
            'euismod, quis auctor nisl sodales.'
        )
        arg = text.replace('\n', ' ')
        exp = (
            'Lorem ipsum dolor sit amet, consectetur\n'
            'adipiscing elit. Cras fermentum maximus\n'
            'auctor. Cras a varius ligula. Phasellus\n'
            'ut ipsum eu erat consequat posuere.\n'
            'Pellentesque habitant morbi [...]'
        )
        wrapper = AnsiTextWrapper(width=40, max_lines=5)
        res = wrapper.fill(arg)
        msg = _build_msg(exp, res)
        self.assertEqual(exp, res, msg=msg)

    def test_large_word(self) -> None:
        arg = (
            'Lorem ipsum dolor sit amet, consectetur '
            'adipiscing elit. Cras fermentum maximus '
            'auctor. Cras a varius ligula. Phasellus '
            'ut ipsum eu erat consequat posuere. '
            'Duis Pellentesquehabitantmorbitristiques'
            'enectusetnetusetmalesuadafamesacblandit '
            'turpis egestas. Maecenas ultricies lacus '
            'id massa interdum dignissim. Curabitur '
            'efficitur ante sit amet nibh '
            'consectetur, consequat rutrum nunc '
            'egestas. Duis mattis arcu eget orci '
            'euismod, sit amet vulputate ante '
            'scelerisque. Aliquam ultrices, turpis id '
            'gravida vestibulum, tortor ipsum '
            'consequat mauris, eu cursus nisi felis '
            'at felis. Quisque blandit lacus nec '
            'mattis suscipit. Proin sed tortor ante. '
            'Praesent fermentum orci id dolor '
            'euismod, quis auctor nisl sodales.'
        )
        exp = (
            'Lorem ipsum dolor sit amet, consectetur\n'
            'adipiscing elit. Cras fermentum maximus\n'
            'auctor. Cras a varius ligula. Phasellus\n'
            'ut ipsum eu erat consequat posuere. Duis\n'
            'Pellentesquehabitantmorbitristiquesenect\n'
            'usetnetusetmalesuadafamesacblandit\n'
            'turpis egestas. Maecenas ultricies lacus\n'
            'id massa interdum dignissim. Curabitur\n'
            'efficitur ante sit amet nibh\n'
            'consectetur, consequat rutrum nunc\n'
            'egestas. Duis mattis arcu eget orci\n'
            'euismod, sit amet vulputate ante\n'
            'scelerisque. Aliquam ultrices, turpis id\n'
            'gravida vestibulum, tortor ipsum\n'
            'consequat mauris, eu cursus nisi felis\n'
            'at felis. Quisque blandit lacus nec\n'
            'mattis suscipit. Proin sed tortor ante.\n'
            'Praesent fermentum orci id dolor\n'
            'euismod, quis auctor nisl sodales.'
        )
        wrapper = AnsiTextWrapper(width=40)
        res = wrapper.fill(arg)
        msg = _build_msg(exp, res)
        self.assertEqual(exp, res, msg=msg)

    def test_width_40_ansi_all(self) -> None:
        # The expected result wrapped at 40 columns.
        exp = (
            '\x1b[31mLorem ipsum dolor sit amet, consectetur\n'
            'adipiscing elit. Cras fermentum maximus\n'
            'auctor. Cras a varius ligula. Phasellus\n'
            'ut ipsum eu erat consequat posuere.\n'
            'Pellentesque habitant morbi tristique\n'
            'senectus et netus et malesuada fames ac\n'
            'turpis egestas. Maecenas ultricies lacus\n'
            'id massa interdum dignissim. Curabitur\n'
            'efficitur ante sit amet nibh\n'
            'consectetur, consequat rutrum nunc\n'
            'egestas. Duis mattis arcu eget orci\n'
            'euismod, sit amet vulputate ante\n'
            'scelerisque. Aliquam ultrices, turpis id\n'
            'gravida vestibulum, tortor ipsum\n'
            'consequat mauris, eu cursus nisi felis\n'
            'at felis. Quisque blandit lacus nec\n'
            'mattis suscipit. Proin sed tortor ante.\n'
            'Praesent fermentum orci id dolor\n'
            'euismod, quis auctor nisl sodales.\x1b[0m'
        )
        # Copy exp and replace newlines with a space to create the
        # argument for wrapper.fill
        arg = exp.replace('\n', ' ')
        wrapper = AnsiTextWrapper(width=40)
        res = wrapper.fill(arg)
        msg = _build_msg(exp, res)
        self.assertEqual(exp, res, msg=msg)

    def test_width_40_ansi_mixed(self) -> None:
        # The expected result wrapped at 40 columns.
        exp = (
            '\x1b[31m\x1b[1m\x1b[4mLorem ipsum dolor sit amet, consectetur\n'
            'adipiscing elit. Cras fermentum maximus\n'
            'auctor. Cras a varius ligula. Phasellus\n'
            'ut ipsum eu erat consequat posuere.\x1b[0m\n'
            'Pellentesque habitant morbi tristique\n'
            'senectus et netus et malesuada fames ac\n'
            'turpis egestas. Maecenas ultricies lacus\n'
            'id massa interdum dignissim. Curabitur\x1b[38;2;55;172;230m\n'
            'efficitur ante sit amet nibh\n'
            'consectetur, consequat rutrum nunc\x1b[0m\n'
            'egestas. Duis mattis arcu eget orci\n'
            'euismod, sit amet vulputate ante\n'
            'scelerisque. Aliquam ultrices, turpis id\n'
            'gravida vestibulum, tortor ipsum\n'
            'consequat mauris, eu cursus nisi felis\n'
            'at felis. Quisque blandit lacus nec\n'
            'mattis suscipit. Proin sed tortor ante.\n'
            'Praesent fermentum orci id dolor\x1b[38;5;208m\n'
            'euismod, quis auctor nisl sodales.\x1b[0m'
        )
        # Copy exp and replace newlines with a space to create the
        # argument for wrapper.fill
        arg = exp.replace('\n', ' ')
        wrapper = AnsiTextWrapper(width=40)
        res = wrapper.fill(arg)
        msg = _build_msg(exp, res)
        self.assertEqual(exp, res, msg=msg)

    def test_width_40_indent_ansi_mixed(self) -> None:
        text = (
            '\x1b[31m\x1b[1m\x1b[4mLorem ipsum dolor sit amet, consectetur\n'
            'adipiscing elit. Cras fermentum maximus\n'
            'auctor. Cras a varius ligula. Phasellus\n'
            'ut ipsum eu erat consequat posuere.\x1b[0m\n'
            'Pellentesque habitant morbi tristique\n'
            'senectus et netus et malesuada fames ac\n'
            'turpis egestas. Maecenas ultricies lacus\n'
            'id massa interdum dignissim. Curabitur\x1b[38;2;55;172;230m\n'
            'efficitur ante sit amet nibh\n'
            'consectetur, consequat rutrum nunc\x1b[0m\n'
            'egestas. Duis mattis arcu eget orci\n'
            'euismod, sit amet vulputate ante\n'
            'scelerisque. Aliquam ultrices, turpis id\n'
            'gravida vestibulum, tortor ipsum\n'
            'consequat mauris, eu cursus nisi felis\n'
            'at felis. Quisque blandit lacus nec\n'
            'mattis suscipit. Proin sed tortor ante.\n'
            'Praesent fermentum orci id dolor\x1b[38;5;208m\n'
            'euismod, quis auctor nisl sodales.\x1b[0m'
        )
        initial_indent = '\x1b[47m\x1b[30m...\x1b[0m'
        exp = (
            '\x1b[47m\x1b[30m...\x1b[0m\x1b[31m\x1b[1m\x1b[4mLorem ipsum '
            'dolor sit amet,\n'
            '\x1b[47m\x1b[30m...\x1b[0mconsectetur adipiscing elit. Cras\n'
            '\x1b[47m\x1b[30m...\x1b[0mfermentum maximus auctor. Cras a\n'
            '\x1b[47m\x1b[30m...\x1b[0mvarius ligula. Phasellus ut ipsum eu\n'
            '\x1b[47m\x1b[30m...\x1b[0merat consequat posuere.\x1b[0m '
            'Pellentesque\n'
            '\x1b[47m\x1b[30m...\x1b[0mhabitant morbi tristique senectus et\n'
            '\x1b[47m\x1b[30m...\x1b[0mnetus et malesuada fames ac turpis\n'
            '\x1b[47m\x1b[30m...\x1b[0megestas. Maecenas ultricies lacus id\n'
            '\x1b[47m\x1b[30m...\x1b[0mmassa interdum dignissim. '
            'Curabitur\x1b[38;2;55;172;230m\n'
            '\x1b[47m\x1b[30m...\x1b[0mefficitur ante sit amet nibh\n'
            '\x1b[47m\x1b[30m...\x1b[0mconsectetur, consequat rutrum '
            'nunc\x1b[0m\n'
            '\x1b[47m\x1b[30m...\x1b[0megestas. Duis mattis arcu eget orci\n'
            '\x1b[47m\x1b[30m...\x1b[0meuismod, sit amet vulputate ante\n'
            '\x1b[47m\x1b[30m...\x1b[0mscelerisque. Aliquam ultrices, turpis\n'
            '\x1b[47m\x1b[30m...\x1b[0mid gravida vestibulum, tortor ipsum\n'
            '\x1b[47m\x1b[30m...\x1b[0mconsequat mauris, eu cursus nisi\n'
            '\x1b[47m\x1b[30m...\x1b[0mfelis at felis. Quisque blandit lacus\n'
            '\x1b[47m\x1b[30m...\x1b[0mnec mattis suscipit. Proin sed tortor\n'
            '\x1b[47m\x1b[30m...\x1b[0mante. Praesent fermentum orci id\n'
            '\x1b[47m\x1b[30m...\x1b[0mdolor\x1b[38;5;208m euismod, quis '
            'auctor nisl\n'
            '\x1b[47m\x1b[30m...\x1b[0msodales.\x1b[0m'
        )
        # Copy exp and replace newlines with a space to create the
        # argument for wrapper.fill
        arg = text.replace('\n', ' ')
        wrapper = AnsiTextWrapper(
            width=40,
            initial_indent=initial_indent,
            subsequent_indent=initial_indent,
        )
        res = wrapper.fill(arg)
        msg = _build_msg(exp, res)
        self.assertEqual(exp, res, msg=msg)

    def test_width_40_indent_ansi_mixed_placeholder(self) -> None:
        text = (
            '\x1b[31m\x1b[1m\x1b[4mLorem ipsum dolor sit amet, consectetur\n'
            'adipiscing elit. Cras fermentum maximus\n'
            'auctor. Cras a varius ligula. Phasellus\n'
            'ut ipsum eu erat consequat posuere.\x1b[0m\n'
            'Pellentesque habitant morbi tristique\n'
            'senectus et netus et malesuada fames ac\n'
            'turpis egestas. Maecenas ultricies lacus\n'
            'id massa interdum dignissim. Curabitur\x1b[38;2;55;172;230m\n'
            'efficitur ante sit amet nibh\n'
            'consectetur, consequat rutrum nunc\x1b[0m\n'
            'egestas. Duis mattis arcu eget orci\n'
            'euismod, sit amet vulputate ante\n'
            'scelerisque. Aliquam ultrices, turpis id\n'
            'gravida vestibulum, tortor ipsum\n'
            'consequat mauris, eu cursus nisi felis\n'
            'at felis. Quisque blandit lacus nec\n'
            'mattis suscipit. Proin sed tortor ante.\n'
            'Praesent fermentum orci id dolor\x1b[38;5;208m\n'
            'euismod, quis auctor nisl sodales.\x1b[0m'
        )
        initial_indent = '\x1b[47m\x1b[30m...\x1b[0m'
        exp = (
            '\x1b[47m\x1b[30m...\x1b[0m\x1b[31m\x1b[1m\x1b[4mLorem ipsum '
            'dolor sit amet,\n'
            '\x1b[47m\x1b[30m...\x1b[0mconsectetur adipiscing elit. Cras\n'
            '\x1b[47m\x1b[30m...\x1b[0mfermentum maximus auctor. Cras a\n'
            '\x1b[47m\x1b[30m...\x1b[0mvarius ligula. Phasellus ut ipsum eu\n'
            '\x1b[47m\x1b[30m...\x1b[0merat consequat posuere.\x1b[0m '
            '\x1b[31m[...]\x1b[0m'
        )
        # Copy exp and replace newlines with a space to create the
        # argument for wrapper.fill
        arg = text.replace('\n', ' ')
        wrapper = AnsiTextWrapper(
            width=40,
            initial_indent=initial_indent,
            subsequent_indent=initial_indent,
            max_lines=5,
            placeholder=' \x1b[31m[...]\x1b[0m'
        )
        res = wrapper.wrap(arg)
        res = '\n'.join(res)
        msg = _build_msg(exp, res)
        self.assertEqual(exp, res, msg=msg)
