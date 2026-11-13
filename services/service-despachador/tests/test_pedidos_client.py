from unittest.mock import patch

import requests


def test_obtener_pedidos_pendientes_exito(pedidos_client_module):
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [{"id": 1, "estado": "PENDIENTE"}]
        res, code = pedidos_client_module.obtener_pedidos_pendientes()
        assert code == 200
        assert isinstance(res, list)


def test_obtener_pedidos_pendientes_error(pedidos_client_module):
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("Error red")
        res, code = pedidos_client_module.obtener_pedidos_pendientes()
        assert code == 500
        assert "error" in res


def test_obtener_todos_los_pedidos_exito(pedidos_client_module):
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [{"id": 1}, {"id": 2}]
        res, code = pedidos_client_module.obtener_todos_los_pedidos()
        assert code == 200
        assert len(res) == 2


def test_obtener_todos_los_pedidos_error(pedidos_client_module):
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("Fallo conexion")
        res, code = pedidos_client_module.obtener_todos_los_pedidos()
        assert code == 500
        assert "error" in res


def test_obtener_detalle_pedido_404(pedidos_client_module):
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 404
        res, code = pedidos_client_module.obtener_detalle_pedido(999)
        assert res is None
        assert code == 404


def test_obtener_detalle_pedido_exito_y_campos(pedidos_client_module):
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "id": 101,
            "peso": 3.5,
            "es_urgente": True,
            "lat_origen": 10.0,
            "lon_origen": -74.0,
            "lat_destino": 10.1,
            "lon_destino": -74.1,
            "estado": "PENDIENTE"
        }
        res, code = pedidos_client_module.obtener_detalle_pedido(101)
        assert code == 200
        assert res["peso_kg"] == 3.5
        assert res["origen"]["lat"] == 10.0
        assert res["destino"]["lon"] == -74.1


def test_obtener_detalle_pedido_campos_anidados(pedidos_client_module):
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "id": 102,
            "peso_kg": 4.0,
            "es_fragil": True,
            "fecha_creacion": "2026-01-01",
            "origen": {"lat": 1.0, "lon": 2.0},
            "destino": {"lat": 3.0, "lon": 4.0},
            "estado": "PENDIENTE"
        }
        res, code = pedidos_client_module.obtener_detalle_pedido(102)
        assert code == 200
        assert res["origen"] == {"lat": 1.0, "lon": 2.0}
        assert res["fecha_creacion"] == "2026-01-01"
        assert res["es_fragil"] is True


def test_obtener_detalle_pedido_error(pedidos_client_module):
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("Error red")
        res, code = pedidos_client_module.obtener_detalle_pedido(101)
        assert code == 500
        assert "error" in res


def test_actualizar_estado_pedido_patch_exito(pedidos_client_module):
    with patch('requests.patch') as mock_patch:
        mock_patch.return_value.status_code = 200
        mock_patch.return_value.json.return_value = {"mensaje": "OK"}
        res, code = pedidos_client_module.actualizar_estado_pedido(101, "EN_CAMINO")
        assert code == 200


def test_actualizar_estado_pedido_fallback_put(pedidos_client_module):
    """Prueba la respuesta HTTP 405 para activar el fallback a PUT"""
    with patch('requests.patch') as mock_patch, patch('requests.put') as mock_put:
        mock_patch.return_value.status_code = 405
        mock_put.return_value.status_code = 200
        mock_put.return_value.json.return_value = {"mensaje": "OK via PUT"}

        res, code = pedidos_client_module.actualizar_estado_pedido(101, "EN_CAMINO")
        assert code == 200
        assert mock_put.called


def test_actualizar_estado_pedido_error(pedidos_client_module):
    with patch('requests.patch') as mock_patch:
        mock_patch.side_effect = requests.exceptions.RequestException("Error red")
        res, code = pedidos_client_module.actualizar_estado_pedido(101, "EN_CAMINO")
        assert code == 500
        assert "error" in res