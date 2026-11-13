import importlib

from unittest.mock import patch


def test_despachar_sin_pedido_id(client):
    response = client.post('/despachar', json={})
    assert response.status_code == 400


def test_despachar_pedido_no_encontrado(client):
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 404
        mock_get.return_value.json.return_value = {}
        response = client.post('/despachar', json={"pedido_id": 999})
        assert response.status_code == 404


def test_despachar_exito(client):
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"id": 101, "peso_kg": 2.0}
        response = client.post('/despachar', json={"pedido_id": 101})
        assert response.status_code == 200
        assert response.get_json()["pedido_id"] == 101


def test_obtener_pedidos_activos(client, listener_module):
    listener_module.pedidos_memoria = {
        101: {"id": 101, "estado": "EN_CAMINO"},
        102: {"id": 102, "estado": "ENTREGADO"}
    }
    response = client.get('/pedidos-activos')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["id"] == 101


def test_obtener_pedidos_activos_fallback(client, listener_module):
    listener_module.pedidos_memoria = {}
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [{"id": 201, "estado": "PENDIENTE"}]
        response = client.get('/pedidos-activos')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1


def test_obtener_pedidos_activos_fallback_formato_dict(client, listener_module):
    listener_module.pedidos_memoria = {}
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "data": [{"id": 202, "estado": "PENDIENTE"}]
        }
        response = client.get('/pedidos-activos')
        assert response.status_code == 200
        assert response.get_json()[0]["id"] == 202


def test_obtener_pedidos_activos_fallback_error(client, listener_module):
    listener_module.pedidos_memoria = {}
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 500
        mock_get.return_value.json.return_value = {"error": "Fallo"}
        response = client.get('/pedidos-activos')
        assert response.status_code == 200
        assert response.get_json() == []


def test_cambiar_en_camino(client, listener_module):
    listener_module.pedidos_memoria = {101: {"id": 101, "estado": "PENDIENTE"}}
    with patch('requests.patch') as mock_patch:
        mock_patch.return_value.status_code = 200
        mock_patch.return_value.json.return_value = {"mensaje": "OK"}
        response = client.put('/pedidos/101/en-camino')
        assert response.status_code == 200
        assert listener_module.pedidos_memoria[101]["estado"] == "EN_CAMINO"


def test_cambiar_en_camino_pedido_fuera_de_memoria(client, listener_module):
    listener_module.pedidos_memoria = {}
    with patch('requests.patch') as mock_patch:
        mock_patch.return_value.status_code = 200
        mock_patch.return_value.json.return_value = {"mensaje": "OK"}
        response = client.post('/pedidos/202/en-camino')
        assert response.status_code == 200
        assert listener_module.pedidos_memoria == {}


def test_entregar_pedido(client, listener_module):
    listener_module.pedidos_memoria = {101: {"id": 101, "estado": "EN_CAMINO"}}
    with patch('requests.patch') as mock_patch:
        mock_patch.return_value.status_code = 200
        mock_patch.return_value.json.return_value = {"mensaje": "OK"}
        response = client.put('/pedidos/101/entregar')
        assert response.status_code == 200
        assert listener_module.pedidos_memoria[101]["estado"] == "ENTREGADO"


def test_entregar_pedido_fuera_de_memoria(client, listener_module):
    listener_module.pedidos_memoria = {}
    with patch('requests.patch') as mock_patch:
        mock_patch.return_value.status_code = 200
        mock_patch.return_value.json.return_value = {"mensaje": "OK"}
        response = client.post('/pedidos/203/entregar')
        assert response.status_code == 200
        assert listener_module.pedidos_memoria == {}


def test_run_expone_la_aplicacion(client):
    """El punto de entrada del servicio construye la app Flask."""
    modulo_run = importlib.import_module('run')
    assert modulo_run.app is not None