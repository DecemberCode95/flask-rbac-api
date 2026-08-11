from app.extensions import db
from app.models.user import User
from app.models.role import Role


def test_profile_access(client):
    client.post(
        "/api/auth/register",
        json={
            "username": "carlos_user",
            "email": "carlos@example.com",
            "password": "password123",
        },
    )
    login_res = client.post(
        "/api/auth/login", json={"username": "carlos_user", "password": "password123"}
    )
    token = login_res.get_json()["token"]

    # Sin token -> 401
    res_no_token = client.get("/api/users/profile")
    assert res_no_token.status_code == 401

    # Con token -> 200
    res_with_token = client.get(
        "/api/users/profile", headers={"Authorization": f"Bearer {token}"}
    )
    assert res_with_token.status_code == 200
    assert res_with_token.get_json()["user"]["username"] == "carlos_user"


def test_admin_role_restriction(client, app):
    client.post(
        "/api/auth/register",
        json={
            "username": "regular_user",
            "email": "regular@example.com",
            "password": "password123",
        },
    )

    with app.app_context():
        admin_role = Role.query.filter_by(name="ADMIN").first()
        admin = User(username="admin_user", email="admin@example.com")
        admin.set_password("admin123")
        admin.roles.append(admin_role)
        db.session.add(admin)
        db.session.commit()

    reg_login = client.post(
        "/api/auth/login", json={"username": "regular_user", "password": "password123"}
    )
    reg_token = reg_login.get_json()["token"]

    admin_login = client.post(
        "/api/auth/login", json={"username": "admin_user", "password": "admin123"}
    )
    admin_token = admin_login.get_json()["token"]

    # Usuario sin rol ADMIN intenta acceder a ruta protegida -> 403
    res_regular = client.get(
        "/api/users/", headers={"Authorization": f"Bearer {reg_token}"}
    )
    assert res_regular.status_code == 403

    # Usuario ADMIN accede -> 200
    res_admin = client.get(
        "/api/users/", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res_admin.status_code == 200
    assert len(res_admin.get_json()["users"]) == 2
