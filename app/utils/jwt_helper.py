import jwt
from datetime import datetime, timezone, timedelta
from flask import current_app


def generate_token(user_id: int, roles: list) -> str:
    payload = {
        "sub": user_id,
        "roles": roles,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc)
        + current_app.config["JWT_ACCESS_TOKEN_EXPIRES"],
    }
    return jwt.encode(payload, current_app.config["JWT_SECRET_KEY"], algorithm="HS256")


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token, current_app.config["JWT_SECRET_KEY"], algorithms=["HS256"]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return {"error": "El token ha expirado"}
    except jwt.InvalidTokenError:
        return {"error": "Token inválido"}
