# type: ignore[override]

import re
from itertools import chain
from sys import hexversion
from textwrap import TextWrapper
from typing import (
    List,
    Optional,
    Sequence,
    cast,
)

# If the python version is >= 3.8
if hexversion >= 0x03080000:
    from functools import cached_property
else:
    from .decorators import cached_property  # type: ignore[misc]

__all__ = ['len_without_ansi', 'AnsiTextWrapper']

_ANSI_RE = re.compile('(\x1b\\[[0-9;:]+[ABCDEFGHJKSTfhilmns])')


def len_without_ansi(seq: Sequence) -> int:
    """Return the character length of the given
    :obj:`Sequence <typing.Sequence>` without counting any ANSI codes.

    *New in version 0.6*

    Args:
         seq (:obj:`Sequence <typing.Sequence>`): A string or a list/tuple
             of strings.

    :rtype:
        :obj:`int`

    Example:
        >>> from flutils.txtutils import len_without_ansi
        >>> text = '\\x1b[38;5;209mfoobar\\x1b[0m'
        >>> len_without_ansi(text)
        6
    """
    if hasattr(seq, 'capitalize'):
        _text: str = cast(str, seq)
        seq = [c for c in _ANSI_RE.split(_text) if c]
    seq = [c for c in chain(*map(_ANSI_RE.split, seq)) if c]
    seq = cast(Sequence[str], seq)
    out = 0
    for text in seq:
        if hasattr(text, 'capitalize'):
            if text.startswith('\x1b[') and text.endswith('m'):
                continue
            else:
                out += len(text)
    return out


class AnsiTextWrapper(TextWrapper):
    """A :obj:`TextWrapper <textwrap.TextWrapper>` object that correctly
    wraps text containing ANSI codes.


    *New in version 0.6*

    Args:
        width (int, optional): The maximum length of wrapped lines.
            As long as there are no individual words in the input text
            longer than this given ``width``,
            :obj:`~flutils.txtutils.AnsiTextWrapper`
            guarantees that no output line will be longer than ``width``
            characters.  Defaults to: ``70``
        initial_indent (str, optional): Text that will be prepended
            to the first line of wrapped output. Counts towards the
            length of the first line. An empty string value will not
            indent the first line.  Defaults to: ``''`` an empty string.
        subsequent_indent (str, optional): Text that will be prepended
            to all lines of wrapped output except the first. Counts
            towards the length of each line except the first.
            Defaults to: ``''`` an empty string.
        expand_tabs (bool, optional): If :obj:`True`, then all tab
            characters in text will be expanded to spaces using the
            :obj:`expandtabs <str.expandtabs>`.  Also see the ``tabsize``
            argument.  Defaults to: :obj:`True`.
        replace_whitespace (bool, optional): If :obj:`True`, after tab
            expansion but before wrapping, the wrap() method will replace
            each whitespace character with a single space. The whitespace
            characters replaced are as follows: tab, newline, vertical
            tab, form-feed, and carriage return (``'\\t\\n\\v\\f\\r'``).
            Defaults to: :obj:`True`.
        fix_sentence_endings (bool, optional): If :obj:`True`,
            :obj:`~flutils.txtutils.AnsiTextWrapper`
            attempts to detect sentence endings and
            ensure that sentences are always separated by exactly two
            spaces. This is generally desired for text in a monospaced
            font. However, the sentence detection algorithm is imperfect;
            it assumes that a sentence ending consists of a lowercase
            letter followed by one of '.', '!', or '?', possibly
            followed by one of '"' or "'", followed by a space.
            Defaults to: :obj:`False`.
        break_long_words (bool, optional): If :obj:`True`, then words
            longer than width will be broken in order to ensure that no
            lines are longer than width. If it is :obj:`False`, long words
            will not be broken, and some lines may be longer than width.
            (Long words will be put on a line by themselves, in order to
            minimize the amount by which width is exceeded.)
            Defaults to: :obj:`True`.
        drop_whitespace (bool, optional): If :obj:`True`, whitespace at
            the beginning and ending of every line (after wrapping but
            before indenting) is dropped. Whitespace at the beginning of
            the paragraph, however, is not dropped if non-whitespace
            follows it. If whitespace being dropped takes up an entire
            line, the whole line is dropped. Defaults to: :obj:`True`
        break_on_hyphens (bool, optional): If :obj:`True`, wrapping will
            occur preferably on whitespaces and right after hyphens in
            compound words, as it is customary in English. If
            :obj:`false`, only whitespaces will be considered as
            potentially good places for line breaks, but you need to set
            ``break_long_words`` to :obj:`False` if you want truly
            insecable words.  Defaults to: :obj:`True`.
        tabsize (int, optional): If ``expand_tabs`` is :obj:`True`, then
            all tab characters in text will be expanded to zero or more
            spaces, depending on the current column and the given tab size.
            Defaults to: ``8``.
        max_lines (:obj:`int` or :obj:`None`, optional): If not :obj:`None`,
            then the output will contain at most ``max_lines lines``, with
            ``placeholder`` appearing at the end of the output.
            Defaults to: :obj:`None`.
        placeholder (str, optional): Text that will appear at the end of
            the output text if it has been truncated.
            Defaults to: ``' [...]'``

    Note:
        The ``initial_indent``, ``subsequent_indent`` and ``placeholder``
        parameters can also contain ANSI codes.

    Note:
        If ``expand_tabs`` is :obj:`False` and ``replace_whitespace``
        is :obj:`True`, each tab character will be replaced by a single
        space, which is not the same as tab expansion.

    Note:
        If ``replace_whitespace`` is :obj:`False`, newlines may appear
        in the middle of a line and cause strange output. For this reason,
        text should be split into paragraphs (using :obj:`str.splitlines`
        or similar) which are wrapped separately.

    Example:
        Use :obj:`~flutils.txtutils.AnsiTextWrapper` the same way as using
        :obj:`TextWrapper <textwrap.TextWrapper>`::

            from flutils.txtutils import AnsiTextWrapper
            text = (
                '\\x1b[31m\\x1b[1m\\x1b[4mLorem ipsum dolor sit amet, '
                'consectetur adipiscing elit. Cras fermentum maximus '
                'auctor. Cras a varius ligula. Phasellus ut ipsum eu '
                'erat consequat posuere.\\x1b[0m Pellentesque habitant '
                'morbi tristique senectus et netus et malesuada fames ac '
                'turpis egestas. Maecenas ultricies lacus id massa '
                'interdum dignissim. Curabitur \\x1b[38;2;55;172;230m '
                'efficitur ante sit amet nibh consectetur, consequat '
                'rutrum nunc\\x1b[0m egestas. Duis mattis arcu eget orci '
                'euismod, sit amet vulputate ante scelerisque. Aliquam '
                'ultrices, turpis id gravida vestibulum, tortor ipsum '
                'consequat mauris, eu cursus nisi felis at felis. '
                'Quisque blandit lacus nec mattis suscipit. Proin sed '
                'tortor ante.  Praesent fermentum orci id dolor '
                '\\x1b[38;5;208meuismod, quis auctor nisl sodales.\\x1b[0m'
            )
            wrapper = AnsiTextWrapper(width=40)
            wrapped_text = wrapper.fill(text)
            print(wrapped_text)

        The output:

            .. image:: ../static/AnsiTextWrapper_example_result.png
               :scale: 75%

    """

    def __init__(
            self,
            width: int = 70,
            initial_indent: str = '',
            subsequent_indent: str = '',
            expand_tabs: bool = True,
            replace_whitespace: bool = True,
            fix_sentence_endings: bool = False,
            break_long_words: bool = True,
            drop_whitespace: bool = True,
            break_on_hyphens: bool = True,
            tabsize: int = 8,
            *,
            max_lines: Optional[int] = None,
            placeholder: str = ' [...]'
    ) -> None:
        self.__initial_indent: str = ''
        self.__subsequent_indent: str = ''
        self.__placeholder: str = ''
        self.width: int = width
        self.initial_indent = initial_indent
        self.subsequent_indent = subsequent_indent
        self.expand_tabs: bool = expand_tabs
        self.replace_whitespace: bool = replace_whitespace
        self.fix_sentence_endings: bool = fix_sentence_endings
        self.break_long_words: bool = break_long_words
        self.drop_whitespace: bool = drop_whitespace
        self.break_on_hyphens: bool = break_on_hyphens
        self.tabsize: int = tabsize
        self.max_lines: Optional[int] = max_lines
        self.placeholder = placeholder

    @property  # type: ignore[override]
    def initial_indent(self) -> str:  # type: ignore
        return self.__initial_indent

    @initial_indent.setter
    def initial_indent(self, value: str) -> None:
        self.__initial_indent = value
        if 'initial_indent_len' in self.__dict__.keys():
            del self.__dict__['initial_indent_len']

    @cached_property
    def initial_indent_len(self) -> int:
        if not self.initial_indent:
            return 0
        return len_without_ansi(self.initial_indent)

    @property  # type: ignore[override]
    def subsequent_indent(self) -> str:  # type: ignore
        return self.__subsequent_indent

    @subsequent_indent.setter
    def subsequent_indent(self, value: str) -> None:
        self.__subsequent_indent = value
        if 'subsequent_indent_len' in self.__dict__.keys():
            del self.__dict__['subsequent_indent_len']

    @cached_property
    def subsequent_indent_len(self) -> int:
        if not self.subsequent_indent:
            return 0
        return len_without_ansi(self.subsequent_indent)

    @property  # type: ignore[override]
    def placeholder(self) -> str:  # type: ignore
        return self.__placeholder

    @placeholder.setter
    def placeholder(self, value: str) -> None:
        self.__placeholder = value
        if 'placeholder_len' in self.__dict__.keys():
            del self.__dict__['placeholder_len']

    @cached_property
    def placeholder_len(self) -> int:
        if not self.placeholder.lstrip():
            return 0
        return len_without_ansi(self.placeholder)

    def _split(self, text: str) -> List[str]:
        """Override to split on ANSI codes."""
        chunks = super()._split(text)
        # The following code describes the following list comprehension:
        #
        # for chunk in chunks:
        #     for c in _ANSI_RE.split(chunk):
        #         if c:
        #             out.append(c)
        # return out
        return [c for c in chain(*map(_ANSI_RE.split, chunks)) if c]

    def _wrap_chunks(self, chunks: List[str]) -> List[str]:

        lines = []
        if self.width <= 0:
            raise ValueError("invalid width %r (must be > 0)" % self.width)
        if self.max_lines is not None:
            if self.max_lines > 1:
                indent = self.subsequent_indent
            else:
                indent = self.initial_indent
            indent_len = len_without_ansi(indent)
            _placeholder_len = len_without_ansi(self.placeholder.lstrip())
            if indent_len + _placeholder_len > self.width:
                raise ValueError('placeholder too large for max width')
            del _placeholder_len

        # Arrange in reverse order so items can be efficiently popped
        # from a stack of chucks.
        chunks.reverse()

        while chunks:

            # Start the list of chunks that will make up the current line.
            # cur_len is just the length of all the chunks in cur_line.
            cur_line = []
            cur_len = 0

            # Figure out which static string will prefix this line.
            if lines:
                indent = self.subsequent_indent
            else:
                indent = self.initial_indent

            indent_len = len_without_ansi(indent)

            # Maximum width for this line.
            width = self.width - indent_len

            # First chunk on line is whitespace -- drop it, unless this
            # is the very beginning of the text (ie. no lines started yet).
            if self.drop_whitespace and chunks[-1].strip() == '' and lines:
                del chunks[-1]

            while chunks:
                l = len_without_ansi(chunks[-1])

                # Can at least squeeze this chunk onto the current line.
                if cur_len + l <= width:
                    cur_line.append(chunks.pop())
                    cur_len += l
                    continue

                # Nope, this line is full.
                else:
                    break

            # The current line is full, and the next chunk is too big to
            # fit on *any* line (not just this one).
            if chunks and len_without_ansi(chunks[-1]) > width:
                self._handle_long_word(chunks, cur_line, cur_len, width)
                cur_len = sum(map(len_without_ansi, cur_line))

            # If the last chunk on this line is all whitespace, drop it.
            if (self.drop_whitespace and
                    cur_line and
                    cur_line[-1].strip() == ''):
                cur_len -= len_without_ansi(cur_line[-1])
                del cur_line[-1]

            if cur_line:
                if (self.max_lines is None or
                        len(lines) + 1 < self.max_lines or
                        (not chunks or
                         self.drop_whitespace and
                         len(chunks) == 1 and
                         not chunks[0].strip()) and cur_len <= width):
                    # Convert current line back to a string and store it in
                    # list of all lines (return value).
                    lines.append(indent + ''.join(cur_line))
                else:

                    # Add the placeholder to the current line if it fits.
                    # If it does NOT fit, remove each chunk until it does.
                    while cur_line:
                        # If the current line's last chunk has a length
                        # greater than zero; and, the length of the current
                        # line plus the length of the placeholder is less
                        # than or equal to the maximum length for this line...
                        if (cur_line[-1].strip() and
                                cur_len + self.placeholder_len <= width):
                            # Add the placeholder to the current line's chunks
                            cur_line.append(self.placeholder)
                            # Concatenate the indent and the combined
                            # current line's chunks into a single line.
                            # Then add this line to the list of lines.
                            lines.append(indent + ''.join(cur_line))
                            break

                        cur_len -= len_without_ansi(cur_line[-1])
                        # delete the current line's last chunk
                        del cur_line[-1]

                    # Because the placeholder could NOT fit on the current
                    # line, try to add the place holder on the previous line.
                    else:
                        if lines:
                            # Get the previous line
                            prev_line = lines[-1].rstrip()
                            # Get the previous line length
                            prev_line_len = len_without_ansi(prev_line)

                            # If the previous line's length plus the
                            # placeholder's length is less than the
                            # allowed line width...
                            if (prev_line_len + self.placeholder_len <=
                                    self.width):
                                # Add the placeholder at the end of the
                                # previous line
                                lines[-1] = prev_line + self.placeholder
                                break
                        lines.append(indent + self.placeholder.lstrip())
                    break

        return lines

    def wrap(self, text: str) -> List[str]:
        """Wraps the single paragraph in the given ``text`` so every line is
        at most ``width`` characters long. All wrapping options are taken
        from instance attributes of the
        :obj:`~flutils.txtutils.AnsiTextWrapper` instance.

        Args:
            text (str): The text to be wrapped.

        Returns:
            A ``List[str]`` of output lines, without final newlines.
            If the wrapped output has no content, the returned list is
            empty.
        """
        return super().wrap(text)

    def fill(self, text: str) -> str:
        """Wraps a single paragraph.

        Args:
            text (str): The text to be wrapped.

         Returns:
              A single :obj:`str` containing the wrapped paragraph.
        """
        return super().fill(text)
