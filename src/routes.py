from flask import request, make_response, jsonify
from werkzeug.security import check_password_hash

from src import app, Constants
from src.configuration_file_gateway import ConfigurationFileGatewayFactory
from src.exceptions import NotAllRequiredConfigurationFields, UnknownAlgorithmException, \
    NotValidAlgorithmConfigException
from src.models import ConfigurationFileFactory
from src.repository import AlgorithmRepository, TrainingResultsRepository, UsersRepository, ConfigurationFileRepository
from src.utils.authorization import Auth, token_required
from src.utils.data_validators import ParserFactory


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
def get_all_not_processed_configuration_files(current_user):
    configuration_file_gateway = ConfigurationFileGatewayFactory.get_default_gateway()
    parser_factory = ParserFactory()

    scheduled_conf_files = ConfigurationFileRepository.get_all_unprocessed_configuration_files(
        configuration_file_gateway,
        parser_factory
    )

    results = [result.to_dict() for result in scheduled_conf_files]
    return make_response(jsonify({
        "Number of scheduled configuration files ": len(results),
        "Scheduled configuration files ": results
    }), 200)


@app.route('/failed', methods=['GET'])
@token_required
def get_all_failed_runs(current_user):
    configuration_file_gateway = ConfigurationFileGatewayFactory.get_default_gateway()
    parser_factory = ParserFactory()

    scheduled_conf_files = ConfigurationFileRepository.get_all_failed_configuration_files(
        configuration_file_gateway,
        parser_factory
    )

    results = [result.to_dict() for result in scheduled_conf_files]
    return make_response(jsonify({
        "Number of failed configuration files ": len(results),
        "Failed files ": results
    }), 200)


@app.route('/done', methods=['GET'])
@token_required
def get_all_done_runs(current_user):
    configuration_file_gateway = ConfigurationFileGatewayFactory.get_default_gateway()
    parser_factory = ParserFactory()

    scheduled_conf_files = ConfigurationFileRepository.get_all_done_configuration_files(
        configuration_file_gateway,
        parser_factory
    )

    results = [result.to_dict() for result in scheduled_conf_files]
    return make_response(jsonify({
        "Number of processed configuration files ": len(results),
        "Processed files ": results
    }), 200)


@app.route('/processing', methods=['GET'])
@token_required
def get_all_processing_runs(current_user):
    configuration_file_gateway = ConfigurationFileGatewayFactory.get_default_gateway()
    parser_factory = ParserFactory()

    scheduled_conf_files = ConfigurationFileRepository.get_all_processing_configuration_files(
        configuration_file_gateway,
        parser_factory
    )

    results = [result.to_dict() for result in scheduled_conf_files]
    return make_response(jsonify({
        "Number of currently processed configuration files ": len(results),
        "Processing files ": results
    }), 200)


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
