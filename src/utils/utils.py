import os
import random
import string
from datetime import datetime
from typing import Dict, List


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


def generate_random_id(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def get_current_time_as_string() -> str:
    return datetime.now().strftime("%d-%m-%Y_%H-%M-%S")


def get_all_files_with_extension_in_directory(directory: str, extension: str = '.json'):
    assert isinstance(directory, str), "directory parameter must be a string"
    assert isinstance(extension, str), "extension parameter must be a string"

    all_files = os.listdir(directory)
    files_with_extension = [file for file in all_files if file[-(len(extension)):] == extension]

    return files_with_extension
