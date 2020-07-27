import sys
import unittest
from io import BytesIO

from flutils.cmdutils import run


class TestStaticTypes(unittest.TestCase):
    """This test will call ``mypy`` to do type checking.

    The ``mypy`` configuration exists in ``setup.cfg``.
    """

    def test_static_types(self) -> None:
        """Static type checking with mypy"""
        cmd = 'mypy -p flutils'
        with BytesIO() as stdout:
            return_code = run(
                cmd,
                stdout=stdout,
                stderr=stdout,
            )
            text: bytes = stdout.getvalue()
        if return_code != 0:
            txt = text.decode(sys.getdefaultencoding())
            msg = (
                    '\n'
                    'mypy command: %s\n'
                    'return code:  %r\n'
                    'The following problems were found with mypy:\n\n'
                    '%s\n' % (cmd, return_code, txt)
            )
            self.fail(msg=msg)
