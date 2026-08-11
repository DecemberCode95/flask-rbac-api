from marshmallow import Schema, fields, validate

class CreateShipmentSchema(Schema):
    recipient_name = fields.Str(
        required=True, 
        validate=validate.Length(min=2, max=120, error="El nombre del destinatario debe tener al menos 2 caracteres")
    )
    origin_address = fields.Str(
        required=True, 
        validate=validate.Length(min=5, max=255, error="La dirección de origen debe ser detallada (mínimo 5 caracteres)")
    )
    destination_address = fields.Str(
        required=True, 
        validate=validate.Length(min=5, max=255, error="La dirección de destino debe ser detallada (mínimo 5 caracteres)")
    )

class AddTrackingEventSchema(Schema):
    location = fields.Str(
        required=True, 
        validate=validate.Length(min=2, max=255, error="La ubicación es obligatoria (ej. 'Centro de Distribución Bogotá')")
    )
    status = fields.Str(
        required=True, 
        validate=validate.OneOf(
            ["CREADO", "EN_BODEGA", "EN_TRANSITO", "EN_REPARTO", "ENTREGADO", "CANCELADO"],
            error="Estado no válido. Las opciones permitidas son: CREADO, EN_BODEGA, EN_TRANSITO, EN_REPARTO, ENTREGADO, CANCELADO"
        )
    )
    description = fields.Str(required=False)

create_shipment_schema = CreateShipmentSchema()
add_tracking_event_schema = AddTrackingEventSchema()
