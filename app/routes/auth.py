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
    """
    Registro de nuevo usuario
    ---
    tags:
      - Autenticación
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - username
            - email
            - password
          properties:
            username:
              type: string
              example: juan_perez
            email:
              type: string
              example: juan@example.com
            password:
              type: string
              example: password123
    responses:
      201:
        description: Usuario creado exitosamente
      400:
        description: Datos de entrada inválidos o usuario/email ya registrado
    """
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
    """
    Inicio de sesión de usuario y emisión de JWT
    ---
    tags:
      - Autenticación
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: juan_perez
            password:
              type: string
              example: password123
    responses:
      200:
        description: Login exitoso, devuelve el token JWT
      401:
        description: Credenciales inválidas o cuenta inactiva
    """
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
    """
    Cierre de sesión y revocación del token JWT
    ---
    tags:
      - Autenticación
    responses:
      200:
        description: Sesión cerrada exitosamente y token revocado
      401:
        description: Token inválido o revocado anteriormente
    """
    auth_header = request.headers.get("Authorization")
    token = auth_header.split(" ")

    # Agregar token a la lista negra
    blacklist_token(token)

    return jsonify({"message": "Sesión cerrada exitosamente"}), 200
