from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from src.constants import Constants

app = Flask(__name__)

app.config['SECRET_KEY'] = Constants.SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = Constants.SQLALCHEMY_DATABASE_URI

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from src import routes
