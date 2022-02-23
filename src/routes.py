import json

from flask import request, make_response, jsonify
from werkzeug.security import check_password_hash

from src import app, Constants
from src.models import ConfigurationFileFactory
from src.repository import AlgorithmRepository, TrainingResultsRepository, UsersRepository, ConfigurationFileRepository
from src.utils.authorization import Auth, token_required
from src.utils.configuration_file_gateway import ConfigurationFileGatewayFactory
from src.utils.data_validators import ParserFactory
from src.exceptions import NotAllRequiredConfigurationFields, UnknownAlgorithmException, \
    NotValidAlgorithmConfigException
from src.utils.utils import get_configuration_file_name, get_configuration_absolute_path, \
    get_all_files_with_extension_in_directory, all_required_config_fields, check_algorithm_config, \
    add_utility_config_extensions


@app.route('/login', methods=['POST', 'GET'])
def login_user():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response(jsonify({'Message': "Could not verify"}), 401)

    user = UsersRepository.get_user_by_username(auth.username)

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


@app.route('/schedule_v2', methods=['POST'])
@token_required
def schedule_training_v2(current_user):
    data = request.get_json()
    parser_factory = ParserFactory()

    error = None
    error_code = 418

    try:
        configuration_file = ConfigurationFileFactory.from_dict(data, parser_factory)
    except NotAllRequiredConfigurationFields:
        error = f"Config must have fields: {Constants.REQUIRED_CONFIG_FIELDS}"
    except UnknownAlgorithmException:
        error = f"Algorithm must be one of values: {Constants.KNOWN_ALGORITHMS}"
    except NotValidAlgorithmConfigException as e:
        error = str(e)

    if error is not None:
        return make_response(
            jsonify({'Message': error}), error_code
        )

    metadata = ConfigurationFileRepository.save(
        configuration_file,
        ConfigurationFileGatewayFactory.get_default_gateway()
    )

    return make_response(jsonify({'message': metadata}, 201))


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
    all_training_results = TrainingResultsRepository.get_all_results()

    results = [result.to_dict() for result in all_training_results]
    return make_response(jsonify({"All results": results}), 200)


@app.route('/results/environment/<environment>', methods=['GET'])
@token_required
def get_results_for_environment(current_user, environment):
    results_for_environment = TrainingResultsRepository.get_results_for_environment(environment)

    results_as_dicts = [result.to_dict() for result in results_for_environment]
    return make_response(jsonify({f"Results for {environment} environment": results_as_dicts}), 200)


@app.route('/results/algorithm/<algorithm>', methods=['GET'])
@token_required
def get_results_for_algorithm(current_user, algorithm):
    if algorithm not in Constants.KNOWN_ALGORITHMS:
        make_response(jsonify({"Message": f"Unknown algorithm: {algorithm}"}), 400)

    algorithm_id = AlgorithmRepository.get_algorithm_by_name(algorithm).id
    results_for_algorithm = TrainingResultsRepository.get_results_for_algorithm(algorithm_id)

    results = [result.to_dict() for result in results_for_algorithm]
    return make_response(jsonify({f"Results for {algorithm} algorithm": results}), 200)
