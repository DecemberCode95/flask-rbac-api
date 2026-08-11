from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.extensions import db
from app.models.shipment import Shipment
from app.models.tracking_event import TrackingEvent
from app.schemas.shipment_schema import create_shipment_schema, add_tracking_event_schema
from app.utils.auth_decorators import token_required, roles_required

shipments_bp = Blueprint('shipments', __name__, url_prefix='/api/shipments')

@shipments_bp.route('/', methods=['POST'])
@token_required
def create_shipment(current_user):
    """
    Crear un nuevo envío de paquete
    ---
    tags:
      - Envíos y Logística
    security:
      - BearerAuth: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - recipient_name
            - origin_address
            - destination_address
          properties:
            recipient_name:
              type: string
              example: Carlos Mendoza
            origin_address:
              type: string
              example: Calle 100 # 15-20, Bogotá
            destination_address:
              type: string
              example: Carrera 43A # 1-50, Medellín
    responses:
      201:
        description: Envío creado con número de seguimiento asignado
      400:
        description: Datos de entrada inválidos
      401:
        description: Token de autenticación faltante o inválido
    """
    json_data = request.get_json() or {}
    try:
        data = create_shipment_schema.load(json_data)
    except ValidationError as err:
        return jsonify({'message': 'Error de validación', 'errors': err.messages}), 400

    new_shipment = Shipment(
        sender_id=current_user.id,
        recipient_name=data['recipient_name'],
        origin_address=data['origin_address'],
        destination_address=data['destination_address'],
        status='CREADO'
    )
    db.session.add(new_shipment)
    db.session.flush()

    initial_event = TrackingEvent(
        shipment_id=new_shipment.id,
        location=data['origin_address'],
        status='CREADO',
        description='Envío registrado exitosamente en el sistema'
    )
    db.session.add(initial_event)
    db.session.commit()

    return jsonify({
        'message': 'Envío registrado con éxito',
        'shipment': new_shipment.to_dict()
    }), 201


@shipments_bp.route('/', methods=['GET'])
@token_required
def list_shipments(current_user):
    """
    Listar envíos registrados (Mis envíos o todos si es ADMIN)
    ---
    tags:
      - Envíos y Logística
    security:
      - BearerAuth: []
    responses:
      200:
        description: Lista de envíos
      401:
        description: Token de autenticación faltante o inválido
    """
    if current_user.has_role('ADMIN'):
        shipments = Shipment.query.order_by(Shipment.created_at.desc()).all()
    else:
        shipments = Shipment.query.filter_by(sender_id=current_user.id).order_by(Shipment.created_at.desc()).all()

    return jsonify({'shipments': [s.to_dict() for s in shipments]}), 200


@shipments_bp.route('/<string:tracking_number>', methods=['GET'])
def get_tracking(tracking_number):
    """
    Rastrear un envío por su código público de seguimiento
    ---
    tags:
      - Envíos y Logística
    parameters:
      - in: path
        name: tracking_number
        type: string
        required: true
        example: TRK-8X9A21B4
    responses:
      200:
        description: Detalles del envío e historial completo de rastreo
      404:
        description: Código de seguimiento no encontrado
    """
    shipment = Shipment.query.filter_by(tracking_number=tracking_number.upper()).first()
    if not shipment:
        return jsonify({'message': 'Código de seguimiento no encontrado'}), 404

    return jsonify({'shipment': shipment.to_dict()}), 200


@shipments_bp.route('/<string:tracking_number>/events', methods=['POST'])
@token_required
@roles_required('DRIVER', 'ADMIN')
def add_tracking_event(current_user, tracking_number):
    """
    Registrar evento de actualización de ubicación y estado (Solo Repartidores o Admins)
    ---
    tags:
      - Envíos y Logística
    security:
      - BearerAuth: []
    parameters:
      - in: path
        name: tracking_number
        type: string
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - location
            - status
          properties:
            location:
              type: string
              example: Centro Logístico Medellín - Terminal Norte
            status:
              type: string
              example: EN_REPARTO
            description:
              type: string
              example: Paquete asignado al vehículo de reparto #12
    responses:
      201:
        description: Evento de rastreo agregado y estado actualizado
      403:
        description: Acceso denegado (Requiere rol DRIVER o ADMIN)
      404:
        description: Código de seguimiento no encontrado
    """
    shipment = Shipment.query.filter_by(tracking_number=tracking_number.upper()).first()
    if not shipment:
        return jsonify({'message': 'Código de seguimiento no encontrado'}), 404

    json_data = request.get_json() or {}
    try:
        data = add_tracking_event_schema.load(json_data)
    except ValidationError as err:
        return jsonify({'message': 'Error de validación', 'errors': err.messages}), 400

    new_event = TrackingEvent(
        shipment_id=shipment.id,
        location=data['location'],
        status=data['status'],
        description=data.get('description', '')
    )

    shipment.status = data['status']

    db.session.add(new_event)
    db.session.commit()

    return jsonify({
        'message': 'Actualización de rastreo registrada con éxito',
        'shipment': shipment.to_dict()
    }), 201
