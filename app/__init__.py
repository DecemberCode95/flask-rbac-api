import logging
from flask import Flask, jsonify, request
from flasgger import Swagger
from app.config import Config
from app.extensions import db, limiter

def configure_logging(app):
    """Configuración del sistema de registros (Logs)"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s'
    )
    
    @app.after_request
    def log_request_info(response):
        app.logger.info(f"{request.remote_addr} - {request.method} {request.path} -> {response.status_code}")
        return response

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    configure_logging(app)

    # Configuración de Swagger UI
    app.config['SWAGGER'] = {
        'title': 'API de Autenticación, RBAC y Logística',
        'uiversion': 3,
        'description': 'Documentación interactiva de la API para gestión de usuarios, roles y rastreo de envíos'
    }
    Swagger(app)

    db.init_app(app)
    limiter.init_app(app)

    # Ruta raíz para comprobación de estado de Render (Healthcheck)
    @app.route('/')
    def index():
        return jsonify({
            'status': 'online',
            'message': 'API de Autenticación, RBAC y Logística activa',
            'documentation': '/apidocs'
        }), 200

    # --- MANEJADORES DE ERRORES CENTRALIZADOS ---

    @app.errorhandler(400)
    def bad_request_error(e):
        return jsonify({'error': 'Bad Request', 'message': str(e.description)}), 400

    @app.errorhandler(401)
    def unauthorized_error(e):
        return jsonify({'error': 'Unauthorized', 'message': 'No autorizado o token no válido'}), 401

    @app.errorhandler(403)
    def forbidden_error(e):
        return jsonify({'error': 'Forbidden', 'message': 'Acceso denegado: permisos insuficientes'}), 403

    @app.errorhandler(404)
    def not_found_error(e):
        return jsonify({'error': 'Not Found', 'message': 'El recurso solicitado no fue encontrado'}), 404

    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({'error': 'Too Many Requests', 'message': 'Límite de peticiones excedido. Por favor intente más tarde.'}), 429

    @app.errorhandler(500)
    def internal_server_error(e):
        app.logger.error(f"Error interno del servidor: {e}")
        return jsonify({'error': 'Internal Server Error', 'message': 'Ocurrió un error interno en el servidor.'}), 500

    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        app.logger.error(f"Excepción no controlada: {e}", exc_info=True)
        return jsonify({'error': 'Internal Server Error', 'message': 'Ocurrió un error inesperado.'}), 500

    from app.routes.auth import auth_bp
    from app.routes.users import users_bp
    from app.routes.shipments import shipments_bp
    from app.routes.analytics import analytics_bp
    
    app.register_blueprint(analytics_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(shipments_bp)

    with app.app_context():
        db.create_all()

    return app
