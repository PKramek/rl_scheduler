from datetime import datetime
from typing import Dict, Tuple, List

from src import Constants
from src.utils.acer_acerac_parsers import get_acer_acerac_parser


def config_correct(data: Dict) -> Tuple[bool, str]:
    assert isinstance(data, dict)

    if not all_required_config_fields(data):
        return False, f"Config must have fields: {Constants.REQUIRED_CONFIG_FIELDS}"

    return check_algorithm_config(data)


def all_required_config_fields(data: Dict) -> bool:
    if Constants.REQUIRED_CONFIG_FIELDS != set(data.keys()):
        return False
    return True


def check_algorithm_config(data: Dict) -> Tuple[bool, str]:
    if not algorithm_known(data['algorithm']):
        return False, f"Unknown algorithm: {data['algorithm']}"

    if data['algorithm'] in {'acer', 'acerac'}:
        parser = get_acer_acerac_parser()
    else:
        raise NotImplementedError()

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


def get_configuration_file_name(data: Dict) -> str:
    assert isinstance(data, dict) and "algorithm" in data.keys()

    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y_%H-%M-%S")

    return f"{data['algorithm']}_{dt_string}.json"


def get_configuration_absolute_path(filename: str) -> str:
    configurations_dir = Constants.FLASK_CONFIGURATIONS_DIRECTORY
    path = f"{configurations_dir}/{filename}"

    return path
