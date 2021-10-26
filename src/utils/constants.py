import os

class Constants:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
