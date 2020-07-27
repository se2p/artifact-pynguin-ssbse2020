import unittest
from typing import (
    ClassVar,
    Dict,
    List,
    Tuple,
    Type,
)
from unittest.mock import (
    Mock,
    patch,
)

from setuptools import Command

from flutils.setuputils import add_setup_cfg_commands
from flutils.setuputils.cfg import SetupCfgCommandConfig
from flutils.setuputils.cmd import (
    _finalize_options,
    _initialize_options,
    _run,
)


def _build_class(
        setup_command_cfg: SetupCfgCommandConfig
) -> Type[Command]:
    setup_klass = type(
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
    klass = type(klass_name, (setup_klass, Command), {})
    return klass


class TestSetupUtils(unittest.TestCase):

    def setUp(self) -> None:
        self.kwargs: Dict[str, str] = {
            'name': 'raijin',
            'home': '/home/user',
            'setup_dir': '/home/user/tmp/raijin'
        }
        self.args: List[SetupCfgCommandConfig] = [
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
        self.command_classes: List[Type[Command]] = list(
            map(lambda x: _build_class(x), self.args)
        )

        patcher = patch(
            'flutils.setuputils.each_sub_command_config',
            return_value=self.args
        )
        self.each_sub_command_config = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.setuputils.build_setup_cfg_command_class',
            side_effect=self.command_classes
        )
        self.build_setup_cfg_command_class = patcher.start()
        self.addCleanup(patcher.stop)

    def test_add_setup_cfg_commands(self) -> None:
        setup_kwargs = {}
        add_setup_cfg_commands(setup_kwargs)
        self.assertTrue('cmdclass' in setup_kwargs.keys())
        for x, cfg in enumerate(self.args):
            self.assertTrue(cfg.name in setup_kwargs['cmdclass'].keys())
            self.assertEqual(
                setup_kwargs['cmdclass'][cfg.name],
                self.command_classes[x]
            )
