import json
import os
import uuid
from functools import wraps

import jwt
from flask import Flask, request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash

from model import db
from model.users import Users
from utils.auth_util import Auth
from utils.utils import required_fields, get_configuration_file_name

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("SQLALCHEMY_DATABASE_URI")

app.logger.info(f"SECRET_KEY: {app.config['SECRET_KEY']}")
app.logger.info(f"SQLALCHEMY_DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None

        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']

        if not token:
            return jsonify({'message': 'a valid token is missing'})

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            print(f"public_id={data['public_id']}")
            current_user = Users.query.filter_by(public_id=data['public_id']).first()
            print(current_user)
        except Exception as e:
            print(e)
            return jsonify({'message': 'token is invalid'})

        return f(current_user, *args, **kwargs)

    return decorator


@app.route('/register', methods=['POST'])
def signup_user():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')

    uuid_test = uuid.uuid4()
    print(f"{str(uuid_test)}: lengths = {len(str(uuid_test))}")
    print(f"{str(hashed_password)}: lengths = {len(str(hashed_password))}")

    new_user = Users(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, admin=True)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'registered successfully'})


@app.route('/login', methods=['POST', 'GET'])
def login_user():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})

    user = Users.query.filter_by(name=auth.username).first()

    if check_password_hash(user.password, auth.password):
        token = Auth.encode_auth_token(user.public_id)
        return jsonify({'token': token})

    return make_response('Login required', 401, {'Message': "Login required"})


@app.route('/schedule_training', methods=['POST'])
@token_required
def schedule_training(current_user):
    data = request.get_json()

    is_data_correct, response_message = required_fields(data)

    if not is_data_correct:
        return make_response(
            'Data incomplete', 418,
            {'Message': response_message}
        )

    configurations_dir = os.environ.get('FLASK_CONFIGURATIONS_DIRECTORY')
    app.logger.info(f"configurations_dir: {configurations_dir}")
    filename = get_configuration_file_name(data)
    path = f"{configurations_dir}/{filename}.json"

    with open(path, 'w') as f:
        json.dump(data, f)

    return jsonify({'message': 'Configuration scheduled for training'})


@app.route('/schedule_trainings', methods=['GET'])
@token_required
def get_all_not_run_configurations(current_user):
    configurations_dir = os.environ.get('FLASK_CONFIGURATIONS_DIRECTORY')
    app.logger.info(f"configurations_dir: {configurations_dir}")
    files = os.listdir(configurations_dir)

    return jsonify({"scheduled trainings": files})


if __name__ == '__main__':
    app.run(debug=True)
