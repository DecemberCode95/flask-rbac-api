import pytest
from app import create_app
from app.config import TestingConfig
from app.extensions import db
from app.models.role import Role


@pytest.fixture
def app():
    app = create_app(TestingConfig)

    with app.app_context():
        db.create_all()

        admin_role = Role(name="ADMIN", description="Administrator")
        user_role = Role(name="USER", description="Standard User")
        db.session.add_all([admin_role, user_role])
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
