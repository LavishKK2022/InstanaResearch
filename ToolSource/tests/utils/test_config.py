from unittest.mock import patch
from aioptim.utils.config import YAMLLoader, Config, Prompt
import os
from pathlib import Path
import pytest
from yaml import safe_load


@pytest.fixture
def directory():
    return os.path.dirname(os.path.abspath(__file__))


@pytest.fixture
def parent_directory(directory):
    return os.path.dirname(directory)


@pytest.fixture
def real_config(parent_directory):
    return os.path.join(parent_directory, "config", "test_config.yml")


@pytest.fixture
def test_config(parent_directory):
    return os.path.join(parent_directory, "config", "create-config.yml")


@pytest.fixture
def write_config(parent_directory):
    return os.path.join(parent_directory, "config", "test_write.yml")


def test_YAMLLoader_file_exists(parent_directory, real_config):

    with patch.object(YAMLLoader, "get_abs_path", return_value=parent_directory):
        assert not YAMLLoader.file_exists()

    with patch.object(YAMLLoader, "get_abs_path", return_value=real_config):
        assert Config.file_exists()

    with patch.object(YAMLLoader, "get_abs_path", return_value=""):
        assert not Config.file_exists()


def test_YAMLLoader_create_file(test_config):
    with patch.object(YAMLLoader, "get_abs_path", return_value=test_config):
        YAMLLoader.create_file()
        path = Path(test_config)
        assert path.is_file()
        path.unlink()


def test_YAMLLoader_get_contents(real_config):
    with patch.object(YAMLLoader, "get_abs_path", return_value=real_config):
        assert YAMLLoader.get_contents() == {
            'Branch': 'main',
            'GitHub': 'github_PAT',
            'IBM_Key': 'apiToken',
            'IBM_Label': 'robot',
            'IBM_Tenant': 'kep',
            'IBM_Unit': 'testing',
            'Model': 'codellama:34b-instruct-q4_K_M',
            'ModelPath': 'somePath',
            'Repository': 'priv-robot-shop'}

    with patch.object(YAMLLoader, "get_abs_path", return_value=""):
        with pytest.raises(YAMLLoader.YAMLException):
            YAMLLoader.get_contents()


def test_YAMLLoader_write_contents(write_config):
    data = {"test": "testdata"}
    with patch.object(YAMLLoader, "get_abs_path", return_value=write_config):
        YAMLLoader._write_contents(data)
        with open(write_config, mode='r') as file:
            assert safe_load(file) == data
    Path(write_config).unlink()

def test_YAMLLoader_write_contents_exception(write_config):
    data = {"test": "testdata"}
    Path.touch(write_config)
    os.chmod(write_config, 0)
    with patch.object(YAMLLoader, "get_abs_path", return_value=write_config):
        with pytest.raises(YAMLLoader.YAMLException):
            YAMLLoader._write_contents(data)
    Path(write_config).unlink()


def test_YAMLLoader_get_abs_path(parent_directory):
    config = os.path.join(parent_directory, "config", "config.yml")
    prompt = os.path.join(parent_directory, "config", "prompt.yml")
    with patch("os.path.abspath", return_value=__file__):
        assert Config.get_abs_path() == config
        assert Prompt.get_abs_path() == prompt


def test_Prompt_validation():
    with patch.object(Prompt, "file_exists", return_value=False):
        with pytest.raises(YAMLLoader.YAMLException):
            Prompt.validate()
    with patch.object(Prompt, "file_exists", return_value=True):
        with patch.object(Prompt, "get_contents", return_value={}):
            with pytest.raises(YAMLLoader.YAMLException):
                Prompt.validate()

    with patch.object(Prompt, "file_exists", return_value=True):
        with patch.object(Prompt, "get_contents", return_value={
            'code_generation': "",
            'codejudge_analyse': "",
            'codejudge_summarise': "",
            'description_generation': ""
        }
        ):
            with pytest.raises(YAMLLoader.YAMLException):
                Prompt.validate()

    with patch.object(Prompt, "file_exists", return_value=True):
        with patch.object(Prompt, "get_contents", return_value={
            'code_generation': "test",
            'codejudge_analyse': "test",
            'codejudge_summarise': "test",
            'description_generation': "test"
        }
        ):
            Prompt.validate()


def test_Config_validatation():
    with patch.object(Config, "file_exists", return_value=False):
        with pytest.raises(YAMLLoader.YAMLException):
            Config.validate()

    with patch.object(Config, "file_exists", return_value=True):
        with patch.object(Config, "get_contents", return_value={}):
            with pytest.raises(YAMLLoader.YAMLException):
                Config.validate()

    with patch.object(Config, "file_exists", return_value=True):
        with patch.object(Config, "get_contents", return_value={
                'ModelPath': "",
                'IBM_Label': "",
                'Branch': "",
                'Repository': "",
                'IBM_Key': "",
                'IBM_Unit': "",
                'IBM_Tenant': "",
                'Model': "",
                'GitHub': ""
            }
        ):
            with pytest.raises(YAMLLoader.YAMLException):
                Config.validate()

    with patch.object(Config, "file_exists", return_value=True):
        with patch.object(Config, "get_contents", return_value={
                'ModelPath': "test",
                'IBM_Label': "test",
                'Branch': "test",
                'Repository': "test",
                'IBM_Key': "test",
                'IBM_Unit': "test",
                'IBM_Tenant': "test",
                'Model': "test",
                'GitHub': "test"
            }
        ):
            Config.validate()


def test_Config_store_data():
    config = Config(*(["test"] * 9))
    with patch.object(YAMLLoader, "_write_contents") as mocked_method:
        config.store_data()
        assert mocked_method.call_args[0][0] == {
            'IBM_Tenant': 'test',
            'IBM_Unit': 'test',
            'IBM_Key': 'test',
            'IBM_Label': 'test',
            'GitHub': 'test',
            'Repository': 'test',
            'Branch': 'test',
            'Model': 'test',
            'ModelPath': 'test'
        }


def test_ConfigKeys_get_keys():
    assert Config.ConfigKeys.get_keys() == {
        'ModelPath',
        'IBM_Label',
        'Branch',
        'Repository',
        'IBM_Key',
        'IBM_Unit',
        'IBM_Tenant',
        'Model',
        'GitHub'
    }


def test_PromptKeys_get_keys():
    assert Prompt.PromptKeys.get_keys() == {
        'code_generation',
        'codejudge_analyse',
        'codejudge_summarise',
        'description_generation'
    }
