import unittest
from configparser import (
    ConfigParser,
    NoOptionError,
    NoSectionError,
)
from typing import List
from unittest.mock import (
    Mock,
    PropertyMock,
    patch,
)

# noinspection PyProtectedMember
from flutils.setuputils.cfg import (
    SetupCfgCommandConfig,
    _each_setup_cfg_command,
    _each_setup_cfg_command_section,
    _get_name,
    _prep_setup_dir,
    _validate_setup_dir,
    each_sub_command_config,
)


class TestCfg(unittest.TestCase):

    """This will test ``flutils.setuputils.cfg``

    Some tests in this object are assuming the setup.cfg file looks
    like this::

        [metadata]
        name = raijin
        version = attr: flutils.__version__

        [setup.command.lint]
        description = Verify {name} {setup_dir} {home}
        command = linter {setup_dir} {home} {name}

        [setup.command.a_command]
        name = {name}-style
        commands =
            linter {setup_dir} {home} {name}
            styler {setup_dir}
            another-command

        [setup.command.missing]
        description = This command is missing commands


        [setup.command.multi]
        command = first
        commands =
            second
            third
    """

    def setUp(self) -> None:
        parser = Mock(spec=ConfigParser)
        type(parser).sections = Mock(return_value=[
            'section_1',
            'section_2',
            'metadata',
            'setup.command.lint',
            'setup.command.a_command',
            'setup.command.missing',
            'setup.command.multi'
        ])
        type(parser).options = Mock(side_effect=[
            # parser.options('setup.command.lint')
            ['description', 'command'],
            # parser.options('setup.command.a_command')
            ['name', 'commands'],
            # parser.options('setup.command.missing')
            ['description'],
            # parser.options('setup.command.multi')
            ['command', 'commands'],

        ])
        type(parser).get = Mock(side_effect=[
            # parser.get('setup.command.lint', 'command')
            'linter {setup_dir} {home} {name}',
            # parser.get('setup.command.lint', 'description')
            'Verify {name} {setup_dir} {home}',
            # parser.get('setup.command.a_command', 'commands')
            '\nlinter {setup_dir} {home} {name}\nstyler {'
            'setup_dir}\nanother-command',
            # parser.get('setup.command.a_command', 'name')
            '{name}-style',
            # parser.get('setup.command.multi', 'command')
            'first',
            # parser.get('setup.command.multi', 'commands')
            '\nsecond\nthird',
        ])
        self.parser = parser

        self.kwargs = {
            'name': 'raijin',
            'home': '/home/user',
            'setup_dir': '/home/user/tmp/raijin'
        }

        self.path = '/a/file/path'

    def test_each_setup_cfg_command_section(self) -> None:
        ret = list(_each_setup_cfg_command_section(self.parser))
        exp = [
            ('setup.command.lint', 'lint'),
            ('setup.command.a_command', 'a_command'),
            ('setup.command.missing', 'missing'),
            ('setup.command.multi', 'multi'),
        ]
        self.assertEqual(
            ret,
            exp,
            msg=(
                '\n\n'
                'list(_each_setup_cfg_command_section(self.parser))\n'
                'expected: {exp!r}\n'
                '     got: {ret!r}\n'
            ).format(exp=exp, ret=ret)
        )

    @staticmethod
    def _obj_for_msg(obj: List[SetupCfgCommandConfig]) -> str:
        out = ['[']
        for row in obj:
            out.append('  SetupCfgCommandConfig(')
            for key in row._fields:
                if key == 'commands':
                    out.append('    {}=('.format(key))
                    for val in row.commands:
                        out.append('      {!r},'.format(val))
                    out.append('    ),')
                else:
                    out.append('    {}={!r}'.format(key, getattr(row, key)))
            out.append('  ),')
        out.append(']')
        return '\n'.join(out)

    def test_each_setup_cfg_command(self) -> None:
        patcher = patch(
            'flutils.setuputils.cfg._each_setup_cfg_command_section',
            return_value=[
                ('setup.command.lint', 'lint'),
                ('setup.command.a_command', 'a_command'),
                ('setup.command.missing', 'missing'),
                ('setup.command.multi', 'multi'),
            ]
        )
        patcher.start()
        self.addCleanup(patcher.stop)

        ret = list(_each_setup_cfg_command(self.parser, self.kwargs))
        self.parser.options.assert_any_call('setup.command.multi')
        ret_msg = self._obj_for_msg(ret)
        exp = [
            SetupCfgCommandConfig(
                name='lint',
                camel='Lint',
                description=(
                    'Verify {name} {setup_dir} {home}'
                ).format(**self.kwargs),
                commands=(
                    (
                        'linter {setup_dir} {home} {name}'
                    ).format(**self.kwargs),
                )
            ),
            SetupCfgCommandConfig(
                name='{name}-style'.format(**self.kwargs),
                camel='RaijinStyle',
                description='',
                commands=(
                    (
                        'linter {setup_dir} {home} {name}'
                    ).format(**self.kwargs),
                    (
                        'styler {setup_dir}'
                    ).format(**self.kwargs),
                    'another-command',
                )
            ),
            SetupCfgCommandConfig(
                name='multi',
                camel='Multi',
                description='',
                commands=(
                    'first',
                    'second',
                    'third',
                )
            ),
        ]
        exp_msg = self._obj_for_msg(exp)
        self.assertEqual(
            ret,
            exp,
            msg=(
                '\n\n'
                'list(_each_setup_cfg_command(self.parser))\n\n'
                'expected:\n\n'
                '{exp_msg}\n\n'
                'got:\n\n'
                '{ret_msg}\n\n'
            ).format(exp_msg=exp_msg, ret_msg=ret_msg)
        )

    def test_get_name__0(self) -> None:
        parser = Mock(spec=ConfigParser)
        type(parser).get = Mock(return_value=self.kwargs['name'])

        ret = _get_name(parser, self.path)
        exp = self.kwargs['name']
        self.assertEqual(
            ret,
            exp,
            msg=(
                '\n\n'
                '_get_name(self.parser2, self.path)\n'
                'expected: {exp!r}\n'
                '     got: {ret!r}\n'
            ).format(exp=exp, ret=ret)
        )

    def test_get_name__1(self) -> None:
        parser = Mock(spec=ConfigParser)
        type(parser).get = Mock(side_effect=NoSectionError('metadata'))
        with self.assertRaises(LookupError):
            _get_name(parser, self.path)

    def test_get_name__2(self) -> None:
        parser = Mock(spec=ConfigParser)
        type(parser).get = Mock(side_effect=NoOptionError('name', 'metadata'))
        with self.assertRaises(LookupError):
            _get_name(parser, self.path)

    def test_get_name__3(self) -> None:
        parser = Mock(spec=ConfigParser)
        type(parser).get = Mock(return_value='')
        with self.assertRaises(LookupError):
            _get_name(parser, self.path)

    def test_validate_setup_dir__0(self) -> None:
        with self.assertRaises(FileNotFoundError):
            with patch('os.path.exists', return_value=False):
                _validate_setup_dir('/a/path')

    def test_validate_setup_dir__1(self) -> None:
        with self.assertRaises(NotADirectoryError):
            with patch('os.path.exists', return_value=True):
                with patch('os.path.isdir', return_value=False):
                    _validate_setup_dir('/a/path')

    def test_validate_setup_dir__2(self) -> None:
        with self.assertRaises(FileNotFoundError):
            with patch('os.path.exists', return_value=True):
                with patch('os.path.isdir', return_value=True):
                    with patch('os.path.isfile', return_value=False):
                        _validate_setup_dir('/a/path')

    def test_validate_setup_dir__3(self) -> None:
        values = [True, False]
        with self.assertRaises(FileNotFoundError):
            with patch('os.path.exists', return_value=True):
                with patch('os.path.isdir', return_value=True):
                    with patch('os.path.isfile', side_effect=values):
                        _validate_setup_dir('/a/path')

    def test_prep_setup_dir__0(self) -> None:
        exp = '/a/dir'
        with patch('os.path.realpath', return_value=exp):
            ret = _prep_setup_dir('.')
            self.assertEqual(
                ret,
                exp,
                msg=(
                    "\n\n"
                    "_prep_setup_dir('.')\n"
                    "expected: {exp!r}\n"
                    "     got: {ret!r}\n"
                ).format(exp=exp, ret=ret)
            )

    def test_prep_setup_dir__1(self) -> None:
        frame_summary = Mock()
        type(frame_summary).filename = PropertyMock(
            return_value='/a/dir/path/setup.py'
        )

        patcher = patch(
            'flutils.setuputils.cfg.extract_stack',
            return_value=[frame_summary]
        )
        patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.setuputils.cfg._validate_setup_dir',
            return_value=None
        )
        patcher.start()
        self.addCleanup(patcher.stop)

        exp = '/a/dir/path'
        patcher = patch(
            'flutils.setuputils.cfg.os.path.realpath',
            return_value=exp
        )
        patcher.start()
        self.addCleanup(patcher.stop)

        ret = _prep_setup_dir()
        self.assertEqual(ret, exp)

    def test_prep_setup_dir__2(self) -> None:
        frame_summary = Mock()
        type(frame_summary).filename = PropertyMock(
            return_value='/a/dir/path/a.py'
        )

        patcher = patch(
            'flutils.setuputils.cfg.extract_stack',
            return_value=[frame_summary]
        )
        patcher.start()
        self.addCleanup(patcher.stop)

        with self.assertRaises(FileNotFoundError):
            _prep_setup_dir()

    def test_each_sub_command_config(self) -> None:

        # prep_setup_dir
        patcher = patch(
            'flutils.setuputils.cfg._prep_setup_dir',
            return_value=self.kwargs['setup_dir']
        )
        prep_setup_dir = patcher.start()
        self.addCleanup(patcher.stop)

        # expanduser
        patcher = patch(
            'flutils.setuputils.cfg.os.path.expanduser',
            return_value=self.kwargs['home']
        )
        expanduser = patcher.start()
        self.addCleanup(patcher.stop)

        # parser
        patcher = patch(
            'flutils.setuputils.cfg.ConfigParser',
            autospec=True
        )
        parser = patcher.start()
        self.addCleanup(patcher.stop)

        # get_name
        patcher = patch(
            'flutils.setuputils.cfg._get_name',
            return_value='raijin'
        )
        get_name = patcher.start()
        self.addCleanup(patcher.stop)

        # isfile
        patcher = patch(
            'flutils.setuputils.cfg.os.path.isfile',
            return_value=True
        )
        patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.setuputils.cfg._each_setup_cfg_command',
            side_effect=[
                SetupCfgCommandConfig(
                    name='lint',
                    camel='Lint',
                    description=(
                        'Verify {name} {setup_dir} {home}'
                    ).format(**self.kwargs),
                    commands=(
                        (
                            'linter {setup_dir} {home} {name}'
                        ).format(**self.kwargs),
                    )
                ),
                SetupCfgCommandConfig(
                    name='{name}-style'.format(**self.kwargs),
                    camel='RaijinStyle',
                    description='',
                    commands=(
                        (
                            'linter {setup_dir} {home} {name}'
                        ).format(**self.kwargs),
                        (
                            'styler {setup_dir}'
                        ).format(**self.kwargs),
                        'another-command',
                    )
                ),
                SetupCfgCommandConfig(
                    name='multi',
                    camel='Multi',
                    description='',
                    commands=(
                        'first',
                        'second',
                        'third',
                    )
                ),
            ]
        )
        each_setup_cfg_command = patcher.start()
        self.addCleanup(patcher.stop)

        _ = list(each_sub_command_config('.'))
        prep_setup_dir.assert_called_once_with('.')
        expanduser.assert_called_once_with('~')
        get_name.assert_called()
        ret = len(parser.method_calls)
        exp = 2
        self.assertEqual(
            ret,
            exp,
            msg=(
                '\n\n'
                'expected parser.read() to be called only {exp} times\n'
                'However it was called {ret} time(s).\n'
            ).format(exp=exp, ret=ret)
        )
        each_setup_cfg_command.assert_called()
