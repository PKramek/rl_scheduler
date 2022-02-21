from typing import Dict

from sqlalchemy import ForeignKey

from src import db, Constants
from src.utils.data_validators import ParserFactory
from src.utils.exceptions import UnknownAlgorithmException, NotValidAlgorithmException, \
    NotAllRequiredConfigurationFields
from src.utils.utils import get_args_as_list_of_strings


class Algorithm(db.Model):
    __tablename__ = 'algorithm'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)

    def __repr__(self):
        return f"<Algorithm(name={self.name})>"


class TrainingResults(db.Model):
    __tablename__ = 'training_results'
    result_id = db.Column(db.Integer, primary_key=True)
    best_mean_result = db.Column(db.Float, nullable=False)
    results_subdirectory = db.Column(db.String, nullable=False)
    environment = db.Column(db.String, nullable=False)
    algorithm_config = db.Column(db.String, nullable=False)
    date = db.Column(db.TIMESTAMP(), nullable=False)
    algorithm = db.Column(db.Integer, ForeignKey('algorithm.id'))

    def __repr__(self):
        return f"""<TrainingResults(best_mean_result={self.best_mean_result},
                results_subdirectory={self.results_subdirectory},
                environment={self.environment},
                algorithm_config={self.algorithm_config},
                date={self.date},
                algorithm={self.algorithm}
                )>"""


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50))
    name = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))
    admin = db.Column(db.Boolean)


class ConfigurationFile():
    def __init__(self, algorithm: str, algorithm_config: Dict, parser_factory=ParserFactory()):
        self._algorithm = None
        self._algorithm_config = None

        self.algorithm = algorithm

        assert hasattr(parser_factory, 'get_parser'), "Parser Factory must have a method called 'get_parser'"
        self._parser_factory = parser_factory

        self.algorithm_config = algorithm_config

    @staticmethod
    def from_dict(data: Dict, parser_factory=ParserFactory()) -> 'ConfigurationFile':
        if not Constants.REQUIRED_CONFIG_FIELDS != set(data.keys()):
            raise NotAllRequiredConfigurationFields(f"Config must have fields: {Constants.REQUIRED_CONFIG_FIELDS}")

        configuration_file = ConfigurationFile(
            data["algorithm"], data["algorithm_config"], parser_factory
        )

        return configuration_file

    def to_dict(self) -> Dict:
        if self.algorithm is None or self.algorithm_config is None:
            raise NotAllRequiredConfigurationFields()

        return {
            "algorithm": self.algorithm,
            "algorithm_config": self.algorithm_config
        }

    @property
    def algorithm(self) -> str:
        return self._algorithm

    @algorithm.setter
    def algorithm(self, algorithm: str):
        if algorithm not in Constants.KNOWN_ALGORITHMS:
            raise UnknownAlgorithmException(
                f"Algorithm must be one of values: {Constants.KNOWN_ALGORITHMS}, not {algorithm}"
            )
        self._algorithm = algorithm

    @property
    def algorithm_config(self) -> Dict:
        return self._algorithm_config

    @algorithm_config.setter
    def algorithm_config(self, algorithm_config: Dict):
        assert self.algorithm is not None

        parser = self._parser_factory.get_parser(self.algorithm)
        config_as_list = get_args_as_list_of_strings(algorithm_config)

        parser.parse_args(config_as_list)

        if parser.error_message:
            raise NotValidAlgorithmException(parser.error_message)

        self._algorithm_config = algorithm_config

    def get_environment_name(self) -> str:
        assert self.algorithm_config is not None
        key = self._get_environment_name_key()
        return self.algorithm_config[key]

    def _get_environment_name_key(self):
        assert self.algorithm is not None

        if self.algorithm in {'acer', 'acerac'}:
            key = 'env_name'
        else:
            key = 'env'
        return key
