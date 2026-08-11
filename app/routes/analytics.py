import json
from flask import Blueprint, jsonify
from app.models.shipment import Shipment
from app.utils.auth_decorators import token_required, roles_required
from app.utils.redis_helper import redis_client

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

@analytics_bp.route('/dashboard', methods=['GET'])
@token_required
@roles_required('ADMIN')
def get_dashboard_metrics(current_user):
    """
    Obtener métricas y KPIs logísticos en tiempo real (Caché con Redis)
    ---
    tags:
      - Métricas y Analítica
    security:
      - BearerAuth: []
    responses:
      200:
        description: Resumen de métricas operativas
    """
    cache_key = "analytics:dashboard_kpis"
    
    # Intentar obtener desde caché de Redis
    if redis_client:
        try:
            cached_data = redis_client.get(cache_key)
            if cached_data:
                return jsonify({'source': 'cache_redis', 'metrics': json.loads(cached_data)}), 200
        except Exception:
            pass

    # Calcular métricas desde la base de datos
    total_shipments = Shipment.query.count()
    active_shipments = Shipment.query.filter(Shipment.status.in_(['CREADO', 'EN_BODEGA', 'EN_TRANSITO', 'EN_REPARTO'])).count()
    delivered_shipments = Shipment.query.filter_by(status='ENTREGADO').count()
    cancelled_shipments = Shipment.query.filter_by(status='CANCELADO').count()

    metrics = {
        'total_shipments': total_shipments,
        'active_shipments': active_shipments,
        'delivered_shipments': delivered_shipments,
        'cancelled_shipments': cancelled_shipments,
        'delivery_success_rate': f"{round((delivered_shipments / total_shipments * 100), 2)}%" if total_shipments > 0 else "0%"
    }

    # Guardar en Redis por 60 segundos
    if redis_client:
        try:
            redis_client.setex(cache_key, 60, json.dumps(metrics))
        except Exception:
            pass

    return jsonify({'source': 'database', 'metrics': metrics}), 200
