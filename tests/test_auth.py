def test_register_user(client):
    response = client.post(
        "/api/auth/register",
        json={
            "username": "juan_perez",
            "email": "juan@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["user"]["username"] == "juan_perez"
    assert "USER" in data["user"]["roles"]


def test_login_user(client):
    client.post(
        "/api/auth/register",
        json={
            "username": "maria_gomez",
            "email": "maria@example.com",
            "password": "password123",
        },
    )

    response = client.post(
        "/api/auth/login", json={"username": "maria_gomez", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "token" in data
    assert data["user"]["username"] == "maria_gomez"
