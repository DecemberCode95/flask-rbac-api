from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.user import User
from app.models.role import Role
from app.utils.jwt_helper import generate_token

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"message": "Username, email y password son requeridos"}), 400

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
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Username y password son requeridos"}), 400

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return jsonify({"message": "Credenciales inválidas"}), 401

    if not user.is_active:
        return jsonify({"message": "Cuenta de usuario inactiva"}), 401

    roles = [role.name for role in user.roles]
    token = generate_token(user.id, roles)

    return jsonify({"token": token, "user": user.to_dict()}), 200
