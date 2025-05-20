"""
Utility class to load YAML config file and prompt file.

[4] Nkmk, “Get the path of the current file (script) in Python: __file__,”
    note.nkmk.me, Aug. 2023. [Online].
    Available: https://note.nkmk.me/en/python-script-file-path/

"""
from dataclasses import dataclass
from enum import Enum
from yaml import safe_load, dump
from pathlib import Path
from typing import ClassVar
from abc import ABC, abstractmethod
import os


class YAMLLoader(ABC):
    """
    Base class for the loading of YAML files.
    """
    class YAMLException(Exception):
        pass

    @classmethod
    def file_exists(cls):
        """
        Verifies if a file exists

        Returns:
            True if the file exists, False otherwise
        """
        return Path(cls.get_abs_path()).is_file()

    @classmethod
    def create_file(cls):
        """
        Creates the YAML file.
        """
        Path(cls.get_abs_path()).touch()

    @classmethod
    def get_contents(cls):
        """
        Retrieve the contents of the YAML file.

        Raises:
            YAMLLoader.YAMLException: Error with reading the file contents.

        Returns:
            The data stored in the file
        """
        try:
            with open(cls.get_abs_path(), mode='r') as file:
                return safe_load(file)
        except Exception as e:
            raise YAMLLoader.YAMLException(
                f"Error retrieiving the configuration file: {e}"
            )

    @classmethod
    def _write_contents(cls, data):
        """
        Writes the contents to the YAML file.

        Args:
            data: The data to write

        Raises:
            YAMLLoader.YAMLException: Error writing to the file.
        """
        try:
            with open(cls.get_abs_path(), mode="w+") as file:
                file.write(dump(data))
        except Exception:
            raise YAMLLoader.YAMLException(
                f"Error writing to configuration file: {cls.get_abs_path()}"
            )

    @classmethod
    def get_abs_path(cls):
        """
        Get the absolute value for the path of a file.

        Returns:
            File path.
        """
        directory = os.path.dirname(os.path.abspath(__file__))
        parent_directory = os.path.dirname(directory)
        return os.path.join(parent_directory, "config", cls.PATH)

    @staticmethod
    @abstractmethod
    def validate():  # pragma: no cover
        pass


@dataclass
class Prompt(YAMLLoader):
    PATH: ClassVar[str] = 'prompt.yml'

    class PromptKeys(Enum):
        """
        Useful for having a shared state for PromptKeys.
        """
        CODE_GEN = "code_generation"
        DES_GEN = "description_generation"
        CJ_ANALYSER = "codejudge_analyse"
        CJ_SUMMARISE = "codejudge_summarise"

        @staticmethod
        def get_keys():
            """
            Returns the PromptKeys

            Returns:
                The prompt description keys.
            """
            return set(prompt.value for prompt in Prompt.PromptKeys)

    @staticmethod
    def validate():
        """
        Ensures that:
            - File exists
            - File hasn't been modified
            - File isn't empty

        Raises:
            YAMLLoader.YAMLException: If the file does not exist or this tool
            is not configured properly.
        """
        if not Prompt.file_exists():
            raise YAMLLoader.YAMLException(
                "The YAML prompt file does not exist, run setup"
            )

        contents = Prompt.get_contents()
        if Prompt.PromptKeys.get_keys() != contents.keys():
            raise YAMLLoader.YAMLException(
                "YAML prompt file is incorrectly formatted"
            )

        if "" in contents.values():
            raise YAMLLoader.YAMLException(
                "YAML prompt contains empty values"
            )


@dataclass
class Config(YAMLLoader):
    """ 
    This class holds the concrete implementation for
    the configuration file
    """
    tenant: str
    unit: str
    api: str
    label: str
    github: str
    repository_name: str
    repository_branch: str
    model: str
    model_path: str
    PATH: ClassVar[str] = 'config.yml'

    class ConfigKeys(Enum):
        """ Content keys to maintain a shared state"""
        IBM_TENANT = "IBM_Tenant"
        IBM_UNIT = "IBM_Unit"
        IBM_KEY = "IBM_Key"
        IBM_LABEL = "IBM_Label"
        GITHUB = "GitHub"
        REPOSITORY = "Repository"
        BRANCH = "Branch"
        MODEL = "Model"
        MODEL_PATH = "ModelPath"

        @staticmethod
        def get_keys():
            """
            Returns the ConfigKeys

            Returns:
                A set of keys representing the config parameters.
            """
            return set(config.value for config in Config.ConfigKeys)

    def store_data(self):
        """Stores config data to a file """
        config = Config.ConfigKeys
        data = {
            config.IBM_TENANT.value: self.tenant,
            config.IBM_UNIT.value: self.unit,
            config.IBM_KEY.value: self.api,
            config.IBM_LABEL.value: self.label,
            config.GITHUB.value: self.github,
            config.REPOSITORY.value: self.repository_name,
            config.BRANCH.value: self.repository_branch,
            config.MODEL.value: self.model,
            config.MODEL_PATH.value: self.model_path
        }
        super()._write_contents(data)

    @staticmethod
    def validate():
        """ 
        Ensures that:
            - File exists
            - File hasn't been modified
            - File isn't empty

        Raises:
            YAMLLoader.YAMLException: If the file does not exist or this
            tool is not configured properly.
        """
        if not Config.file_exists():
            raise YAMLLoader.YAMLException(
                "The YAML config file does not exist, run setup"
            )

        contents = Config.get_contents()
        if Config.ConfigKeys.get_keys() != contents.keys():
            raise YAMLLoader.YAMLException(
                "YAML config file is incorrectly formatted, run setup"
            )

        if "" in contents.values():
            raise YAMLLoader.YAMLException(
                "YAML config contains empty values, run setup"
            )
