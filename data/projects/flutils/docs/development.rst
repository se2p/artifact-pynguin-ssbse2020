===========
Development
===========

Contributions to flutils can be made by sending a Merge request via
fork of `GitLab <https://gitlab.com/finite-loop/flutils>`_.  If you don't
have a GitLab account you can
`sign up here <https://gitlab.com/users/sign_up>`_.


Requirements
============


pyenv
-----

`pyenv <https://github.com/pyenv/pyenv>`_ is used to install and manage
different versions of Python on your system and will not effect the
system's Python.

#. Install the `pyenv prerequisites <https://bit.ly/2SNguOD>`_.

#. (Optional) By default `pyenv <https://github.com/pyenv/pyenv>`_ will
   be installed at ``~/.pyenv``.  If you desire, change the install
   location by setting the environment variable, ``PYENV_ROOT``, with
   the new location (e.g. ``export PYENV_ROOT=/a/new/path``).

#. Run the following to install:

   >>> curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash

   * Make sure to follow any post install instructions.

   * Mac users can install `pyenv <https://github.com/pyenv/pyenv>`_ via
     `homebrew <https://brew.sh/>`_.  THIS IS NOT RECOMMENDED; because,
     updates to pyenv lag behind.  Use at your own peril.

#. Restart your shell so that path changes take effect:

   >>> exec "${SHELL}"

#. Add the ``xxenv-latest`` plug-in to ``pyenv``:

   >>> git clone https://github.com/momo-lab/xxenv-latest.git "$(pyenv root)"/plugins/xxenv-latest


Python
------

flutils is designed to work with multiple versions of Python. So, we need
to make sure the latest versions are installed.

* As new versions of Python are released you'll need to follow these same
  instructions.

#. Update pyenv:

   >>> pyenv update

#. Install the latest versions of the following Pythons:

   >>> pyenv latest install -v
   >>> pyenv latest install -v 3.7
   >>> pyenv latest install -v 3.6


pipenv
------

pipenv is used for setting up a development virtualenv and installing
and managing the development dependencies.

Follow the instructions for installing pipenv
`here <https://pipenv.kennethreitz.org/en/latest/install/#installing-pipenv>`_.

.. warning:: There has not been a new release of pipenv since 2018-11-26.
   There are also rumors that the project may be dead.  Because of this,
   sometime in the future, flutils will replace the use of pipenv with
   `poetry <https://python-poetry.org/>`_.


Setup
=====

Code
----

#. Clone the flutils code from
   `GitLab <https://gitlab.com/finite-loop/flutils>`_ :

   * Clone with SSH:

     >>> git clone git@gitlab.com:finite-loop/flutils.git

   * or, with HTTPS:

     >>> git clone https://gitlab.com/finite-loop/flutils.git

#. Change directory:

   >>> cd flutils

Virtual Environment
-------------------

#. In the code's root directory run the following command to setup the
   virtualenv needed for development:

   >>> pipenv install --dev --python "$(pyenv root)/versions/$(pyenv latest -p)/bin/python"

#. To activate the flutils virtualenv:

   >>> pipenv shell


Testing
=======

Within the activated flutils virtualenv, the following commands can be used to
test code changes:

* ``./setup.py test`` will run all unit tests, integration tests and type
  checks (`mypy <http://mypy-lang.org/>`_).

* ``./setup.py coverage`` will run all the tests and produce a coverage report.

* ``./setup.py lint`` will run code analysis checks using
  `pylint <https://pylint.org>`_.

* ``./setup.py style`` will run code styling enforcement checks using
  `flake8 <https://flake8.pycqa.org/en/latest/>`_.

* ``./setup.py security`` will run code security checks using
  `bandit <https://bandit.readthedocs.io/en/latest/>`_.

* ``./setup.py pipelinetests`` will run all of the above tests.

* ``make tests`` will run all of the above tests across the multiple supported
  versions of Python using `tox <https://tox.readthedocs.io/en/latest/>`_.
  make sure to run this command before submitting a pull-request.  Code that
  does not pass this test will not be accepted.

CI Environment
==============

.. warning:: This requires Docker to be installed and running.

Run the following commands when a new version of Python has been released:

#. If a new minor version (e.g. 3.9) of Python has been released, changes
   need to be made  in ``tests/Dockerfile`` to reflect the new version.

#. To build a new Docker image with the latest supported versions of Python:

   >>> make docker-image

#. Deploy the newly built Docker image to the regestry:

   >>> make docker-image-push


New Release
===========

#. Bump the version number in ``flutils/__init__.py``, commit and push.

#. Update the build requirements for the documentation build server.

   >>> make docs-requirements

#. Cut a new tag:

   >>> git tag "v$(python -c 'import flutils; print(flutils.__version__)')"

#. Push the new tag:

   >>> git push --tags

#. Build and push the release to ``test.pypi.org``:

   >>> make sdist-push-test

#. Go to the link shown in the output of the above command and verify
   everything.

#. Build and push the release to ``pypi.org``:

   >>> make sdist-push



References
==========

* `pyenv installer <https://github.com/pyenv/pyenv-installer>`_


