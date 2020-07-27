# pylint: disable=R0801
from os import PathLike
from typing import (
    Any,
    Dict,
    Optional,
    Union,
)

from .cfg import each_sub_command_config
from .cmd import build_setup_cfg_command_class


def add_setup_cfg_commands(
        setup_kwargs: Dict[str, Any],
        setup_dir: Optional[Union[PathLike, str]] = None
) -> None:
    """Add additional custom ``setup.py`` commands that are defined in
    ``setup.cfg``.

    Args:
        setup_kwargs (dict): A dictionary holding the
            `setuptools.setup keyword arguments <https://bit.ly/2Ju4Zad>`_.
            (see example below).
        setup_dir (:obj:`str` or :obj:`Path <pathlib.Path>`, optional): The
            root directory of the project. (e.g. the directory that contains
            the ``setup.py`` file).  Defaults to: ``None`` which will try to
            determine the directory using the call stack.

    :rtype: :obj:`None`

    Example:
        Use in ``setup.py`` like the following::

            #!/usr/bin/env python

            import os

            from setuptools import setup

            from flutils.setuputils import add_setup_cfg_commands

            setup_kwargs = {}
            setup_dir = os.path.dirname(os.path.realpath(__file__))
            add_setup_cfg_commands(setup_kwargs, setup_dir=setup_dir)
            setup(**setup_kwargs)

    """
    for sub_command_cfg in each_sub_command_config(setup_dir):
        klass = build_setup_cfg_command_class(sub_command_cfg)
        if 'cmdclass' not in setup_kwargs.keys():
            setup_kwargs['cmdclass'] = {}
        setup_kwargs['cmdclass'][sub_command_cfg.name] = klass
