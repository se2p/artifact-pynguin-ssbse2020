import os
from configparser import (
    ConfigParser,
    NoOptionError,
    NoSectionError,
)
from traceback import (
    FrameSummary,
    extract_stack,
)
from typing import (
    Dict,
    Generator,
    List,
    NamedTuple,
    Optional,
    Tuple,
    Union,
    cast,
)

from flutils.strutils import underscore_to_camel


class SetupCfgCommandConfig(NamedTuple):
    name: str
    camel: str
    description: str
    commands: Tuple[str, ...]


def _each_setup_cfg_command_section(
        parser: ConfigParser
) -> Generator[Tuple[str, str], None, None]:
    for section in parser.sections():
        section = cast(str, section)
        section = section.strip()
        if section.startswith('setup.command.'):
            command_name = '.'.join(section.split('.')[2:])
            if command_name:
                yield section, command_name


def _each_setup_cfg_command(
        parser: ConfigParser,
        format_kwargs: Dict[str, str]
) -> Generator[SetupCfgCommandConfig, None, None]:
    for section, command_name in _each_setup_cfg_command_section(parser):
        commands: List[str] = []
        options: List[str] = parser.options(section)
        for option in ('command', 'commands'):
            if option in options:
                val: str = parser.get(section, option)
                val = val.format(**format_kwargs)
                commands += list(
                    filter(len, map(lambda x: x.strip(), val.splitlines()))
                )
        if commands:
            cmd_name = ''
            if 'name' in options:
                cmd_name = parser.get(section, 'name')
            cmd_name = cmd_name or command_name
            cmd_name = cmd_name.format(name=format_kwargs['name'])

            description = ''
            if 'description' in options:
                description = parser.get(section, 'description')
            description = description.format(**format_kwargs)

            title = cmd_name.replace('.', '_')
            title = title.replace('-', '_')

            if title.isidentifier() is True:
                yield SetupCfgCommandConfig(
                    cmd_name,
                    underscore_to_camel(title, lower_first=False),
                    description,
                    tuple(commands)
                )


def _get_name(
        parser: ConfigParser,
        setup_cfg_path: str,
) -> str:
    try:
        out = parser.get('metadata', 'name')
    except NoSectionError:
        raise LookupError(
            "The config file, %r, is missing the 'metadata' section."
            % setup_cfg_path
        )
    except NoOptionError:
        raise LookupError(
            "The 'metadata', section is missing the 'name' option in "
            "the config file, %r."
            % setup_cfg_path
        )
    if not out:
        raise LookupError(
            "The 'metadata', section's, 'name' option is not set in "
            "the config file, %r."
            % setup_cfg_path
        )
    return out


def _validate_setup_dir(setup_dir: str) -> None:
    """Validates the given ``setup_dir``."""
    if os.path.exists(setup_dir) is False:
        raise FileNotFoundError(
            "The given 'setup_dir' of %r does NOT exist."
            % setup_dir
        )
    if os.path.isdir(setup_dir) is False:
        raise NotADirectoryError(
            "The given 'setup_dir' of %r is NOT a directory."
            % setup_dir
        )
    path = os.path.join(setup_dir, 'setup.py')
    if os.path.isfile(path) is False:
        raise FileNotFoundError(
            "The given 'setup_dir' of %r does NOT contain a setup.py "
            "file." % setup_dir
        )
    path = os.path.join(setup_dir, 'setup.cfg')
    if os.path.isfile(path) is False:
        raise FileNotFoundError(
            "The given 'setup_dir' of %r does NOT contain a setup.cfg "
            "file." % setup_dir
        )


def _prep_setup_dir(
        setup_dir: Optional[Union[os.PathLike, str]] = None
) -> str:
    """The path to the directory that contains the project's ``setup.py``
    file.
    """
    if setup_dir:
        setup_dir = str(setup_dir)
        _validate_setup_dir(setup_dir)
        return os.path.realpath(setup_dir)

    for fs in extract_stack():
        fs = cast(FrameSummary, fs)
        basename = os.path.basename(fs.filename)
        if basename == 'setup.py':
            setup_dir = str(os.path.dirname(fs.filename))
            _validate_setup_dir(setup_dir)
            return os.path.realpath(setup_dir)
    raise FileNotFoundError(
        "Unable to find the directory that contains the 'setup.py' file."
    )


def each_sub_command_config(
        setup_dir: Optional[Union[os.PathLike, str]] = None
) -> Generator[SetupCfgCommandConfig, None, None]:
    format_kwargs: Dict[str, str] = {
        'setup_dir': _prep_setup_dir(setup_dir),
        'home': os.path.expanduser('~')
    }
    setup_cfg_path = os.path.join(format_kwargs['setup_dir'], 'setup.cfg')
    parser = ConfigParser()
    parser.read(setup_cfg_path)
    format_kwargs['name'] = _get_name(parser, setup_cfg_path)
    path = os.path.join(format_kwargs['setup_dir'], 'setup_commands.cfg')
    if os.path.isfile(path):
        parser = ConfigParser()
        parser.read(path)
    yield from _each_setup_cfg_command(parser, format_kwargs)
