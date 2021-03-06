import os


class Constants:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    RL_CONFIGURATIONS = "/rl_configurations"
    RL_CONFIGURATIONS_FAILED_SUBDIRECTORY = 'error'
    RL_CONFIGURATIONS_DONE_SUBDIRECTORY = 'done'
    RL_CONFIGURATIONS_PROCESSING_SUBDIRECTORY = 'processing'
    KNOWN_ALGORITHMS = {'acer', 'acerac', 'fastacer', 'fastacerax', 'PPO', 'SAC'}
    REQUIRED_CONFIG_FIELDS = {"algorithm", "algorithm_config"}
    TOKEN_EXPIRATION_TIME_IN_MINUTES = 30
