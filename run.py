import logging

from src import app

if __name__ == '__main__':
    app.logger.setLevel(logging.INFO)
    app.run(debug=False, host='0.0.0.0')
