from functools import wraps
from flask import request, jsonify
from app.utils.jwt_helper import decode_token
from app.utils.redis_helper import is_token_blacklisted
from app.models.user import User


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify(
                {
                    "message": "Se requiere un token válido en el encabezado Authorization"
                }
            ), 401

        token = auth_header.split(" ")

        # Verificar si el token está en la lista negra (sesión cerrada)
        if is_token_blacklisted(token):
            return jsonify(
                {"message": "El token ha sido revocado (sesión cerrada)"}
            ), 401

        decoded = decode_token(token)

        if "error" in decoded:
            return jsonify({"message": decoded["error"]}), 401

        current_user = User.query.get(decoded["sub"])
        if not current_user or not current_user.is_active:
            return jsonify({"message": "Usuario no encontrado o inactivo"}), 401

        return f(current_user, *args, **kwargs)

    return decorated


def roles_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated(current_user, *args, **kwargs):
            user_roles = [role.name for role in current_user.roles]
            if not any(role in allowed_roles for role in user_roles):
                return jsonify(
                    {"message": "Acceso denegado: permisos insuficientes"}
                ), 403
            return f(current_user, *args, **kwargs)

        return decorated

    return decorator
