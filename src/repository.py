from functools import lru_cache

from sqlalchemy import desc

from src.models import Algorithm, TrainingResults, Users


class UsersRepository:
    @staticmethod
    def get_user_by_public_id(public_id: int):
        return Users.query.filter_by(public_id=public_id).first()

    @staticmethod
    def get_user_by_username(username: str):
        return Users.query.filter_by(name=username).first()


class AlgorithmRepository:
    # There are only 4 algorithms in the database, and they never change
    @staticmethod
    @lru_cache(maxsize=4)
    def get_algorithm_by_name(name: str) -> Algorithm:
        return Algorithm.query.filter(Algorithm.name == name).first()

    @staticmethod
    @lru_cache(maxsize=4)
    def get_algorithm_by_id(algorithm_id: int):
        return Algorithm.query.get(algorithm_id)


class TrainingResultsRepository:
    @staticmethod
    def get_all_results():
        return TrainingResults.query.order_by(
            desc(TrainingResults.environment),
            desc(TrainingResults.best_mean_result)
        ).all()

    @staticmethod
    def get_results_for_algorithm(algorithm_id: int):
        return TrainingResults.query.filter(TrainingResults.algorithm == algorithm_id).order_by(
            desc(TrainingResults.environment), desc(TrainingResults.best_mean_result)).all()

    @staticmethod
    def get_results_for_environment(environment: str):
        return TrainingResults.query.filter(TrainingResults.environment == environment).order_by(
            desc(TrainingResults.best_mean_result)).all()
