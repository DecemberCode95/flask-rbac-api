from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.user import User
from app.models.role import Role
from app.utils.auth_decorators import token_required, roles_required

users_bp = Blueprint("users", __name__, url_prefix="/api/users")


@users_bp.route("/profile", methods=["GET"])
@token_required
def get_profile(current_user):
    return jsonify({"user": current_user.to_dict()}), 200


@users_bp.route("/", methods=["GET"])
@token_required
@roles_required("ADMIN")
def list_users(current_user):
    users = User.query.all()
    return jsonify({"users": [user.to_dict() for user in users]}), 200


@users_bp.route("/<int:user_id>/roles", methods=["PUT"])
@token_required
@roles_required("ADMIN")
def update_user_roles(current_user, user_id):
    data = request.get_json() or {}
    role_names = data.get("roles", [])

    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({"message": "Usuario no encontrado"}), 404

    roles = Role.query.filter(Role.name.in_(role_names)).all()
    target_user.roles = roles
    db.session.commit()

    return jsonify(
        {"message": "Roles actualizados correctamente", "user": target_user.to_dict()}
    ), 200
