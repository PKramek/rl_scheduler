from datetime import datetime
from typing import Dict, Tuple


# datetime object containing current date and time

# TODO
def check_acer_acerac_config(data: Dict) -> Tuple[bool, str]:
    return True, ""


# TODO
def check_other_algorithms_config(data: Dict) -> Tuple[bool, str]:
    return True, ""


def required_fields(data: Dict) -> Tuple[bool, str]:
    assert isinstance(data, dict)
    if ("algorithm", "algorithm_config") != set(data.keys()):
        return False, "Invalid fields"

    if data["algorithm"] in ("acer", "acerac"):
        return check_acer_acerac_config(data)
    else:
        return check_other_algorithms_config(data)


def get_configuration_file_name(data: Dict) -> str:
    assert isinstance(data, dict) and "algorithm" in data.keys()

    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y_%H-%M-%S")

    return f"{data['algorithm']}_{dt_string}"
