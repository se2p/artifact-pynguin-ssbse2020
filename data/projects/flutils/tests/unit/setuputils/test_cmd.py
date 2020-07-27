import os
import unittest
from subprocess import PIPE
from unittest.mock import (
    ANY,
    Mock,
    PropertyMock,
    call,
    patch,
)

from flutils.setuputils.cfg import SetupCfgCommandConfig
# noinspection PyProtectedMember
from flutils.setuputils.cmd import (
    _DIVIDER,
    _each_command,
    _finalize_options,
    _get_path,
    _initialize_options,
    _run,
    _show_command,
    build_setup_cfg_command_class,
)


class TestCmd(unittest.TestCase):


    @patch('flutils.setuputils.cmd.os.access', return_value=True)
    @patch('flutils.setuputils.cmd.os.path.isfile', return_value=True)
    def test_get_path__0(self, isfile, access) -> None:
        arg = '/a/path/to/ls'
        ret = _get_path(arg)
        self.assertEqual(
            ret,
            arg,
            msg=(
                '\n\n'
                'flutils.setuputils.cmd._get_path({arg!r})\n'
                'expected: {arg!r}\n'
                '     got: {ret!r}\n'
            ).format(arg=arg, ret=ret)
        )
        isfile.assert_called_once_with(arg)
        access.assert_called_once_with(arg, os.X_OK)

    @patch('flutils.setuputils.cmd.os.path.isfile', return_value=False)
    def test_get_path__1(self, isfile) -> None:
        arg = '/a/path/to/ls'
        with self.assertRaises(FileNotFoundError):
            _get_path(arg)
        isfile.assert_called_once_with(arg)

    @patch('flutils.setuputils.cmd.os.access', return_value=True)
    @patch('flutils.setuputils.cmd.shutil.which', return_value='/a/path/to/ls')
    def test_get_path__2(self, which, access) -> None:
        arg = 'ls'
        exp = '/a/path/to/ls'
        ret = _get_path(arg)
        self.assertEqual(
            ret,
            exp,
            msg=(
                '\n\n'
                'flutils.setuputils.cmd._get_path({arg!r})\n'
                'expected: {exp!r}\n'
                '     got: {ret!r}\n'
            ).format(arg=arg, exp=exp, ret=ret)
        )
        which.assert_called_once_with(arg)
        access.assert_called_once_with(exp, os.X_OK)

    @patch('flutils.setuputils.cmd.os.access', return_value=False)
    @patch('flutils.setuputils.cmd.shutil.which', return_value='/a/path/to/ls')
    def test_get_path__3(self, which, access) -> None:
        arg = 'ls'
        access_arg = '/a/path/to/ls'
        with self.assertRaises(PermissionError):
            _get_path(arg)

        which.assert_called_once_with(arg)
        access.assert_called_once_with(access_arg, os.X_OK)

    @patch('flutils.setuputils.cmd.shutil.which', return_value=None)
    def test_get_path__4(self, which) -> None:
        arg = 'ls'
        with self.assertRaises(FileNotFoundError):
            _get_path(arg)
        which.assert_called_once_with(arg)

    def test_each_command(self) -> None:
        arg = (
            '/a/path/to/ls -flap ',
            'test -a --abc=true --def false /with/a/path/a_file.txt'
        )
        exp = [
            (
                '/a/path/to/ls',
                '-flap'
            ),
            (
                '/a/path/to/test',
                '-a',
                '--abc=true',
                '--def',
                'false',
            )
        ]
        with patch('flutils.setuputils.cmd.shlex') as shlex:
            with patch('flutils.setuputils.cmd._get_path') as get_path:
                get_path.side_effect = [
                    '/a/path/to/ls',
                    '/a/path/to/test'
                ]

                shlex.split.side_effect = exp
                ret = list(_each_command(arg))
                self.assertEqual(
                    ret,
                    exp,
                    msg=(
                        '\n\n'
                        'flutils.setuputils.cmd._each_command({arg!r))\n\n'
                        'expected:\n'
                        '    {exp!r}\n\n',
                        'got:\n'
                        '    {ret!r}\n\n'
                    )
                )
                calls = list(map(lambda x: call.split(x.strip()), arg))
                shlex.assert_has_calls(calls)

    @staticmethod
    def test_show_command() -> None:
        command = (
            '/a/path/to/test',
            '-a',
            '--abc=true',
            '--def',
            'false',
        )
        with patch('builtins.print') as prnt:
            prnt.return_value.write.side_effect = [
                None,
                None,
                None,
                None,
                None,
                None,
                None,
            ]
            _show_command(command)
            calls = [
                call.write(_DIVIDER),
                call.write('/a/path/to/test\n'),
                call.write('  -a\n'),
                call.write('  --abc=true\n'),
                call.write('  --def\n'),
                call.write('  false\n'),
                call.write('\n\n'),
            ]
            prnt.assert_has_calls(calls)

    def test_initialize_options(self) -> None:
        _self = Mock()
        self.assertIsNone(_initialize_options(_self))

    def test_finalize_options(self) -> None:
        _self = Mock()
        self.assertIsNone(_finalize_options(_self))

    def test_run__0(self) -> None:
        cmds = (
            (
                '/a/path/to/ls',
                '-flap'
            ),
            (
                '/a/path/to/test',
                '-a',
                '--abc=true',
                '--def',
                'false',
            )
        )

        _self = Mock()
        commands = PropertyMock(return_value=cmds)
        type(_self).commands = commands

        patcher = patch('flutils.setuputils.cmd.sys', autospec=True)
        sys = patcher.start()
        sys.exit.return_value = None
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.setuputils.cmd._each_command',
            return_value=cmds
        )
        each_command = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch('flutils.setuputils.cmd._show_command')
        show_command = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.setuputils.cmd.run',
            side_effect=[0, 0]
        )
        run = patcher.start()
        self.addCleanup(patcher.stop)

        _run(_self)

        each_command.assert_called_once_with(cmds)
        show_command.assert_has_calls([
            call(cmds[0]),
            call(cmds[1])
        ])
        run.assert_has_calls([
            call(cmds[0]),
            call(cmds[1])
        ])
        sys.exit.assert_called_once_with(0)

    def test_run__1(self) -> None:
        cmds = (
            (
                '/a/path/to/ls',
                '-flap'
            ),
            (
                '/a/path/to/test',
                '-a',
                '--abc=true',
                '--def',
                'false',
            )
        )

        _self = Mock()
        commands = PropertyMock(return_value=cmds)
        type(_self).commands = commands

        patcher = patch('flutils.setuputils.cmd.sys', autospec=True)
        sys = patcher.start()
        sys.exit.return_value = None
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.setuputils.cmd._each_command',
            return_value=cmds
        )
        each_command = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch('flutils.setuputils.cmd._show_command')
        show_command = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.setuputils.cmd.run',
            side_effect=[0, 5]
        )
        run = patcher.start()
        self.addCleanup(patcher.stop)

        _run(_self)

        each_command.assert_called_once_with(cmds)
        show_command.assert_has_calls([
            call(cmds[0]),
            call(cmds[1])
        ])
        run.assert_has_calls([
            call(cmds[0]),
            call(cmds[1])
        ])
        sys.exit.assert_called_once_with(5)

    @staticmethod
    def test_build_sub_command_class() -> None:
        arg = SetupCfgCommandConfig(
            name='multi',
            camel='Multi',
            description='',
            commands=(
                'first',
                'second',
                'third',
            )
        )
        with patch('flutils.setuputils.cmd._type') as type_:
            build_setup_cfg_command_class(arg)
            type_.assert_has_calls([
                call('SetupCfgCommand', ANY, ANY),
                call('MultiCommand', ANY, ANY)
            ])
