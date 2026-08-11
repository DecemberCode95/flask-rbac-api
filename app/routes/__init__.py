# Archivo de inicialización para rutas/blueprints
from flask import Flask, jsonify
from flasgger import Swagger
from app.config import Config
from app.extensions import db, limiter


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Configuración de Swagger UI
    app.config["SWAGGER"] = {
        "title": "API de Autenticación y RBAC",
        "uiversion": 3,
        "description": "Documentación interactiva de la API para gestión de usuarios y roles",
    }
    Swagger(app)

    db.init_app(app)
    limiter.init_app(app)

    # Manejador personalizado cuando se excede el límite de velocidad (Error 429)
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify(
            {
                "message": "Límite de peticiones excedido. Por favor intente más tarde.",
                "error": str(e.description),
            }
        ), 429

    from app.routes.auth import auth_bp
    from app.routes.users import users_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)

    with app.app_context():
        db.create_all()

    return app