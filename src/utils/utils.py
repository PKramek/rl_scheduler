from datetime import datetime
from typing import Dict, Tuple, List

from src.utils.acer_acerac_parsers import get_acer_acerac_parser


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
                    for sub_value in value:
                        result.append(f"{sub_value}")
                else:
                    result.append(f"{value}")

    return result


def check_acer_acerac_config(data: Dict) -> Tuple[bool, str]:
    config_as_list = get_args_as_list_of_strings(data)
    parser = get_acer_acerac_parser()
    parser.parse_args(config_as_list)

    if parser.error_message:
        return False, parser.error_message

    return True, ""


# TODO
def check_other_algorithms_config(data: Dict) -> Tuple[bool, str]:
    return True, ""


def required_fields(data: Dict) -> Tuple[bool, str]:
    assert isinstance(data, dict)
    if {"algorithm", "algorithm_config"} != set(data.keys()):
        return False, "Invalid fields"

    if data["algorithm"] in ("acer", "acerac"):
        return check_acer_acerac_config(data['algorithm_config'])
    else:
        return check_other_algorithms_config(data)


def get_configuration_file_name(data: Dict) -> str:
    assert isinstance(data, dict) and "algorithm" in data.keys()

    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y_%H-%M-%S")

    return f"{data['algorithm']}_{dt_string}"
