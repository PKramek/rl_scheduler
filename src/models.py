from sqlalchemy import ForeignKey

from src import db


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

    def to_dict(self):
        return {
            "result_id": self.result_id,
            "best_mean_result": self.best_mean_result,
            "results_subdirectory": self.results_subdirectory,
            "environment": self.environment,
            "algorithm_config": self.algorithm_config,
            "date": self.date,
            "algorithm": Algorithm.query.get(self.algorithm).name
        }


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50))
    name = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))
    admin = db.Column(db.Boolean)
