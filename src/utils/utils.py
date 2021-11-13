import os
import random
import string
from datetime import datetime
from typing import Dict, Tuple, List

from src import Constants
from src.models import TrainingResults
from src.repository import AlgorithmRepository
from src.utils.data_validators import get_acer_acerac_parser, get_other_algorithms_parser


def all_required_config_fields(data: Dict) -> Tuple[bool, str]:
    if Constants.REQUIRED_CONFIG_FIELDS != set(data.keys()):
        return False, f"Config must have fields: {Constants.REQUIRED_CONFIG_FIELDS}"
    return True, ''


def check_algorithm_config(data: Dict) -> Tuple[bool, str]:
    if not algorithm_known(data['algorithm']):
        return False, f"Unknown algorithm: {data['algorithm']}"

    if data['algorithm'] in {'acer', 'acerac'}:
        parser = get_acer_acerac_parser()
    else:
        parser = get_other_algorithms_parser()

    config_as_list = get_args_as_list_of_strings(data['algorithm_config'])

    parser.parse_args(config_as_list)

    if parser.error_message:
        return False, parser.error_message

    return True, ""


def algorithm_known(algorithm: str) -> bool:
    return algorithm in Constants.KNOWN_ALGORITHMS


def get_args_as_list_of_strings(data: Dict) -> List[str]:
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


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def get_environment_name_from_data(data: Dict):
    assert isinstance(data, dict) and "algorithm" in data.keys()

    algorithm = data['algorithm']
    if algorithm in {'acer', 'acerac'}:
        key = 'env_name'
    else:
        key = 'env'

    return data['algorithm_config'][key]


def get_configuration_file_name(data: Dict) -> str:
    assert isinstance(data, dict) and "algorithm" in data.keys()

    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y_%H-%M-%S")

    random_id = id_generator()
    env_name = get_environment_name_from_data(data)

    return f"{env_name}_{data['algorithm']}_{random_id}_{dt_string}.json"


def get_configuration_absolute_path(filename: str) -> str:
    assert isinstance(filename, str), "filename parameter must be a string"

    configurations_dir = Constants.RL_CONFIGURATIONS
    path = f"{configurations_dir}/{filename}"

    return path


def get_all_files_with_extension_in_directory(directory: str, extension: str = '.json'):
    assert isinstance(directory, str), "directory parameter must be a string"
    assert isinstance(extension, str), "extension parameter must be a string"

    all_files = os.listdir(directory)
    files_with_extension = [file for file in all_files if file[-(len(extension)):] == extension]

    return files_with_extension


def add_utility_config_extensions(config: Dict) -> Dict:
    assert isinstance(config, dict), "configuration must be a dictionary"
    assert {"algorithm", "algorithm_config"} == set(config.keys())

    if config['algorithm'] in {'acer', 'acerac'}:
        config = add_random_experiment_name(config)

    return config


def add_random_experiment_name(config: Dict) -> Dict:
    if "experiment_name" not in config['algorithm_config'].keys():
        random_id = id_generator()
        config['algorithm_config']['experiment_name'] = random_id

    return config


def training_results_to_dict(training_results: TrainingResults):
    return {
        "result_id": training_results.result_id,
        "best_mean_result": training_results.best_mean_result,
        "results_subdirectory": training_results.results_subdirectory,
        "environment": training_results.environment,
        "algorithm_config": training_results.algorithm_config,
        "date": training_results.date,
        "algorithm": AlgorithmRepository.get_algorithm_by_id(training_results.algorithm).name
    }
