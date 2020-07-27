#!/usr/bin/env python

import os

from setuptools import setup

from flutils.setuputils import add_setup_cfg_commands

setup_kwargs = {}
setup_dir = os.path.dirname(os.path.realpath(__file__))
add_setup_cfg_commands(setup_kwargs, setup_dir=setup_dir)
setup(**setup_kwargs)
