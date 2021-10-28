import json
import jwt
import uuid
from flask import request, make_response, jsonify
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

from src import app, db, Constants
from src.models import Users
from src.utils.auth_util import Auth
from src.utils.utils import config_correct, get_configuration_file_name, get_configuration_absolute_path, \
    get_all_files_with_extension_in_directory


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None

        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']

        if not token:
            return make_response(jsonify({'message': 'a valid token is missing'}), 401)

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = Users.query.filter_by(public_id=data['public_id']).first()
        except Exception:  # TODO find right exceptions
            return make_response(jsonify({'message': 'token is invalid'}), 401)

        return f(current_user, *args, **kwargs)

    return decorator


@app.route('/register', methods=['POST'])
def signup_user():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')

    new_user = Users(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, admin=True)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'registered successfully'}, 201)


@app.route('/login', methods=['POST', 'GET'])
def login_user():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response(jsonify({'Message': "Could not verify"}), 401)

    user = Users.query.filter_by(name=auth.username).first()
    if not user:
        return make_response(jsonify({'Could not find user'}), 401)

    if check_password_hash(user.password, auth.password):
        token = Auth.encode_auth_token(user.public_id)
        return make_response(jsonify({'token': token}), 200)

    return make_response(jsonify({'Wrong password': token}), 401)


@app.route('/schedule', methods=['POST'])
@token_required
def schedule_training(current_user):
    data = request.get_json()

    is_data_correct, response_message = config_correct(data)

    if not is_data_correct:
        return make_response(
            jsonify({'Message': response_message}), 418
        )

    filename = get_configuration_file_name(data)
    path = get_configuration_absolute_path(filename)

    with open(path, 'x') as f:
        json.dump(data, f)

    return make_response(jsonify({'message': f'Configuration created: {filename}'}), 201)


@app.route('/scheduled', methods=['GET'])
@token_required
def get_all_not_run_configurations(current_user):
    configurations_dir = Constants.AIRFLOW_RL_CONFIGURATIONS
    json_files = get_all_files_with_extension_in_directory(configurations_dir, '.json')

    return make_response(jsonify({"scheduled trainings": json_files}), 200)
