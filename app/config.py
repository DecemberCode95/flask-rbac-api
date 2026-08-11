import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-prod")
    JWT_SECRET_KEY = os.environ.get(
        "JWT_SECRET_KEY", "dev-jwt-secret-key-change-in-prod"
    )
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        hours=int(os.environ.get("JWT_EXPIRATION_HOURS", 1))
    )

    db_url = os.environ.get("DATABASE_URL")

    # Corrección automática para las URLs de PostgreSQL de Render (postgres:// -> postgresql://)
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    if db_url and db_url.startswith("postgresql"):
        try:
            import psycopg2

            SQLALCHEMY_DATABASE_URI = db_url
        except ImportError:
            SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(
                os.path.abspath(os.path.dirname(__file__)), "../app.db"
            )
    elif db_url:
        SQLALCHEMY_DATABASE_URI = db_url
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "../app.db"
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SECRET_KEY = "test-secret-key"
    JWT_SECRET_KEY = "test-jwt-secret-key"
