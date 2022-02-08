from datetime import datetime, timedelta

import jwt
from flask import request, make_response, jsonify

from src import app
from src.repository import UsersRepository
from src.utils.constants import Constants


class Auth:

    @staticmethod
    def encode_auth_token(public_id: str) -> str:
        token = jwt.encode(
            {'public_id': public_id,
             'exp': datetime.utcnow() + timedelta(minutes=Constants.TOKEN_EXPIRATION_TIME_IN_MINUTES)},
            Constants.SECRET_KEY,
            algorithm="HS256")

        return token

    @staticmethod
    def decode_auth_token(token: str) -> dict:
        auth_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        return auth_data


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None

        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']

        if not token:
            return make_response(jsonify({'message': 'a valid token is missing'}), 401)

        try:
            data = Auth.decode_auth_token(token)
        except jwt.PyJWTError:
            return make_response(jsonify({'message': 'token is invalid'}), 401)

        current_user = UsersRepository.get_user_by_public_id(data['public_id'])
        if not current_user:
            return make_response(jsonify({'message': 'User not found'}), 401)

        return f(current_user, *args, **kwargs)

    return decorator
