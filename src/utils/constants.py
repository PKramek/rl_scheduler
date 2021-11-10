import os


class Constants:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    RL_CONFIGURATIONS = "/rl_configurations"
    KNOWN_ALGORITHMS = {'acer', 'acerac', 'PPO', 'SAC'}
    REQUIRED_CONFIG_FIELDS = {"algorithm", "algorithm_config"}
