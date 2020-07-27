import errno
import fcntl
import os
import pty
import shlex
import shutil
import struct
import sys
import termios
from itertools import chain
from select import select
from subprocess import Popen
from typing import (
    Any,
    IO,
    List,
    Optional,
    Sequence,
    TextIO,
    cast,
)

__all__ = ['run']


def _set_size(
        fd: int,
        columns: int = 80,
        lines: int = 20
) -> None:
    """Using the passed in file descriptor (of tty), set the terminal
    size to that of the current terminal size.  If the current
    terminal size cannot be found the given defaults will be used.
    """
    # The following was adapted from: https://stackoverflow.com/a/6420070
    size = struct.pack("HHHH", lines, columns, 0, 0)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, size)  # type: ignore[call-overload]


def run(
        command: Sequence,
        stdout: Optional[IO] = None,
        stderr: Optional[IO] = None,
        columns: int = 80,
        lines: int = 24,
        force_dimensions: bool = False,
        interactive: bool = False,
        **kwargs: Any
) -> int:
    """Run the given command line command and return the command's
    return code.

    When the given ``command`` is executed, the command's stdout and
    stderr outputs are captured in a pseudo terminal.  The captured
    outputs are then added to this function's ``stdout`` and ``stderr``
    IO objects.

    This function will capture any ANSI escape codes in the output of
    the given command.  This even includes ANSI colors.

    Args:
        command (str, List[str], Tuple[str]): The command to execute.
        stdout (:obj:`typing.IO`, optional):  An input/output stream
            that will hold the command's ``stdout``.  Defaults to:
            :obj:`sys.stdout <sys.stdout>`; which will output
            the command's ``stdout`` to the terminal.
        stderr (:obj:`typing.IO`, optional):  An input/output stream
            that will hold the command's ``stderr``.  Defaults to:
            :obj:`sys.stderr <sys.stderr>`; which will output
            the command's ``stderr`` to the terminal.
        columns (int, optional): The number of character columns the pseudo
            terminal may use.  If ``force_dimensions`` is :obj:`False`, this
            will be the fallback columns value when the the current terminal's
            column size cannot be found.  If ``force_dimensions`` is
            :obj:`True`, this will be actual character column value.
            Defaults to: ``80``.
        lines (int, optional): The number of character lines the pseudo
            terminal may use.  If ``force_dimensions`` is :obj:`False`, this
            will be the fallback lines value when the the current terminal's
            line size cannot be found.  If ``force_dimensions`` is :obj:`True`,
            this will be actual character lines value.  Defaults to: ``24``.
        force_dimensions (bool, optional): This controls how the given
            ``columns`` and ``lines`` values are to be used.  A value of
            :obj:`False` will use the given ``columns`` and ``lines`` as
            fallback values if the current terminal dimensions cannot be
            successfully queried.  A value of :obj:`True` will resize the
            pseudo terminal using the given ``columns`` and ``lines`` values.
            Defaults to: :obj:`False`.
        interactive (bool, optional): A value of :obj:`True` will
            interactively run the given ``command``.  Defaults to:
            :obj:`False`.
        **kwargs: Any additional key-word-arguments used with
            :obj:`Popen <subprocess.Popen>`.  ``stdout`` and ``stderr``
            will not be used if given in ``**kwargs``.  Defaults to: ``{}``.

    Returns:
        int: The return value from running the given ``command``

    Raises:
        RuntimeError: When using ``interactive=True`` and the ``bash``
            executable cannot be located.
        OSError: Any errors raised when tring to read the pseudo terminal.

    Example:
        An example using :obj:`~flutils.cmdutils.run` in code::

            from flutils.cmdutils import run
            from io import BytesIO
            import sys
            import os

            home = os.path.expanduser('~')
            with BytesIO() as stream:
                return_code = run(
                    'ls "%s"' % home,
                    stdout=stream,
                    stderr=stream
                )
                text = stdout.getvalue()
            text = text.decode(sys.getdefaultencoding())
            if return_code == 0:
                print(text)
            else:
                print('Error: %s' % text)
    """
    # Handle bytes
    if hasattr(command, 'decode'):
        raise TypeError(
            "The given 'command' must be of type: str, List[str] or "
            "Tuple[str]."
        )
    # Handle str
    cmd: List[str]
    if hasattr(command, 'capitalize'):
        command = cast(str, command)
        cmd = list(shlex.split(command))
    else:
        cmd = list(command)

    if interactive is True:
        bash = shutil.which('bash')
        if not bash:
            raise RuntimeError(
                "Unable to run the command:  %r, in interactive mode "
                "because 'bash' could NOT be found on the system."
                % ' '.join(command)
            )
        cmd = [bash, '-i', '-c'] + cmd

    if stdout is None:
        stdout = sys.stdout
    stdout = cast(IO, stdout)

    if stderr is None:
        stderr = sys.stderr
    stderr = cast(IO, stderr)

    if force_dimensions is False:
        columns, lines = shutil.get_terminal_size(
            fallback=(columns, lines)
        )

    # The following is adapted from: https://stackoverflow.com/a/31953436

    masters, slaves = zip(pty.openpty(), pty.openpty())

    try:
        # Resize the pseudo terminals to the size of the current terminal
        for fd in chain(masters, slaves):
            _set_size(
                fd,
                columns=columns,
                lines=lines
            )

        kwargs['stdout'] = slaves[0]
        kwargs['stderr'] = slaves[1]

        if 'stdin' not in kwargs.keys():
            kwargs['stdin'] = slaves[0]

        with Popen(cmd, **kwargs) as p:

            for fd in slaves:
                os.close(fd)  # no input
            readable = {
                masters[0]: stdout,
                masters[1]: stderr,
            }
            while readable:
                for fd in select(readable, [], [])[0]:
                    try:
                        data = os.read(fd, 1024)  # read available
                    except OSError as e:
                        if e.errno != errno.EIO:
                            raise
                        del readable[fd]  # EIO means EOF on some systems
                    else:
                        if not data:  # EOF
                            del readable[fd]
                        else:
                            if hasattr(readable[fd], 'encoding'):
                                obj = readable[fd]
                                obj = cast(TextIO, obj)
                                data_str = data.decode(
                                    obj.encoding
                                )
                                readable[fd].write(data_str)
                            else:
                                readable[fd].write(data)
                            readable[fd].flush()
    finally:
        for fd in chain(masters, slaves):
            try:
                os.close(fd)
            except OSError:
                pass
    return p.returncode
