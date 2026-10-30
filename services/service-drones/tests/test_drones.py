import pytest

def test_get_drones_exitoso(client):
    """Prueba la consulta general de drones"""
    response = client.get('/drones')
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

def test_crear_dron_exitoso(client):
    """Prueba la creación de un nuevo dron (POST /drones)"""
    payload = {
        "modelo": "DJI Matrice 350 RTK",
        "capacidad_maxima_kg": 5.5,
        "bateria": 95,
        "estado": "DISPONIBLE"
    }
    response = client.post('/drones', json=payload)
    assert response.status_code in [200, 201]
    data = response.get_json()
    assert data["modelo"] == "DJI Matrice 350 RTK"

def test_actualizar_telemetria_exitoso(client):
    """Prueba la actualización de batería y estado (PUT /drones/<id>/telemetria)"""
    payload = {
        "bateria": 80,
        "estado": "EN_MISION"
    }
    response = client.put('/drones/1/telemetria', json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["bateria"] == 80
    assert data["estado"] == "EN_MISION"

def test_actualizar_telemetria_dron_inexistente(client):
    """Prueba el caso de error 404 al actualizar un dron que no existe"""
    payload = {"bateria": 50, "estado": "DISPONIBLE"}
    response = client.put('/drones/999/telemetria', json=payload)
    assert response.status_code == 404