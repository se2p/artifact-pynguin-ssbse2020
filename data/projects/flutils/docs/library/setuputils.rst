*****
Setup
*****

Custom ``setup.py`` Commands
============================

  flutils offers the ability to quickly add additional ``setup.py`` custom
  commands to a Python project.

Requirements
------------

  Custom Setup Commands can be used in Python projects that are using
  `setuptools <https://bit.ly/2NvPOwe>`_ with a ``setup.cfg``
  `configuration file <https://bit.ly/2N1sVl0>`_.

  Setup Commands requires that the ``setup.py`` and ``setup.cfg`` files exist
  in the root directory of a typical Python project structure::

      my_project/
      │
      ├── docs/
      │   ├── doc1.rst
      │   └── doc2.rst
      │
      ├── my_project/
      │   ├── __init__.py
      │   ├── module1.py
      │   └── module2.py
      │
      ├── setup.cfg
      ├── setup.py
      └── tests/
          ├── test1.py
          └── test2.py


  To use Custom Setup Commands, the ``setup.cfg`` file must have, at least, the
  following defined::

    [metadata]
    name == my_project

Custom Command Definitions
--------------------------

  The actual command definitions can exist in ``setup.cfg`` and/or
  ``setup_commands.cfg``.  If the ``setup_commands.cfg`` file exists then
  the command definitions from in this file will be used; and, command
  definitions in ``setup.cfg`` are ignored.

  The general idea is to have ``setup_commands.cfg`` ignored by version control,
  allowing developers customize command definitions to their specific needs.
  While command definitions needed for deployment, testing etc can be kept in
  version control.

  Each individual Custom-Setup-Command definition starts with a section header
  of::

      [setup.command.<name-of-custom-setup-command>]

  Underneath the section header the following options can be used:

  * ``description = <text>``: A short description about the custom
    setup command. This is displayed with ``setup.py --help-commands``

  * ``command = <text>``: The command line command or commands to execute when
    the ``setup.py`` custom command is called.

  * ``commands = <text>``: The command line command or commands to execute when
    the ``setup.py`` custom command is called.  If both ``command`` and
    ``commands`` exist, the value of ``command`` will be executed first.

  * ``name = <text>``: This option can override the
    ``<name-of-custom-setup-command>`` set in the section header.


  The following string interpolation variables can be used on all but the
  ``name`` option.

  * ``{name}``: the name of the project as set in the ``[metadata]`` section
    ``name`` option.

  * ``{setup_dir}``: The full path to the directory that contains the
    ``setup.py`` file.

  * ``{home}``: The full path to the user's home directory.


Example ``setup.cfg``
---------------------

  The following example of ``setup.cfg`` contains the definitions for the
  ``setup.py lint`` and ``setup.py lint-all`` commands::

      [metadata]
      name = my_project

      [setup.command.lint]
      description = Lint the {name} project files
      command = pylint --rcfile={setup_dir}/.pylintrc {setup_dir}/{name}

      [setup.command.lint_all]
      name = lint-all
      description = Lint the {name} project and test files
      commands =
          pylint --rcfile={setup_dir}/.pylintrc {setup_dir}/{name}
          pylint --rcfile={setup_dir}/.pylintrc {setup_dir}/tests


Implementation
--------------

  The final step of using Custom Setup Commands is to prepare the commands and
  tell setuptools.


  .. autofunction:: flutils.setuputils.add_setup_cfg_commands
