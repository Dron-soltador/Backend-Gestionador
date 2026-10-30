import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import requests

SERVICE_DIR = str(Path(__file__).resolve().parent.parent)
if SERVICE_DIR not in sys.path:
    sys.path.insert(0, SERVICE_DIR)

from app.services.pedidos_client import (
    obtener_pedidos_pendientes,
    obtener_todos_los_pedidos,
    obtener_detalle_pedido,
    actualizar_estado_pedido
)

def test_obtener_pedidos_pendientes_exito():
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [{"id": 1, "estado": "PENDIENTE"}]
        res, code = obtener_pedidos_pendientes()
        assert code == 200
        assert isinstance(res, list)

def test_obtener_pedidos_pendientes_error():
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("Error red")
        res, code = obtener_pedidos_pendientes()
        assert code == 500
        assert "error" in res

def test_obtener_todos_los_pedidos_exito():
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [{"id": 1}, {"id": 2}]
        res, code = obtener_todos_los_pedidos()
        assert code == 200
        assert len(res) == 2

def test_obtener_todos_los_pedidos_error():
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("Fallo conexion")
        res, code = obtener_todos_los_pedidos()
        assert code == 500
        assert "error" in res

def test_obtener_detalle_pedido_404():
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 404
        res, code = obtener_detalle_pedido(999)
        assert res is None
        assert code == 404

def test_obtener_detalle_pedido_exito_y_campos():
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
        res, code = obtener_detalle_pedido(101)
        assert code == 200
        assert res["peso_kg"] == 3.5
        assert res["origen"]["lat"] == 10.0

def test_actualizar_estado_pedido_patch_exito():
    with patch('requests.patch') as mock_patch:
        mock_patch.return_value.status_code = 200
        mock_patch.return_value.json.return_value = {"mensaje": "OK"}
        res, code = actualizar_estado_pedido(101, "EN_CAMINO")
        assert code == 200

def test_actualizar_estado_pedido_fallback_put():
    """Prueba la respuesta HTTP 405 para activar el fallback a PUT"""
    with patch('requests.patch') as mock_patch, patch('requests.put') as mock_put:
        mock_patch.return_value.status_code = 405
        mock_put.return_value.status_code = 200
        mock_put.return_value.json.return_value = {"mensaje": "OK via PUT"}
        
        res, code = actualizar_estado_pedido(101, "EN_CAMINO")
        assert code == 200
        assert mock_put.called

def test_actualizar_estado_pedido_error():
    with patch('requests.patch') as mock_patch:
        mock_patch.side_effect = requests.exceptions.RequestException("Error red")
        res, code = actualizar_estado_pedido(101, "EN_CAMINO")
        assert code == 500