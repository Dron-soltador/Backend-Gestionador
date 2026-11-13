def _crear_dron(api_client, **cambios):
    payload = {
        "modelo": "DJI Matrice 300 RTK",
        "capacidad_max_kg": 5.5,
        "bateria_porcentaje": 90,
        "estado": "DISPONIBLE"
    }
    payload.update(cambios)
    return api_client.post('/drones', json=payload)


def test_crear_dron_api_exitoso(api_client):
    response = _crear_dron(api_client)
    assert response.status_code == 201
    data = response.get_json()
    assert data["message"] == "Dron registrado exitosamente"
    assert data["drone"]["modelo"] == "DJI Matrice 300 RTK"
    assert data["drone"]["capacidad_max_kg"] == 5.5
    assert data["drone"]["bateria_porcentaje"] == 90
    assert data["drone"]["estado"] == "DISPONIBLE"


def test_crear_dron_api_valores_por_defecto(api_client):
    response = api_client.post('/drones', json={"modelo": "Mavic 3", "capacidad_max_kg": 2})
    assert response.status_code == 201
    data = response.get_json()["drone"]
    assert data["bateria_porcentaje"] == 100
    assert data["estado"] == "DISPONIBLE"
    assert isinstance(data["created_at"], str)


def test_crear_dron_api_sin_modelo(api_client):
    response = _crear_dron(api_client, modelo=None)
    assert response.status_code == 400
    assert "obligatorios" in response.get_json()["message"]


def test_crear_dron_api_sin_capacidad(api_client):
    response = _crear_dron(api_client, capacidad_max_kg=None)
    assert response.status_code == 400


def test_crear_dron_api_estado_invalido(api_client):
    response = _crear_dron(api_client, estado="VOLANDO")
    assert response.status_code == 400
    assert "Estado invalido" in response.get_json()["message"]


def test_crear_dron_api_capacidad_invalida(api_client):
    response = _crear_dron(api_client, capacidad_max_kg="mucho")
    assert response.status_code == 400


def test_crear_dron_api_bateria_invalida(api_client):
    response = _crear_dron(api_client, bateria_porcentaje="lleno")
    assert response.status_code == 400


def test_crear_dron_api_bateria_negativa(api_client):
    response = _crear_dron(api_client, bateria_porcentaje=-1)
    assert response.status_code == 400
    assert "entre 0 y 100" in response.get_json()["message"]


def test_crear_dron_api_bateria_mayor_a_cien(api_client):
    response = _crear_dron(api_client, bateria_porcentaje=101)
    assert response.status_code == 400


def test_listar_drones_api(api_client):
    assert api_client.get('/drones').get_json() == []
    _crear_dron(api_client)
    _crear_dron(api_client, modelo="Flycart 30")
    response = api_client.get('/drones')
    assert response.status_code == 200
    assert len(response.get_json()) == 2


def test_listar_drones_api_filtro_estado(api_client):
    _crear_dron(api_client)
    _crear_dron(api_client, modelo="Flycart 30", estado="EN_MISION")
    response = api_client.get('/drones?estado=EN_MISION')
    assert response.status_code == 200
    datos = response.get_json()
    assert len(datos) == 1
    assert datos[0]["modelo"] == "Flycart 30"


def test_listar_drones_api_filtro_invalido(api_client):
    response = api_client.get('/drones?estado=VOLANDO')
    assert response.status_code == 400
    assert "Estado de filtro invalido" in response.get_json()["message"]


def test_actualizar_bateria_api(api_client):
    drone_id = _crear_dron(api_client).get_json()["drone"]["id"]
    response = api_client.put(f'/drones/{drone_id}/bateria', json={"bateria_porcentaje": 42})
    assert response.status_code == 200
    data = response.get_json()
    assert data["drone"]["bateria_porcentaje"] == 42


def test_actualizar_bateria_api_dron_inexistente(api_client):
    response = api_client.put('/drones/999/bateria', json={"bateria_porcentaje": 42})
    assert response.status_code == 404


def test_actualizar_bateria_api_sin_campo(api_client):
    drone_id = _crear_dron(api_client).get_json()["drone"]["id"]
    response = api_client.put(f'/drones/{drone_id}/bateria', json={})
    assert response.status_code == 400
    assert "obligatorio" in response.get_json()["message"]


def test_actualizar_bateria_api_valor_invalido(api_client):
    drone_id = _crear_dron(api_client).get_json()["drone"]["id"]
    response = api_client.put(f'/drones/{drone_id}/bateria', json={"bateria_porcentaje": "media"})
    assert response.status_code == 400


def test_actualizar_bateria_api_fuera_de_rango(api_client):
    drone_id = _crear_dron(api_client).get_json()["drone"]["id"]
    response = api_client.put(f'/drones/{drone_id}/bateria', json={"bateria_porcentaje": 150})
    assert response.status_code == 400
    assert "estrictamente entre 0 y 100" in response.get_json()["message"]


def test_actualizar_estado_api(api_client):
    drone_id = _crear_dron(api_client).get_json()["drone"]["id"]
    response = api_client.put(f'/drones/{drone_id}/estado', json={"estado": "EN_MISION"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["drone"]["estado"] == "EN_MISION"


def test_actualizar_estado_api_dron_inexistente(api_client):
    response = api_client.put('/drones/999/estado', json={"estado": "EN_MISION"})
    assert response.status_code == 404


def test_actualizar_estado_api_sin_campo(api_client):
    drone_id = _crear_dron(api_client).get_json()["drone"]["id"]
    response = api_client.put(f'/drones/{drone_id}/estado', json={})
    assert response.status_code == 400
    assert "obligatorio" in response.get_json()["message"]


def test_actualizar_estado_api_invalido(api_client):
    drone_id = _crear_dron(api_client).get_json()["drone"]["id"]
    response = api_client.put(f'/drones/{drone_id}/estado', json={"estado": "VOLANDO"})
    assert response.status_code == 400
    assert "Estado invalido" in response.get_json()["message"]