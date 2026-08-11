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

        parts = auth_header.split(" ")
        if len(parts) < 2:
            return jsonify({"message": "Formato de token inválido"}), 401

        token = parts

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


EOF

# 2. Corregir auth.py
cat << "EOF" > app / routes / auth.py
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.extensions import db, limiter
from app.models.user import User
from app.models.role import Role
from app.schemas.auth_schema import register_schema, login_schema
from app.utils.jwt_helper import generate_token
from app.utils.auth_decorators import token_required
from app.utils.redis_helper import blacklist_token

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
@limiter.limit("5 per minute")
def register():
    json_data = request.get_json() or {}
    try:
        data = register_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"message": "Error de validación", "errors": err.messages}), 400

    username = data["username"]
    email = data["email"]
    password = data["password"]

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify(
            {"message": "Nombre de usuario o correo electrónico ya registrado"}
        ), 400

    user_role = Role.query.filter_by(name="USER").first()
    if not user_role:
        user_role = Role(name="USER", description="Standard User")
        db.session.add(user_role)
        db.session.commit()

    new_user = User(username=username, email=email)
    new_user.set_password(password)
    new_user.roles.append(user_role)

    db.session.add(new_user)
    db.session.commit()

    return jsonify(
        {"message": "Usuario registrado con éxito", "user": new_user.to_dict()}
    ), 201


@auth_bp.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    json_data = request.get_json() or {}
    try:
        data = login_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"message": "Error de validación", "errors": err.messages}), 400

    username = data["username"]
    password = data["password"]

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return jsonify({"message": "Credenciales inválidas"}), 401

    if not user.is_active:
        return jsonify({"message": "Cuenta de usuario inactiva"}), 401

    roles = [role.name for role in user.roles]
    token = generate_token(user.id, roles)

    return jsonify({"token": token, "user": user.to_dict()}), 200


@auth_bp.route("/logout", methods=["POST"])
@token_required
def logout(current_user):
    auth_header = request.headers.get("Authorization")
    if auth_header:
        parts = auth_header.split(" ")
        if len(parts) >= 2:
            token = parts
            blacklist_token(token)
    return jsonify({"message": "Sesión cerrada exitosamente"}), 200


EOF
