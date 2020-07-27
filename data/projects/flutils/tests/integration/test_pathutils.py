import os
import shutil
import unittest

from flutils.pathutils import (
    directory_present,
    normalize_path,
    path_absent,
)

# Structure
# ~/tmp/flutils/
#  ├── 1/
#  ├── 2/
#  │   └── a.file
#  ├── 3/
#  │   ├── 2/       (link)
#  │   ├── a.file   (link)
#  │   └── b.file
#  └── 4/           (Not created)


DIR_ROOT = normalize_path('~/tmp/flutils')
DIR_1 = os.path.join(DIR_ROOT, '1')
DIR_2 = os.path.join(DIR_ROOT, '2')
DIR_3 = os.path.join(DIR_ROOT, '3')
DIR_4 = os.path.join(DIR_ROOT, '4')

FILE_A = os.path.join(DIR_2, 'a.file')
FILE_B = os.path.join(DIR_3, 'b.file')

LINK_2 = os.path.join(DIR_3, '2')
LINK_A = os.path.join(DIR_3, 'a.file')


class TestPathAbsent(unittest.TestCase):

    def setUp(self) -> None:
        if os.path.exists(DIR_ROOT):
            shutil.rmtree(DIR_ROOT)
        directory_present(DIR_1)
        directory_present(DIR_2)
        directory_present(DIR_3)

        with open(FILE_A, 'w') as f:
            f.write('')

        with open(FILE_B, 'w') as f:
            f.write('')

        os.symlink(DIR_2, LINK_2)
        os.symlink(FILE_A, LINK_A)

    def tearDown(self) -> None:
        if os.path.exists(DIR_ROOT):
            shutil.rmtree(DIR_ROOT)

    def test_delete_empty_dir(self) -> None:
        path_absent(DIR_1)
        self.assertFalse(
            os.path.exists(DIR_1)
        )

    def test_delete_file(self) -> None:
        path_absent(FILE_B)
        self.assertFalse(
            os.path.exists(FILE_B)
        )

    def test_non_exists(self) -> None:
        path_absent(DIR_4)
        self.assertFalse(
            os.path.exists(DIR_4)
        )

    def test_delete_dir(self) -> None:
        path_absent(DIR_3)
        self.assertFalse(os.path.exists(DIR_3))
        self.assertFalse(os.path.exists(FILE_B))
        self.assertFalse(os.path.exists(LINK_2))
        self.assertFalse(os.path.exists(LINK_A))
        self.assertTrue(os.path.exists(DIR_2))
        self.assertTrue(os.path.exists(FILE_A))

    def test_delete_dir_link(self) -> None:
        path_absent(LINK_2)
        self.assertFalse(os.path.exists(LINK_2))
        self.assertTrue(os.path.exists(DIR_2))
        self.assertTrue(os.path.exists(FILE_B))
        self.assertTrue(os.path.exists(FILE_A))

    def test_delete_parent_dir(self) -> None:
        path_absent(DIR_ROOT)
        self.assertFalse(os.path.exists(DIR_1))
        self.assertFalse(os.path.exists(DIR_2))
        self.assertFalse(os.path.exists(DIR_3))
        self.assertFalse(os.path.exists(DIR_4))
