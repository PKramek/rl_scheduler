from typing import Tuple, Dict, List

from src import Constants
from src.utils.data_validators import ParserFactory
from src.utils.utils import get_args_as_list_of_strings, id_generator


class Configuration:
    def __init__(self, data: Dict):
        self.data = data
        self._data_valid = False

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data: dict):
        assert isinstance(data, dict), 'Data must be a dictionary'
        self._data = data
        self._data_valid = False

    def all_required_fields(self) -> bool:
        if Constants.REQUIRED_CONFIG_FIELDS != set(self.data.keys()):
            return False
        return True

    def algorithm_known(self) -> bool:
        algorithm = self.data['algorithm']
        return algorithm in Constants.KNOWN_ALGORITHMS

    def is_config_valid_for_algorithm(self) -> Tuple[bool, str]:
        parser = ParserFactory.get_parser(self.data['algorithm'])
        algorithm_configuration = self.data['algorithm_config']
        algorithm_config_as_list = get_args_as_list_of_strings(algorithm_configuration)

        parser.parse_args(algorithm_config_as_list)

        if parser.error_message:
            return False, parser.error_message

        return True, ""

    def add_utility_config_extensions(self) -> Dict:
        if self.data['algorithm'] in {'acer', 'acerac'}:
            config = self._add_random_experiment_name()

        return config

    def _add_random_experiment_name(self) -> Dict:
        if "experiment_name" not in self.data['algorithm_config'].keys():
            random_id = id_generator()
            self.data['algorithm_config']['experiment_name'] = random_id

    @staticmethod
    def get_algorithm_args_as_list_of_strings(data: Dict) -> List[str]:
        result = []

        for key, value in data.items():
            if value is not None and value != '':
                if isinstance(value, bool):
                    if value is True:
                        result.append(f"--{key}")
                else:
                    result.append(f"--{key}")
                    if isinstance(value, list) or isinstance(value, tuple):
                        # elements of the list must be separate in args
                        for sub_value in value:
                            result.append(f"{sub_value}")
                    else:
                        result.append(f"{value}")

        return result
