import json
from abc import ABC, abstractmethod
from typing import List, Dict

from src import Constants
from src.models import ConfigurationFile
from src.utils.utils import get_current_time_as_string, generate_random_id, get_all_files_with_extension_in_directory


class ConfigurationFileGateway(ABC):

    @abstractmethod
    def save(self, configuration_file: ConfigurationFile) -> Dict:
        pass

    @abstractmethod
    def get_all_configuration_files_data(self) -> List[Dict]:
        pass


class JsonConfigurationFileGateway(ConfigurationFileGateway):
    def save(self, configuration_file: ConfigurationFile) -> Dict:
        filename = self._get_configuration_file_name(configuration_file)
        abs_path = self._get_configuration_dir_absolute_path(filename)

        configuration_file_as_dict = configuration_file.to_dict()

        with open(abs_path, 'x') as json_file:
            json.dump(configuration_file_as_dict, json_file)

        return {
            'filename': filename,
            'configuration': configuration_file_as_dict
        }

    def get_all_configuration_files_data(self) -> List[Dict]:
        json_files = self._get_all_files_with_json_extension_in_directory()

        configuration_files_data = []

        for file in json_files:
            asb_path = self._get_configuration_dir_absolute_path(file)
            with open(asb_path, 'r') as f:
                # TODO add metadata dict field
                configuration_files_data.append(json.load(f))

        return configuration_files_data

    @staticmethod
    def _get_configuration_file_name(configuration_file: ConfigurationFile):
        assert isinstance(configuration_file, ConfigurationFile)

        timestamp = get_current_time_as_string()
        random_id = generate_random_id()
        env_name = configuration_file.get_environment_name()

        return f"{env_name}_{configuration_file.algorithm}_{random_id}_{timestamp}.json"

    @staticmethod
    def _get_configuration_dir_absolute_path(filename):
        assert isinstance(filename, str), "filename parameter must be a string"

        configurations_dir = Constants.RL_CONFIGURATIONS
        path = f"{configurations_dir}/{filename}"

        return path

    @staticmethod
    def _get_all_files_with_json_extension_in_directory():
        return get_all_files_with_extension_in_directory(Constants.RL_CONFIGURATIONS, '.json')


class ConfigurationFileGatewayFactory:
    CONFIGURATION_FILE_GATEWAY_MAPPING = {
        'json': JsonConfigurationFileGateway,
        'default': JsonConfigurationFileGateway
    }

    @staticmethod
    def get_gateway(gateway_type: str) -> ConfigurationFileGateway:
        configuration_file_gateway_class = ConfigurationFileGatewayFactory.CONFIGURATION_FILE_GATEWAY_MAPPING.get(
            gateway_type, None)

        if configuration_file_gateway_class is None:
            raise ValueError(f"Unknown gateway type: {gateway_type}")

        return configuration_file_gateway_class()

    @staticmethod
    def get_default_gateway() -> ConfigurationFileGateway:
        return ConfigurationFileGatewayFactory.get_gateway('default')
