import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import requests

SERVICE_DIR = str(Path(__file__).resolve().parent.parent)
if SERVICE_DIR not in sys.path:
    sys.path.insert(0, SERVICE_DIR)

import app.services.listener as listener_module
from app.services.listener import (
    procesar_pedido_automatico,
    bucle_escucha,
    iniciar_listener
)

def test_procesar_pedido_automatico_exito():
    with patch('requests.get') as mock_get, patch('requests.patch') as mock_patch:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "id": 101,
            "peso_kg": 2.5,
            "es_urgente": True,
            "estado": "PENDIENTE"
        }
        mock_patch.return_value.status_code = 200
        mock_patch.return_value.json.return_value = {"mensaje": "OK"}

        procesar_pedido_automatico(101)
        assert mock_get.called
        assert mock_patch.called

def test_procesar_pedido_automatico_error_actualizar():
    with patch('requests.get') as mock_get, patch('requests.patch') as mock_patch:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"id": 102, "peso_kg": 1.0}
        mock_patch.return_value.status_code = 500
        mock_patch.return_value.json.return_value = {"error": "Fallo"}

        procesar_pedido_automatico(102)
        assert mock_get.called

def test_procesar_pedido_automatico_sin_pedido():
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 404
        procesar_pedido_automatico(999)
        assert mock_get.called

def test_bucle_escucha_iteracion_y_excepcion():
    listener_module.pedidos_procesados.clear()
    
    mock_ok = MagicMock()
    mock_ok.status_code = 200
    mock_ok.json.return_value = [{"id": 201}]

    with patch('requests.get') as mock_get, \
         patch('requests.patch') as mock_patch, \
         patch('time.sleep', side_effect=[None, KeyboardInterrupt]):
        
        mock_get.side_effect = [
            mock_ok,
            requests.exceptions.RequestException("Error de conexion en loop")
        ]
        mock_patch.return_value.status_code = 200
        mock_patch.return_value.json.return_value = {"mensaje": "OK"}

        with pytest.raises(KeyboardInterrupt):
            bucle_escucha(0.01)

        assert 201 in listener_module.pedidos_procesados

def test_bucle_escucha_formato_dict():
    listener_module.pedidos_procesados.clear()
    
    with patch('requests.get') as mock_get, \
         patch('requests.patch') as mock_patch, \
         patch('time.sleep', side_effect=[KeyboardInterrupt]):
        
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"data": [{"id": 301}]}
        mock_patch.return_value.status_code = 200
        mock_patch.return_value.json.return_value = {"mensaje": "OK"}

        with pytest.raises(KeyboardInterrupt):
            bucle_escucha(0.01)

        assert 301 in listener_module.pedidos_procesados

def test_iniciar_listener():
    with patch('threading.Thread') as mock_thread:
        iniciar_listener()
        assert mock_thread.called