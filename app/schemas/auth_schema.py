from marshmallow import Schema, fields, validate
	

class RegisterSchema(Schema):
    username = fields.Str(
        required=True, 
        validate=validate.Length(min=3, max=80, error="El nombre de usuario debe tener entre 3 y 80 caracteres")
    )
    email = fields.Email(
        required=True, 
        error_messages={"invalid": "Debe proporcionar un correo electrónico válido"}
    )
    password = fields.Str(
        required=True, 
        validate=validate.Length(min=6, error="La contraseña debe tener al menos 6 caracteres")
    )

class LoginSchema(Schema):
    username = fields.Str(required=True, error_messages={"required": "El usuario es obligatorio"})
    password = fields.Str(required=True, error_messages={"required": "La contraseña es obligatoria"})

register_schema = RegisterSchema()
login_schema = LoginSchema()
