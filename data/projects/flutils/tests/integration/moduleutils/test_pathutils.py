import os
import unittest
from pathlib import Path

from flutils.pathutils import (
    find_paths,
    normalize_path,
)


class TestOne(unittest.TestCase):

    def test_integration_path(self):
        val = Path('~/tmp')
        expected = os.path.expanduser('~/tmp')
        val = normalize_path(val)
        self.assertEqual(val.as_posix(), expected)


class TestTwo(unittest.TestCase):

    def test_integration_path(self):
        val = '~/*'
        try:
            list(find_paths(val))
        except Exception as e:
            self.fail('There was an exception: %s' % e)
