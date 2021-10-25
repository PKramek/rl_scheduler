from datetime import datetime, timedelta

import jwt

from utils.constants import Constants


class Auth:

    @staticmethod
    def encode_auth_token(public_id: str) -> str:
        token = jwt.encode(
            {'public_id': public_id,
             'exp': datetime.utcnow() + timedelta(minutes=30)},
            Constants.SECRET_KEY,
            algorithm="HS256")

        return token
