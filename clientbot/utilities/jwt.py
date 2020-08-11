import os
from datetime import datetime, timedelta
import jwt
import json


def jwt_encode(user_id):
    encoded = jwt.encode(
        {"id": str(user_id), "exp": datetime.utcnow() + timedelta(hours=2)},
        os.getenv("JWT_SECRET"),
        algorithm="HS256"
    )

    return encoded.decode('utf-8')


def jwt_auth(req_headers):
    if "Authorization" not in req_headers:
        return None
    token = req_headers["Authorization"][7:] # Everything after "Bearer "

    try:
        return {"success": 1, "response": jwt.decode(token, os.getenv("JWT_SECRET"), algorithms="HS256")}
    except jwt.ExpiredSignatureError:
        return {"success": 0, "error": "Signature has expired."}
    except jwt.DecodeError:
        return {"success": 0, "error": "Bad password."}
    except jwt.InvalidTokenError:
        return {"success": 0, "error": "Bad token."}

