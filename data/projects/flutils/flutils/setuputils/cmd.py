import os
import shlex
import shutil
import sys
from typing import (
    ClassVar,
    Generator,
    List,
    Tuple,
    Type,
    Union,
)

from setuptools import Command

from .cfg import SetupCfgCommandConfig
from ..cmdutils import run


def _get_path(cmd: str) -> str:
    if cmd.startswith(os.path.sep):
        if os.path.isfile(cmd) is True:
            out = cmd
        else:
            raise FileNotFoundError('Unable to find the file: %r' % cmd)
    else:
        out = ''
        path = shutil.which(cmd)
        if path is not None:
            out = str(path)

    if out:
        if os.access(out, os.X_OK) is False:
            raise PermissionError(
                'You do not have execute permission to run the file: %r'
                % out
            )
        return out
    raise FileNotFoundError(
        'Unable to find the file path for the command: %r'
        % cmd
    )


def _each_command(
        commands: Union[List[str], Tuple[str, ...]]
) -> Generator[Tuple[str, ...], None, None]:
    for command in commands:
        command = command.strip()
        hold = []
        for x, part in enumerate(shlex.split(command)):
            if x == 0:
                hold.append(_get_path(part))
            else:
                hold.append(part)
        if hold:
            yield tuple(hold)


_DIVIDER = '\n\n{:-<79}\n'.format('')


def _show_command(
        command: Tuple[str, ...],
) -> None:
    print(_DIVIDER)
    for x, part in enumerate(command):
        if x == 0:
            print('{}\n'.format(part))
        else:
            print('  {}\n'.format(part))
    print('\n\n')


# pylint: disable=W0613
# noinspection PyUnusedLocal
def _initialize_options(self) -> None:
    pass


# noinspection PyUnusedLocal
def _finalize_options(self) -> None:
    pass


def _run(self) -> None:
    for command in _each_command(self.commands):
        _show_command(command)
        val = run(command)
        if val != 0:
            sys.exit(val)
            return
    sys.exit(0)


_type = type  # Allows for easy mocking of type.


def build_setup_cfg_command_class(
        setup_command_cfg: SetupCfgCommandConfig
) -> Type[Command]:
    setup_klass = _type(
        'SetupCfgCommand',
        (object,),
        {
            '__annotations__': {
                'name': ClassVar[str],
                'root_path': ClassVar[str],
                'description': ClassVar[str],
                'user_options': ClassVar[List[str]],
                'commands': ClassVar[Tuple[str, ...]],
            },
            '__module__': __name__,
            '__doc__': None,
            'name': setup_command_cfg.name,
            'root_path': '',
            'description': setup_command_cfg.description,
            'user_options': [],
            'commands': setup_command_cfg.commands,
            'initialize_options': _initialize_options,
            'finalize_options': _finalize_options,
            'run': _run,
        }
    )
    klass_name = '%sCommand' % setup_command_cfg.camel
    klass = _type(klass_name, (setup_klass, Command), {})
    return klass
