import unittest
from types import SimpleNamespace
from unittest.mock import patch

from flutils.pathutils import get_os_group


class TestGetOsGroup(unittest.TestCase):

    def setUp(self):
        # Mock get_os_user
        patcher = patch(
            'flutils.pathutils.get_os_user',
            return_value=SimpleNamespace(pw_gid=3287)
        )
        self.get_os_user = patcher.start()
        self.addCleanup(patcher.stop)

        # Mock grp.getgrgid
        patcher = patch(
            'flutils.pathutils.grp.getgrgid',
            return_value=SimpleNamespace(gr_name='foo')
        )
        self.getgrgid = patcher.start()
        self.addCleanup(patcher.stop)

        # Mock grp.getgrnam
        patcher = patch(
            'flutils.pathutils.grp.getgrnam',
            return_value=SimpleNamespace(gr_name='foo')
        )
        self.getgrnam = patcher.start()
        self.addCleanup(patcher.stop)

    def test_get_os_group_name_is_none(self):
        group_obj = get_os_group()
        self.assertEqual(group_obj.gr_name, 'foo')
        self.getgrnam.assert_not_called()

    def test_get_os_group_name_is_given(self):
        group_obj = get_os_group('test_group')
        self.assertEqual(group_obj.gr_name, 'foo')
        self.getgrnam.assert_called_with('test_group')
        self.get_os_user.assert_not_called()
        self.getgrgid.assert_not_called()

    def test_get_os_group_name_is_gid(self):
        group_obj = get_os_group(254)
        self.get_os_user.assert_not_called()
        self.getgrgid.assert_called_once_with(254)
        self.assertEqual(group_obj.gr_name, 'foo')
        self.getgrnam.assert_not_called()


class TestGetOsGroupException(unittest.TestCase):

    def setUp(self):
        # Mock get_os_user
        patcher = patch(
            'flutils.pathutils.get_os_user',
            return_value=SimpleNamespace(pw_gid=3287)
        )
        self.get_os_user = patcher.start()
        self.addCleanup(patcher.stop)

        # Mock grp.getgrgid
        patcher = patch(
            'flutils.pathutils.grp.getgrgid',
            side_effect=KeyError('Boom!')
        )
        self.getgrgid = patcher.start()
        self.addCleanup(patcher.stop)

        # Mock grp.getgrnam
        patcher = patch(
            'flutils.pathutils.grp.getgrnam',
            side_effect=KeyError('Boom!')
        )
        self.getgrnam = patcher.start()
        self.addCleanup(patcher.stop)

    def test_get_os_group_name_is_invalid(self):
        self.assertRaises(OSError, get_os_group, 'test_group')
        self.get_os_user.assert_not_called()
        self.getgrgid.assert_not_called()

    def test_get_os_group_gid_is_invalid(self):
        self.assertRaises(OSError, get_os_group, 254)
        self.getgrgid.assert_called_once_with(254)
        self.get_os_user.assert_not_called()
        self.getgrnam.assert_not_called()
