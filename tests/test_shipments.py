from app.extensions import db
from app.models.user import User
from app.models.role import Role

def test_create_and_track_shipment(client, app):
    # Registrar usuario y hacer login
    client.post('/api/auth/register', json={
        'username': 'remitente_test',
        'email': 'remitente@test.com',
        'password': 'password123'
    })
    login_res = client.post('/api/auth/login', json={
        'username': 'remitente_test',
        'password': 'password123'
    })
    token = login_res.get_json()['token']

    # Crear envío
    res = client.post('/api/shipments/', json={
        'recipient_name': 'Destinatario Prueba',
        'origin_address': 'Calle 10 # 5-20',
        'destination_address': 'Carrera 15 # 40-50'
    }, headers={'Authorization': f'Bearer {token}'})

    assert res.status_code == 201
    shipment_data = res.get_json()['shipment']
    tracking_number = shipment_data['tracking_number']
    assert tracking_number.startswith('TRK-')

    # Rastrear envío de forma pública
    track_res = client.get(f'/api/shipments/{tracking_number}')
    assert track_res.status_code == 200
    assert track_res.get_json()['shipment']['status'] == 'CREADO'


def test_driver_event_update(client, app):
    # Crear rol DRIVER y usuario repartidor
    with app.app_context():
        driver_role = Role(name='DRIVER', description='Repartidor')
        db.session.add(driver_role)
        driver = User(username='chofer1', email='chofer1@test.com')
        driver.set_password('password123')
        driver.roles.append(driver_role)
        db.session.add(driver)
        db.session.commit()

    # Login repartidor
    driver_login = client.post('/api/auth/login', json={
        'username': 'chofer1',
        'password': 'password123'
    })
    driver_token = driver_login.get_json()['token']

    # Crear envío con usuario normal
    client.post('/api/auth/register', json={'username': 'user2', 'email': 'user2@test.com', 'password': 'password123'})
    u_token = client.post('/api/auth/login', json={'username': 'user2', 'password': 'password123'}).get_json()['token']
    ship_res = client.post('/api/shipments/', json={
        'recipient_name': 'Ana Perez',
        'origin_address': 'Av Principal 123',
        'destination_address': 'Av Secundaria 456'
    }, headers={'Authorization': f'Bearer {u_token}'})
    trk = ship_res.get_json()['shipment']['tracking_number']

    # Repartidor actualiza ubicación
    event_res = client.post(f'/api/shipments/{trk}/events', json={
        'location': 'Bodega Central',
        'status': 'EN_TRANSITO',
        'description': 'Paquete cargado al camión'
    }, headers={'Authorization': f'Bearer {driver_token}'})

    assert event_res.status_code == 201
    assert event_res.get_json()['shipment']['status'] == 'EN_TRANSITO'
