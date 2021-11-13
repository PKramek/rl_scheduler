import json
from functools import wraps

import jwt
from flask import request, make_response, jsonify
from werkzeug.security import check_password_hash

from src import app, Constants
from src.models import Users
from src.repository import AlgorithmRepository, TrainingResultsRepository
from src.utils.auth_util import Auth
from src.utils.utils import get_configuration_file_name, get_configuration_absolute_path, \
    get_all_files_with_extension_in_directory, all_required_config_fields, check_algorithm_config, \
    add_utility_config_extensions, training_results_to_dict


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


@app.route('/login', methods=['POST', 'GET'])
def login_user():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response(jsonify({'Message': "Could not verify"}), 401)

    user = Users.query.filter_by(name=auth.username).first()
    if not user:
        return make_response(jsonify({"message": 'Could not find user'}), 401)

    if check_password_hash(user.password, auth.password):
        token = Auth.encode_auth_token(user.public_id)
        return make_response(jsonify({'token': token}), 200)

    return make_response(jsonify({"message": 'Wrong password'}), 401)


@app.route('/schedule', methods=['POST'])
@token_required
def schedule_training(current_user):
    data = request.get_json()

    all_required_fields, response_message = all_required_config_fields(data)
    if not all_required_fields:
        return make_response(
            jsonify({'Message': response_message}), 418
        )

    data = add_utility_config_extensions(data)

    is_data_correct, response_message = check_algorithm_config(data)

    if not is_data_correct:
        return make_response(
            jsonify({'Message': response_message}), 418
        )

    filename = get_configuration_file_name(data)
    path = get_configuration_absolute_path(filename)

    app.logger.info(f'Configuration will be saved in file: {path}')
    with open(path, 'x') as f:
        json.dump(data, f)

    return make_response(jsonify(
        {
            'message': 'Configuration created',
            'filename': filename,
            'config': data
        }, 201))


@app.route('/scheduled', methods=['GET'])
@token_required
def get_all_not_run_configurations(current_user):
    configurations_dir = Constants.RL_CONFIGURATIONS
    json_files = get_all_files_with_extension_in_directory(configurations_dir, '.json')

    return make_response(jsonify({"scheduled trainings": json_files}), 200)


@app.route('/failed', methods=['GET'])
@token_required
def get_all_failed_runs(current_user):
    configurations_dir = Constants.RL_CONFIGURATIONS
    error_directory = f"{configurations_dir}/{Constants.RL_CONFIGURATIONS_FAILED_SUBDIRECTORY}"
    json_files = get_all_files_with_extension_in_directory(error_directory, '.json')

    return make_response(jsonify({"Failed trainings": json_files}), 200)


@app.route('/done', methods=['GET'])
@token_required
def get_all_done_runs(current_user):
    configurations_dir = Constants.RL_CONFIGURATIONS
    done_directory = f"{configurations_dir}/{Constants.RL_CONFIGURATIONS_DONE_SUBDIRECTORY}"
    json_files = get_all_files_with_extension_in_directory(done_directory, '.json')

    return make_response(jsonify({"Done trainings": json_files}), 200)


@app.route('/processing', methods=['GET'])
@token_required
def get_all_processing_runs(current_user):
    configurations_dir = Constants.RL_CONFIGURATIONS
    processing_directory = f"{configurations_dir}/{Constants.RL_CONFIGURATIONS_PROCESSING_SUBDIRECTORY}"
    json_files = get_all_files_with_extension_in_directory(processing_directory, '.json')

    return make_response(jsonify({"Processing trainings": json_files}), 200)


@app.route('/results', methods=['GET'])
@token_required
def get_all_results(current_user):
    query_results = TrainingResultsRepository.get_all_results()

    results = [training_results_to_dict(result) for result in query_results]
    return make_response(jsonify({"All results": results}), 200)


@app.route('/results/environment/<environment>', methods=['GET'])
@token_required
def get_results_for_environment(current_user, environment):
    query_results = TrainingResultsRepository.get_results_for_environment(environment)

    results = [training_results_to_dict(result) for result in query_results]
    return make_response(jsonify({f"Results for {environment} environment": results}), 200)


@app.route('/results/algorithm/<algorithm>', methods=['GET'])
@token_required
def get_results_for_algorithm(current_user, algorithm):
    if algorithm not in Constants.KNOWN_ALGORITHMS:
        make_response(jsonify({"Message": f"Unknown algorithm: {algorithm}"}), 400)

    algorithm_id = AlgorithmRepository.get_algorithm_by_name(algorithm).id
    query_results = TrainingResultsRepository.get_results_for_algorithm(algorithm_id)

    results = [training_results_to_dict(result) for result in query_results]
    return make_response(jsonify({f"Results for {algorithm} algorithm": results}), 200)
