Currencies, Monetary Value Objects, Arithmetic and Conversion
=============================================================

|BUILD_STATUS|

.. |BUILD_STATUS| image:: https://github.com/vst/pypara/workflows/Install%20and%20Test/badge.svg
    :target: https://github.com/vst/pypara/actions

**TODO**: Provide a complete README.


Development Notes
-----------------

Make sure that `tox <https://tox.readthedocs.io/en/latest/>`_ completes successfully.

Create a virtual environment::

  mkvirtualenv --python=python3.6 <VIRTUAL-ENVIRONMENT-NAME>

Install ``tox``::

  pip install tox

And run ``tox``::

  tox

Publishing
----------

```
pip install --upgrade twine
python setup.py sdist bdist_wheel
twine upload -s dist/*
```
