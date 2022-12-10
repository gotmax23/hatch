import pytest

from hatchling.builders.hooks.version import VersionBuildHook
from hatchling.metadata.core import ProjectMetadata
from hatchling.plugin.manager import PluginManager
from hatchling.utils.constants import DEFAULT_BUILD_SCRIPT


class TestConfigPath:
    def test_correct(self, isolation):
        config = {'path': 'foo/bar.py'}
        hook = VersionBuildHook(str(isolation), config, None, None, '', '')

        assert hook.config_path == hook.config_path == 'foo/bar.py'

    def test_missing(self, isolation):
        config = {'path': ''}
        hook = VersionBuildHook(str(isolation), config, None, None, '', '')

        with pytest.raises(ValueError, match='Option `path` for build hook `version` is required'):
            _ = hook.config_path

    def test_not_string(self, isolation):
        config = {'path': 9000}
        hook = VersionBuildHook(str(isolation), config, None, None, '', '')

        with pytest.raises(TypeError, match='Option `path` for build hook `version` must be a string'):
            _ = hook.config_path


class TestConfigTemplate:
    def test_correct(self, isolation):
        config = {'template': 'foo'}
        hook = VersionBuildHook(str(isolation), config, None, None, '', '')

        assert hook.config_template == hook.config_template == 'foo'

    def test_not_string(self, isolation):
        config = {'template': 9000}
        hook = VersionBuildHook(str(isolation), config, None, None, '', '')

        with pytest.raises(TypeError, match='Option `template` for build hook `version` must be a string'):
            _ = hook.config_template


class TestConfigPattern:
    def test_correct(self, isolation):
        config = {'pattern': 'foo'}
        hook = VersionBuildHook(str(isolation), config, None, None, '', '')

        assert hook.config_pattern == hook.config_pattern == 'foo'

    def test_not_string(self, isolation):
        config = {'pattern': 9000}
        hook = VersionBuildHook(str(isolation), config, None, None, '', '')

        with pytest.raises(TypeError, match='Option `pattern` for build hook `version` must be a string'):
            _ = hook.config_pattern


class TestTemplate:
    def test_default(self, temp_dir, helpers):
        config = {'path': 'baz.py'}
        metadata = ProjectMetadata(
            str(temp_dir),
            PluginManager(),
            {
                'project': {'name': 'foo', 'dynamic': ['version']},
                'tool': {'hatch': {'metadata': {'hooks': {'custom': {}}}}},
            },
        )

        file_path = temp_dir / DEFAULT_BUILD_SCRIPT
        file_path.write_text(
            helpers.dedent(
                """
                from hatchling.metadata.plugin.interface import MetadataHookInterface

                class CustomHook(MetadataHookInterface):
                    def update(self, metadata):
                        metadata['version'] = '1.2.3'
                """
            )
        )

        build_data = {'artifacts': []}
        hook = VersionBuildHook(str(temp_dir), config, None, metadata, '', '')
        hook.initialize([], build_data)

        expected_file = temp_dir / 'baz.py'
        assert expected_file.is_file()
        assert expected_file.read_text() == helpers.dedent(
            """
            # This file is auto-generated by Hatchling. As such, do not:
            #   - modify
            #   - track in version control e.g. be sure to add to .gitignore
            __version__ = VERSION = '1.2.3'
            """
        )
        assert build_data['artifacts'] == ['/baz.py']

    def test_create_necessary_directories(self, temp_dir, helpers):
        config = {'path': 'bar/baz.py'}
        metadata = ProjectMetadata(
            str(temp_dir),
            PluginManager(),
            {
                'project': {'name': 'foo', 'dynamic': ['version']},
                'tool': {'hatch': {'metadata': {'hooks': {'custom': {}}}}},
            },
        )

        file_path = temp_dir / DEFAULT_BUILD_SCRIPT
        file_path.write_text(
            helpers.dedent(
                """
                from hatchling.metadata.plugin.interface import MetadataHookInterface

                class CustomHook(MetadataHookInterface):
                    def update(self, metadata):
                        metadata['version'] = '1.2.3'
                """
            )
        )

        build_data = {'artifacts': []}
        hook = VersionBuildHook(str(temp_dir), config, None, metadata, '', '')
        hook.initialize([], build_data)

        expected_file = temp_dir / 'bar' / 'baz.py'
        assert expected_file.is_file()
        assert expected_file.read_text() == helpers.dedent(
            """
            # This file is auto-generated by Hatchling. As such, do not:
            #   - modify
            #   - track in version control e.g. be sure to add to .gitignore
            __version__ = VERSION = '1.2.3'
            """
        )
        assert build_data['artifacts'] == ['/bar/baz.py']

    def test_custom(self, temp_dir, helpers):
        config = {'path': 'baz.py', 'template': 'VER = {version!r}\n'}
        metadata = ProjectMetadata(
            str(temp_dir),
            PluginManager(),
            {
                'project': {'name': 'foo', 'dynamic': ['version']},
                'tool': {'hatch': {'metadata': {'hooks': {'custom': {}}}}},
            },
        )

        file_path = temp_dir / DEFAULT_BUILD_SCRIPT
        file_path.write_text(
            helpers.dedent(
                """
                from hatchling.metadata.plugin.interface import MetadataHookInterface

                class CustomHook(MetadataHookInterface):
                    def update(self, metadata):
                        metadata['version'] = '1.2.3'
                """
            )
        )

        build_data = {'artifacts': []}
        hook = VersionBuildHook(str(temp_dir), config, None, metadata, '', '')
        hook.initialize([], build_data)

        expected_file = temp_dir / 'baz.py'
        assert expected_file.is_file()
        assert expected_file.read_text() == helpers.dedent(
            """
            VER = '1.2.3'
            """
        )
        assert build_data['artifacts'] == ['/baz.py']


class TestPattern:
    def test_default(self, temp_dir, helpers):
        config = {'path': 'baz.py', 'pattern': True}
        metadata = ProjectMetadata(
            str(temp_dir),
            PluginManager(),
            {
                'project': {'name': 'foo', 'dynamic': ['version']},
                'tool': {'hatch': {'metadata': {'hooks': {'custom': {}}}}},
            },
        )

        file_path = temp_dir / DEFAULT_BUILD_SCRIPT
        file_path.write_text(
            helpers.dedent(
                """
                from hatchling.metadata.plugin.interface import MetadataHookInterface

                class CustomHook(MetadataHookInterface):
                    def update(self, metadata):
                        metadata['version'] = '1.2.3'
                """
            )
        )
        version_file = temp_dir / 'baz.py'
        version_file.write_text(
            helpers.dedent(
                """
                __version__ = '0.0.0'
                """
            )
        )

        build_data = {'artifacts': []}
        hook = VersionBuildHook(str(temp_dir), config, None, metadata, '', '')
        hook.initialize([], build_data)

        assert version_file.read_text() == helpers.dedent(
            """
            __version__ = '1.2.3'
            """
        )
        assert build_data['artifacts'] == ['/baz.py']

    def test_custom(self, temp_dir, helpers):
        config = {'path': 'baz.py', 'pattern': 'v = "(?P<version>.+)"'}
        metadata = ProjectMetadata(
            str(temp_dir),
            PluginManager(),
            {
                'project': {'name': 'foo', 'dynamic': ['version']},
                'tool': {'hatch': {'metadata': {'hooks': {'custom': {}}}}},
            },
        )

        file_path = temp_dir / DEFAULT_BUILD_SCRIPT
        file_path.write_text(
            helpers.dedent(
                """
                from hatchling.metadata.plugin.interface import MetadataHookInterface

                class CustomHook(MetadataHookInterface):
                    def update(self, metadata):
                        metadata['version'] = '1.2.3'
                """
            )
        )
        version_file = temp_dir / 'baz.py'
        version_file.write_text(
            helpers.dedent(
                """
                v = "0.0.0"
                """
            )
        )

        build_data = {'artifacts': []}
        hook = VersionBuildHook(str(temp_dir), config, None, metadata, '', '')
        hook.initialize([], build_data)

        assert version_file.read_text() == helpers.dedent(
            """
            v = "1.2.3"
            """
        )
        assert build_data['artifacts'] == ['/baz.py']
