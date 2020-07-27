import unittest
from unittest.mock import patch

# noinspection PyProtectedMember
from flutils.packages import (
    _BUMP_VERSION_MAJOR,
    _BUMP_VERSION_MINOR,
    _BUMP_VERSION_MINOR_ALPHA,
    _BUMP_VERSION_MINOR_BETA,
    _BUMP_VERSION_PATCH,
    _BUMP_VERSION_PATCH_ALPHA,
    _BUMP_VERSION_PATCH_BETA,
    _VersionInfo,
    _VersionPart,
    bump_version,
)


class TestBumpVersion(unittest.TestCase):

    def test_bump_version__00(self) -> None:
        version = '1.2.3'
        position = 1
        pre_release = ''
        bump_type = _BUMP_VERSION_MAJOR
        exp = '2.0'
        ver_info = _VersionInfo(
            version=version,
            major=_VersionPart(
                pos=0,
                txt='1',
                num=1,
                pre_txt='',
                pre_num=-1,
                name='major'
            ),
            minor=_VersionPart(
                pos=1,
                txt='2',
                num=2,
                pre_txt='',
                pre_num=-1,
                name='minor'
            ),
            patch=_VersionPart(
                pos=2,
                txt='3',
                num=3,
                pre_txt='',
                pre_num=-1,
                name='patch'
            ),
            pre_pos=-1
        )
        patcher = patch(
            'flutils.packages._build_version_info',
            return_value=ver_info
        )
        build_version_info = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.packages._build_version_bump_position',
            return_value=position
        )
        build_version_bump_position = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.packages._build_version_bump_type',
            return_value=bump_type
        )
        build_version_bump_type = patcher.start()
        self.addCleanup(patcher.stop)

        ret = bump_version(version, position=position, pre_release=pre_release)

        self.assertEqual(
            ret,
            exp,
            msg=(
                '\n\n'
                'bump_version({version!r}, '
                'position={position!r}, '
                'pre_release={pre_release!r})\n'
                'expected: {exp!r}\n'
                '     got: {ret!r}\n'
            ).format(
                version=version,
                position=position,
                pre_release=pre_release,
                exp=exp,
                ret=ret
            )
        )
        build_version_info.assert_called_once_with(version)
        build_version_bump_position.assert_called_once_with(position)
        build_version_bump_type.assert_called_once_with(position, pre_release)

    def test_bump_version__01(self) -> None:
        version = '1.2.3'
        position = 2
        pre_release = ''
        bump_type = _BUMP_VERSION_MINOR
        exp = '1.3'
        ver_info = _VersionInfo(
            version=version,
            major=_VersionPart(
                pos=0,
                txt='1',
                num=1,
                pre_txt='',
                pre_num=-1,
                name='major'
            ),
            minor=_VersionPart(
                pos=1,
                txt='2',
                num=2,
                pre_txt='',
                pre_num=-1,
                name='minor'
            ),
            patch=_VersionPart(
                pos=2,
                txt='3',
                num=3,
                pre_txt='',
                pre_num=-1,
                name='patch'
            ),
            pre_pos=-1
        )
        patcher = patch(
            'flutils.packages._build_version_info',
            return_value=ver_info
        )
        build_version_info = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.packages._build_version_bump_position',
            return_value=position
        )
        build_version_bump_position = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.packages._build_version_bump_type',
            return_value=bump_type
        )
        build_version_bump_type = patcher.start()
        self.addCleanup(patcher.stop)

        ret = bump_version(version, position=position, pre_release=pre_release)

        self.assertEqual(
            ret,
            exp,
            msg=(
                '\n\n'
                'bump_version({version!r}, '
                'position={position!r}, '
                'pre_release={pre_release!r})\n'
                'expected: {exp!r}\n'
                '     got: {ret!r}\n'
            ).format(
                version=version,
                position=position,
                pre_release=pre_release,
                exp=exp,
                ret=ret
            )
        )
        build_version_info.assert_called_once_with(version)
        build_version_bump_position.assert_called_once_with(position)
        build_version_bump_type.assert_called_once_with(position, pre_release)

    def test_bump_version__02(self) -> None:
        version = '1.2a19'
        position = 2
        pre_release = ''
        bump_type = _BUMP_VERSION_MINOR
        exp = '1.2'
        ver_info = _VersionInfo(
            version=version,
            major=_VersionPart(
                pos=0,
                txt='1',
                num=1,
                pre_txt='',
                pre_num=-1,
                name='major'
            ),
            minor=_VersionPart(
                pos=1,
                txt='2a19',
                num=2,
                pre_txt='a',
                pre_num=19,
                name='minor'
            ),
            patch=_VersionPart(
                pos=2,
                txt='',
                num=0,
                pre_txt='',
                pre_num=-1,
                name='patch'
            ),
            pre_pos=-1
        )
        patcher = patch(
            'flutils.packages._build_version_info',
            return_value=ver_info
        )
        build_version_info = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.packages._build_version_bump_position',
            return_value=position
        )
        build_version_bump_position = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.packages._build_version_bump_type',
            return_value=bump_type
        )
        build_version_bump_type = patcher.start()
        self.addCleanup(patcher.stop)

        ret = bump_version(version, position=position, pre_release=pre_release)

        self.assertEqual(
            ret,
            exp,
            msg=(
                '\n\n'
                'bump_version({version!r}, '
                'position={position!r}, '
                'pre_release={pre_release!r})\n'
                'expected: {exp!r}\n'
                '     got: {ret!r}\n'
            ).format(
                version=version,
                position=position,
                pre_release=pre_release,
                exp=exp,
                ret=ret
            )
        )
        build_version_info.assert_called_once_with(version)
        build_version_bump_position.assert_called_once_with(position)
        build_version_bump_type.assert_called_once_with(position, pre_release)

    def test_bump_version__03(self) -> None:
        version = '1.2.3'
        position = 2
        pre_release = 'a'
        bump_type = _BUMP_VERSION_MINOR_ALPHA
        exp = '1.3a0'
        ver_info = _VersionInfo(
            version=version,
            major=_VersionPart(
                pos=0,
                txt='1',
                num=1,
                pre_txt='',
                pre_num=-1,
                name='major'
            ),
            minor=_VersionPart(
                pos=1,
                txt='2',
                num=2,
                pre_txt='',
                pre_num=-1,
                name='minor'
            ),
            patch=_VersionPart(
                pos=2,
                txt='3',
                num=3,
                pre_txt='',
                pre_num=-1,
                name='patch'
            ),
            pre_pos=-1
        )
        patcher = patch(
            'flutils.packages._build_version_info',
            return_value=ver_info
        )
        build_version_info = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.packages._build_version_bump_position',
            return_value=position
        )
        build_version_bump_position = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.packages._build_version_bump_type',
            return_value=bump_type
        )
        build_version_bump_type = patcher.start()
        self.addCleanup(patcher.stop)

        ret = bump_version(version, position=position, pre_release=pre_release)

        self.assertEqual(
            ret,
            exp,
            msg=(
                '\n\n'
                'bump_version({version!r}, '
                'position={position!r}, '
                'pre_release={pre_release!r})\n'
                'expected: {exp!r}\n'
                '     got: {ret!r}\n'
            ).format(
                version=version,
                position=position,
                pre_release=pre_release,
                exp=exp,
                ret=ret
            )
        )
        build_version_info.assert_called_once_with(version)
        build_version_bump_position.assert_called_once_with(position)
        build_version_bump_type.assert_called_once_with(position, pre_release)

    def test_bump_version__04(self) -> None:
        version = '1.2a0'
        position = 2
        pre_release = 'a'
        bump_type = _BUMP_VERSION_MINOR_ALPHA
        exp = '1.2a1'
        ver_info = _VersionInfo(
            version=version,
            major=_VersionPart(
                pos=0,
                txt='1',
                num=1,
                pre_txt='',
                pre_num=-1,
                name='major'
            ),
            minor=_VersionPart(
                pos=1,
                txt='2a0',
                num=2,
                pre_txt='a',
                pre_num=0,
                name='minor'
            ),
            patch=_VersionPart(
                pos=2,
                txt='',
                num=0,
                pre_txt='',
                pre_num=-1,
                name='patch'
            ),
            pre_pos=-1
        )
        patcher = patch(
            'flutils.packages._build_version_info',
            return_value=ver_info
        )
        build_version_info = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.packages._build_version_bump_position',
            return_value=position
        )
        build_version_bump_position = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.packages._build_version_bump_type',
            return_value=bump_type
        )
        build_version_bump_type = patcher.start()
        self.addCleanup(patcher.stop)

        ret = bump_version(version, position=position, pre_release=pre_release)

        self.assertEqual(
            ret,
            exp,
            msg=(
                '\n\n'
                'bump_version({version!r}, '
                'position={position!r}, '
                'pre_release={pre_release!r})\n'
                'expected: {exp!r}\n'
                '     got: {ret!r}\n'
            ).format(
                version=version,
                position=position,
                pre_release=pre_release,
                exp=exp,
                ret=ret
            )
        )
        build_version_info.assert_called_once_with(version)
        build_version_bump_position.assert_called_once_with(position)
        build_version_bump_type.assert_called_once_with(position, pre_release)

    def test_bump_version__05(self) -> None:
        version = '1.2b0'
        position = 2
        pre_release = 'a'
        bump_type = _BUMP_VERSION_MINOR_ALPHA
        exp = '1.3a0'
        ver_info = _VersionInfo(
            version=version,
            major=_VersionPart(
                pos=0,
                txt='1',
                num=1,
                pre_txt='',
                pre_num=-1,
                name='major'
            ),
            minor=_VersionPart(
                pos=1,
                txt='2b0',
                num=2,
                pre_txt='b',
                pre_num=0,
                name='minor'
            ),
            patch=_VersionPart(
                pos=2,
                txt='',
                num=0,
                pre_txt='',
                pre_num=-1,
                name='patch'
            ),
            pre_pos=-1
        )
        patcher = patch(
            'flutils.packages._build_version_info',
            return_value=ver_info
        )
        build_version_info = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.packages._build_version_bump_position',
            return_value=position
        )
        build_version_bump_position = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.packages._build_version_bump_type',
            return_value=bump_type
        )
        build_version_bump_type = patcher.start()
        self.addCleanup(patcher.stop)

        ret = bump_version(version, position=position, pre_release=pre_release)

        self.assertEqual(
            ret,
            exp,
            msg=(
                '\n\n'
                'bump_version({version!r}, '
                'position={position!r}, '
                'pre_release={pre_release!r})\n'
                'expected: {exp!r}\n'
                '     got: {ret!r}\n'
            ).format(
                version=version,
                position=position,
                pre_release=pre_release,
                exp=exp,
                ret=ret
            )
        )
        build_version_info.assert_called_once_with(version)
        build_version_bump_position.assert_called_once_with(position)
        build_version_bump_type.assert_called_once_with(position, pre_release)

    def test_bump_version__06(self) -> None:
        version = '1.2b0'
        position = 2
        pre_release = 'b'
        bump_type = _BUMP_VERSION_MINOR_BETA
        exp = '1.2b1'
        ver_info = _VersionInfo(
            version=version,
            major=_VersionPart(
                pos=0,
                txt='1',
                num=1,
                pre_txt='',
                pre_num=-1,
                name='major'
            ),
            minor=_VersionPart(
                pos=1,
                txt='2b0',
                num=2,
                pre_txt='b',
                pre_num=0,
                name='minor'
            ),
            patch=_VersionPart(
                pos=2,
                txt='',
                num=0,
                pre_txt='',
                pre_num=-1,
                name='patch'
            ),
            pre_pos=-1
        )
        patcher = patch(
            'flutils.packages._build_version_info',
            return_value=ver_info
        )
        build_version_info = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.packages._build_version_bump_position',
            return_value=position
        )
        build_version_bump_position = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.packages._build_version_bump_type',
            return_value=bump_type
        )
        build_version_bump_type = patcher.start()
        self.addCleanup(patcher.stop)

        ret = bump_version(version, position=position, pre_release=pre_release)

        self.assertEqual(
            ret,
            exp,
            msg=(
                '\n\n'
                'bump_version({version!r}, '
                'position={position!r}, '
                'pre_release={pre_release!r})\n'
                'expected: {exp!r}\n'
                '     got: {ret!r}\n'
            ).format(
                version=version,
                position=position,
                pre_release=pre_release,
                exp=exp,
                ret=ret
            )
        )
        build_version_info.assert_called_once_with(version)
        build_version_bump_position.assert_called_once_with(position)
        build_version_bump_type.assert_called_once_with(position, pre_release)

    def test_bump_version__07(self) -> None:
        version = '1.2a0'
        position = 2
        pre_release = 'b'
        bump_type = _BUMP_VERSION_MINOR_BETA
        exp = '1.2b0'
        ver_info = _VersionInfo(
            version=version,
            major=_VersionPart(
                pos=0,
                txt='1',
                num=1,
                pre_txt='',
                pre_num=-1,
                name='major'
            ),
            minor=_VersionPart(
                pos=1,
                txt='2a0',
                num=2,
                pre_txt='a',
                pre_num=0,
                name='minor'
            ),
            patch=_VersionPart(
                pos=2,
                txt='',
                num=0,
                pre_txt='',
                pre_num=-1,
                name='patch'
            ),
            pre_pos=-1
        )
        patcher = patch(
            'flutils.packages._build_version_info',
            return_value=ver_info
        )
        build_version_info = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.packages._build_version_bump_position',
            return_value=position
        )
        build_version_bump_position = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.packages._build_version_bump_type',
            return_value=bump_type
        )
        build_version_bump_type = patcher.start()
        self.addCleanup(patcher.stop)

        ret = bump_version(version, position=position, pre_release=pre_release)

        self.assertEqual(
            ret,
            exp,
            msg=(
                '\n\n'
                'bump_version({version!r}, '
                'position={position!r}, '
                'pre_release={pre_release!r})\n'
                'expected: {exp!r}\n'
                '     got: {ret!r}\n'
            ).format(
                version=version,
                position=position,
                pre_release=pre_release,
                exp=exp,
                ret=ret
            )
        )
        build_version_info.assert_called_once_with(version)
        build_version_bump_position.assert_called_once_with(position)
        build_version_bump_type.assert_called_once_with(position, pre_release)

    def test_bump_version__08(self) -> None:
        version = '1.2'
        position = 2
        pre_release = 'b'
        bump_type = _BUMP_VERSION_MINOR_BETA
        exp = '1.3b0'
        ver_info = _VersionInfo(
            version=version,
            major=_VersionPart(
                pos=0,
                txt='1',
                num=1,
                pre_txt='',
                pre_num=-1,
                name='major'
            ),
            minor=_VersionPart(
                pos=1,
                txt='2',
                num=2,
                pre_txt='',
                pre_num=-1,
                name='minor'
            ),
            patch=_VersionPart(
                pos=2,
                txt='',
                num=0,
                pre_txt='',
                pre_num=-1,
                name='patch'
            ),
            pre_pos=-1
        )
        patcher = patch(
            'flutils.packages._build_version_info',
            return_value=ver_info
        )
        build_version_info = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.packages._build_version_bump_position',
            return_value=position
        )
        build_version_bump_position = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.packages._build_version_bump_type',
            return_value=bump_type
        )
        build_version_bump_type = patcher.start()
        self.addCleanup(patcher.stop)

        ret = bump_version(version, position=position, pre_release=pre_release)

        self.assertEqual(
            ret,
            exp,
            msg=(
                '\n\n'
                'bump_version({version!r}, '
                'position={position!r}, '
                'pre_release={pre_release!r})\n'
                'expected: {exp!r}\n'
                '     got: {ret!r}\n'
            ).format(
                version=version,
                position=position,
                pre_release=pre_release,
                exp=exp,
                ret=ret
            )
        )
        build_version_info.assert_called_once_with(version)
        build_version_bump_position.assert_called_once_with(position)
        build_version_bump_type.assert_called_once_with(position, pre_release)

    def test_bump_version__09(self) -> None:
        version = '1.2.3'
        position = 3
        pre_release = ''
        bump_type = _BUMP_VERSION_PATCH
        exp = '1.2.4'
        ver_info = _VersionInfo(
            version=version,
            major=_VersionPart(
                pos=0,
                txt='1',
                num=1,
                pre_txt='',
                pre_num=-1,
                name='major'
            ),
            minor=_VersionPart(
                pos=1,
                txt='2',
                num=2,
                pre_txt='',
                pre_num=-1,
                name='minor'
            ),
            patch=_VersionPart(
                pos=2,
                txt='3',
                num=3,
                pre_txt='',
                pre_num=-1,
                name='patch'
            ),
            pre_pos=-1
        )
        patcher = patch(
            'flutils.packages._build_version_info',
            return_value=ver_info
        )
        build_version_info = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.packages._build_version_bump_position',
            return_value=position
        )
        build_version_bump_position = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.packages._build_version_bump_type',
            return_value=bump_type
        )
        build_version_bump_type = patcher.start()
        self.addCleanup(patcher.stop)

        ret = bump_version(version, position=position, pre_release=pre_release)

        self.assertEqual(
            ret,
            exp,
            msg=(
                '\n\n'
                'bump_version({version!r}, '
                'position={position!r}, '
                'pre_release={pre_release!r})\n'
                'expected: {exp!r}\n'
                '     got: {ret!r}\n'
            ).format(
                version=version,
                position=position,
                pre_release=pre_release,
                exp=exp,
                ret=ret
            )
        )
        build_version_info.assert_called_once_with(version)
        build_version_bump_position.assert_called_once_with(position)
        build_version_bump_type.assert_called_once_with(position, pre_release)

    def test_bump_version__10(self) -> None:
        version = '1.140.2b20'
        position = 3
        pre_release = None
        bump_type = _BUMP_VERSION_PATCH
        exp = '1.140.2'
        ver_info = _VersionInfo(
            version=version,
            major=_VersionPart(
                pos=0,
                txt='1',
                num=1,
                pre_txt='',
                pre_num=-1,
                name='major'
            ),
            minor=_VersionPart(
                pos=1,
                txt='140',
                num=140,
                pre_txt='',
                pre_num=-1,
                name='minor'
            ),
            patch=_VersionPart(
                pos=2,
                txt='2b20',
                num=2,
                pre_txt='b',
                pre_num=20,
                name='patch'
            ),
            pre_pos=-1
        )
        patcher = patch(
            'flutils.packages._build_version_info',
            return_value=ver_info
        )
        build_version_info = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.packages._build_version_bump_position',
            return_value=position
        )
        build_version_bump_position = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.packages._build_version_bump_type',
            return_value=bump_type
        )
        build_version_bump_type = patcher.start()
        self.addCleanup(patcher.stop)

        ret = bump_version(version, position=position, pre_release=pre_release)

        self.assertEqual(
            ret,
            exp,
            msg=(
                '\n\n'
                'bump_version({version!r}, '
                'position={position!r}, '
                'pre_release={pre_release!r})\n'
                'expected: {exp!r}\n'
                '     got: {ret!r}\n'
            ).format(
                version=version,
                position=position,
                pre_release=pre_release,
                exp=exp,
                ret=ret
            )
        )
        build_version_info.assert_called_once_with(version)
        build_version_bump_position.assert_called_once_with(position)
        build_version_bump_type.assert_called_once_with(position, pre_release)

    def test_bump_version__11(self) -> None:
        version = '1.140'
        position = 3
        pre_release = None
        bump_type = _BUMP_VERSION_PATCH
        exp = '1.140.1'
        ver_info = _VersionInfo(
            version=version,
            major=_VersionPart(
                pos=0,
                txt='1',
                num=1,
                pre_txt='',
                pre_num=-1,
                name='major'
            ),
            minor=_VersionPart(
                pos=1,
                txt='140',
                num=140,
                pre_txt='',
                pre_num=-1,
                name='minor'
            ),
            patch=_VersionPart(
                pos=2,
                txt='',
                num=0,
                pre_txt='',
                pre_num=-1,
                name='patch'
            ),
            pre_pos=-1
        )
        patcher = patch(
            'flutils.packages._build_version_info',
            return_value=ver_info
        )
        build_version_info = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.packages._build_version_bump_position',
            return_value=position
        )
        build_version_bump_position = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.packages._build_version_bump_type',
            return_value=bump_type
        )
        build_version_bump_type = patcher.start()
        self.addCleanup(patcher.stop)

        ret = bump_version(version, position=position, pre_release=pre_release)

        self.assertEqual(
            ret,
            exp,
            msg=(
                '\n\n'
                'bump_version({version!r}, '
                'position={position!r}, '
                'pre_release={pre_release!r})\n'
                'expected: {exp!r}\n'
                '     got: {ret!r}\n'
            ).format(
                version=version,
                position=position,
                pre_release=pre_release,
                exp=exp,
                ret=ret
            )
        )
        build_version_info.assert_called_once_with(version)
        build_version_bump_position.assert_called_once_with(position)
        build_version_bump_type.assert_called_once_with(position, pre_release)

    def test_bump_version__12(self) -> None:
        version = '1.2.3'
        position = 3
        pre_release = 'a'
        bump_type = _BUMP_VERSION_PATCH_ALPHA
        exp = '1.2.4a0'
        ver_info = _VersionInfo(
            version=version,
            major=_VersionPart(
                pos=0,
                txt='1',
                num=1,
                pre_txt='',
                pre_num=-1,
                name='major'
            ),
            minor=_VersionPart(
                pos=1,
                txt='2',
                num=2,
                pre_txt='',
                pre_num=-1,
                name='minor'
            ),
            patch=_VersionPart(
                pos=2,
                txt='3',
                num=3,
                pre_txt='',
                pre_num=-1,
                name='patch'
            ),
            pre_pos=-1
        )
        patcher = patch(
            'flutils.packages._build_version_info',
            return_value=ver_info
        )
        build_version_info = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.packages._build_version_bump_position',
            return_value=position
        )
        build_version_bump_position = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.packages._build_version_bump_type',
            return_value=bump_type
        )
        build_version_bump_type = patcher.start()
        self.addCleanup(patcher.stop)

        ret = bump_version(version, position=position, pre_release=pre_release)

        self.assertEqual(
            ret,
            exp,
            msg=(
                '\n\n'
                'bump_version({version!r}, '
                'position={position!r}, '
                'pre_release={pre_release!r})\n'
                'expected: {exp!r}\n'
                '     got: {ret!r}\n'
            ).format(
                version=version,
                position=position,
                pre_release=pre_release,
                exp=exp,
                ret=ret
            )
        )
        build_version_info.assert_called_once_with(version)
        build_version_bump_position.assert_called_once_with(position)
        build_version_bump_type.assert_called_once_with(position, pre_release)

    def test_bump_version__13(self) -> None:
        version = '1.2.1b10'
        position = 3
        pre_release = 'a'
        bump_type = _BUMP_VERSION_PATCH_ALPHA
        exp = '1.2.2a0'
        ver_info = _VersionInfo(
            version=version,
            major=_VersionPart(
                pos=0,
                txt='1',
                num=1,
                pre_txt='',
                pre_num=-1,
                name='major'
            ),
            minor=_VersionPart(
                pos=1,
                txt='2',
                num=2,
                pre_txt='',
                pre_num=-1,
                name='minor'
            ),
            patch=_VersionPart(
                pos=2,
                txt='1b10',
                num=1,
                pre_txt='b',
                pre_num=10,
                name='patch'
            ),
            pre_pos=-1
        )
        patcher = patch(
            'flutils.packages._build_version_info',
            return_value=ver_info
        )
        build_version_info = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.packages._build_version_bump_position',
            return_value=position
        )
        build_version_bump_position = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.packages._build_version_bump_type',
            return_value=bump_type
        )
        build_version_bump_type = patcher.start()
        self.addCleanup(patcher.stop)

        ret = bump_version(version, position=position, pre_release=pre_release)

        self.assertEqual(
            ret,
            exp,
            msg=(
                '\n\n'
                'bump_version({version!r}, '
                'position={position!r}, '
                'pre_release={pre_release!r})\n'
                'expected: {exp!r}\n'
                '     got: {ret!r}\n'
            ).format(
                version=version,
                position=position,
                pre_release=pre_release,
                exp=exp,
                ret=ret
            )
        )
        build_version_info.assert_called_once_with(version)
        build_version_bump_position.assert_called_once_with(position)
        build_version_bump_type.assert_called_once_with(position, pre_release)

    def test_bump_version__14(self) -> None:
        version = '1.2.1a137'
        position = 3
        pre_release = 'a'
        bump_type = _BUMP_VERSION_PATCH_ALPHA
        exp = '1.2.1a138'
        ver_info = _VersionInfo(
            version=version,
            major=_VersionPart(
                pos=0,
                txt='1',
                num=1,
                pre_txt='',
                pre_num=-1,
                name='major'
            ),
            minor=_VersionPart(
                pos=1,
                txt='2',
                num=2,
                pre_txt='',
                pre_num=-1,
                name='minor'
            ),
            patch=_VersionPart(
                pos=2,
                txt='1a137',
                num=1,
                pre_txt='a',
                pre_num=137,
                name='patch'
            ),
            pre_pos=-1
        )
        patcher = patch(
            'flutils.packages._build_version_info',
            return_value=ver_info
        )
        build_version_info = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.packages._build_version_bump_position',
            return_value=position
        )
        build_version_bump_position = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.packages._build_version_bump_type',
            return_value=bump_type
        )
        build_version_bump_type = patcher.start()
        self.addCleanup(patcher.stop)

        ret = bump_version(version, position=position, pre_release=pre_release)

        self.assertEqual(
            ret,
            exp,
            msg=(
                '\n\n'
                'bump_version({version!r}, '
                'position={position!r}, '
                'pre_release={pre_release!r})\n'
                'expected: {exp!r}\n'
                '     got: {ret!r}\n'
            ).format(
                version=version,
                position=position,
                pre_release=pre_release,
                exp=exp,
                ret=ret
            )
        )
        build_version_info.assert_called_once_with(version)
        build_version_bump_position.assert_called_once_with(position)
        build_version_bump_type.assert_called_once_with(position, pre_release)

    def test_bump_version__15(self) -> None:
        version = '1.2.1a137'
        position = 3
        pre_release = 'beta'
        bump_type = _BUMP_VERSION_PATCH_BETA
        exp = '1.2.1b0'
        ver_info = _VersionInfo(
            version=version,
            major=_VersionPart(
                pos=0,
                txt='1',
                num=1,
                pre_txt='',
                pre_num=-1,
                name='major'
            ),
            minor=_VersionPart(
                pos=1,
                txt='2',
                num=2,
                pre_txt='',
                pre_num=-1,
                name='minor'
            ),
            patch=_VersionPart(
                pos=2,
                txt='1a137',
                num=1,
                pre_txt='a',
                pre_num=137,
                name='patch'
            ),
            pre_pos=-1
        )
        patcher = patch(
            'flutils.packages._build_version_info',
            return_value=ver_info
        )
        build_version_info = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.packages._build_version_bump_position',
            return_value=position
        )
        build_version_bump_position = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.packages._build_version_bump_type',
            return_value=bump_type
        )
        build_version_bump_type = patcher.start()
        self.addCleanup(patcher.stop)

        ret = bump_version(version, position=position, pre_release=pre_release)

        self.assertEqual(
            ret,
            exp,
            msg=(
                '\n\n'
                'bump_version({version!r}, '
                'position={position!r}, '
                'pre_release={pre_release!r})\n'
                'expected: {exp!r}\n'
                '     got: {ret!r}\n'
            ).format(
                version=version,
                position=position,
                pre_release=pre_release,
                exp=exp,
                ret=ret
            )
        )
        build_version_info.assert_called_once_with(version)
        build_version_bump_position.assert_called_once_with(position)
        build_version_bump_type.assert_called_once_with(position, pre_release)

    def test_bump_version__16(self) -> None:
        version = '1.2.1b137'
        position = 3
        pre_release = 'beta'
        bump_type = _BUMP_VERSION_PATCH_BETA
        exp = '1.2.1b138'
        ver_info = _VersionInfo(
            version=version,
            major=_VersionPart(
                pos=0,
                txt='1',
                num=1,
                pre_txt='',
                pre_num=-1,
                name='major'
            ),
            minor=_VersionPart(
                pos=1,
                txt='2',
                num=2,
                pre_txt='',
                pre_num=-1,
                name='minor'
            ),
            patch=_VersionPart(
                pos=2,
                txt='1b137',
                num=1,
                pre_txt='b',
                pre_num=137,
                name='patch'
            ),
            pre_pos=-1
        )
        patcher = patch(
            'flutils.packages._build_version_info',
            return_value=ver_info
        )
        build_version_info = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.packages._build_version_bump_position',
            return_value=position
        )
        build_version_bump_position = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.packages._build_version_bump_type',
            return_value=bump_type
        )
        build_version_bump_type = patcher.start()
        self.addCleanup(patcher.stop)

        ret = bump_version(version, position=position, pre_release=pre_release)

        self.assertEqual(
            ret,
            exp,
            msg=(
                '\n\n'
                'bump_version({version!r}, '
                'position={position!r}, '
                'pre_release={pre_release!r})\n'
                'expected: {exp!r}\n'
                '     got: {ret!r}\n'
            ).format(
                version=version,
                position=position,
                pre_release=pre_release,
                exp=exp,
                ret=ret
            )
        )
        build_version_info.assert_called_once_with(version)
        build_version_bump_position.assert_called_once_with(position)
        build_version_bump_type.assert_called_once_with(position, pre_release)

    def test_bump_version__17(self) -> None:
        version = '7.6.14'
        position = 3
        pre_release = 'beta'
        bump_type = _BUMP_VERSION_PATCH_BETA
        exp = '7.6.15b0'
        ver_info = _VersionInfo(
            version=version,
            major=_VersionPart(
                pos=0,
                txt='7',
                num=7,
                pre_txt='',
                pre_num=-1,
                name='major'
            ),
            minor=_VersionPart(
                pos=1,
                txt='6',
                num=6,
                pre_txt='',
                pre_num=-1,
                name='minor'
            ),
            patch=_VersionPart(
                pos=2,
                txt='14',
                num=14,
                pre_txt='',
                pre_num=-1,
                name='patch'
            ),
            pre_pos=-1
        )
        patcher = patch(
            'flutils.packages._build_version_info',
            return_value=ver_info
        )
        build_version_info = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.packages._build_version_bump_position',
            return_value=position
        )
        build_version_bump_position = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.packages._build_version_bump_type',
            return_value=bump_type
        )
        build_version_bump_type = patcher.start()
        self.addCleanup(patcher.stop)

        ret = bump_version(version, position=position, pre_release=pre_release)

        self.assertEqual(
            ret,
            exp,
            msg=(
                '\n\n'
                'bump_version({version!r}, '
                'position={position!r}, '
                'pre_release={pre_release!r})\n'
                'expected: {exp!r}\n'
                '     got: {ret!r}\n'
            ).format(
                version=version,
                position=position,
                pre_release=pre_release,
                exp=exp,
                ret=ret
            )
        )
        build_version_info.assert_called_once_with(version)
        build_version_bump_position.assert_called_once_with(position)
        build_version_bump_type.assert_called_once_with(position, pre_release)
