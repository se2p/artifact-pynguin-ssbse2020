import unittest
from types import SimpleNamespace
from unittest.mock import patch

from flutils.pathutils import get_os_user


class TestGetOsUser(unittest.TestCase):

    def setUp(self):

        # Mock pwd.getpwuid
        patcher = patch(
            'flutils.pathutils.pwd.getpwuid',
            return_value=SimpleNamespace(pw_name='uid_user')
        )
        self.getpwuid = patcher.start()
        self.addCleanup(patcher.stop)

        # Mock getpass.getuser
        patcher = patch(
            'flutils.pathutils.getpass.getuser',
            return_value='test_user'
        )
        self.getuser = patcher.start()
        self.addCleanup(patcher.stop)

        # Mock pwd.getpwnam
        patcher = patch(
            'flutils.pathutils.pwd.getpwnam',
            return_value=SimpleNamespace(pw_name='test_user')
        )
        self.getpwnam = patcher.start()
        self.addCleanup(patcher.stop)

    def test_get_os_user_name_is_none(self):
        user_obj = get_os_user()
        self.getpwuid.assert_not_called()
        self.assertEqual(user_obj.pw_name, 'test_user')
        self.getpwnam.assert_called_with('test_user')

    def test_get_os_user_name_is_given(self):
        user_obj = get_os_user('test_user')
        self.getpwuid.assert_not_called()
        self.assertEqual(user_obj.pw_name, 'test_user')
        self.getuser.assert_not_called()
        self.getpwnam.assert_called_with('test_user')

    def test_get_os_user_uid(self):
        user_obj = get_os_user(254)
        self.assertEqual(user_obj.pw_name, 'uid_user')
        self.getpwuid.assert_called_with(254)
        self.getuser.assert_not_called()
        self.getpwnam.assert_not_called()


class TestGetOsUserException(unittest.TestCase):

    def setUp(self):
        # Mock pwd.getpwuid
        patcher = patch(
            'flutils.pathutils.pwd.getpwuid',
            side_effect=KeyError('Boom!')
        )
        self.getpwuid = patcher.start()
        self.addCleanup(patcher.stop)

        # Mock getpass.getuser
        patcher = patch(
            'flutils.pathutils.getpass.getuser',
            return_value='bad_user'
        )
        self.getuser = patcher.start()
        self.addCleanup(patcher.stop)

        # Mock pwd.getpwnam throw exception
        patcher = patch(
            'flutils.pathutils.pwd.getpwnam',
            side_effect=KeyError('Boom!')
        )
        self.getpwnam = patcher.start()
        self.addCleanup(patcher.stop)

    def test_get_os_user_name_is_invalid(self):
        self.assertRaises(OSError, get_os_user, 'test_user')
        self.getpwuid.assert_not_called()
        self.getuser.assert_not_called()

    def test_get_os_user_uid_is_invalid(self):
        self.assertRaises(OSError, get_os_user, 254)
        self.getuser.assert_not_called()
        self.getpwnam.assert_not_called()
