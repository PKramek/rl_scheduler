import os


class Constants:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    FLASK_CONFIGURATIONS_DIRECTORY = os.environ.get("FLASK_CONFIGURATIONS_DIRECTORY")
    KNOWN_ALGORITHMS = {'acer', 'acerac'}
    REQUIRED_CONFIG_FIELDS = {"algorithm", "algorithm_config"}
