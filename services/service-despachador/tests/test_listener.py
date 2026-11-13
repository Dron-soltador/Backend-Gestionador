from unittest.mock import MagicMock, patch

import pytest
import requests


def test_procesar_pedido_automatico_exito(listener_module):
    listener_module.pedidos_procesados.clear()
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

        listener_module.procesar_pedido_automatico(101)
        assert mock_get.called
        assert mock_patch.called
        assert listener_module.pedidos_memoria[101]["estado"] == "EN_CAMINO"


def test_procesar_pedido_automatico_actualizacion_sin_contenido(listener_module):
    with patch('requests.get') as mock_get, patch('requests.patch') as mock_patch:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"id": 103, "peso_kg": 1.0}
        mock_patch.return_value.status_code = 204
        mock_patch.return_value.json.return_value = {}

        listener_module.procesar_pedido_automatico(103)
        assert listener_module.pedidos_memoria[103]["estado"] == "EN_CAMINO"


def test_procesar_pedido_automatico_error_actualizar(listener_module):
    listener_module.pedidos_procesados.clear()
    with patch('requests.get') as mock_get, patch('requests.patch') as mock_patch:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"id": 102, "peso_kg": 1.0}
        mock_patch.return_value.status_code = 500
        mock_patch.return_value.json.return_value = {"error": "Fallo"}

        listener_module.procesar_pedido_automatico(102)
        assert mock_get.called


def test_procesar_pedido_automatico_sin_pedido(listener_module):
    listener_module.pedidos_procesados.clear()
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 404
        listener_module.procesar_pedido_automatico(999)
        assert mock_get.called


def test_bucle_escucha_iteracion_y_excepcion(listener_module):
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
            listener_module.bucle_escucha(0.01)

        assert 201 in listener_module.pedidos_procesados


def test_bucle_escucha_formato_dict(listener_module):
    listener_module.pedidos_procesados.clear()

    with patch('requests.get') as mock_get, \
         patch('requests.patch') as mock_patch, \
         patch('time.sleep', side_effect=[KeyboardInterrupt]):

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"data": [{"id": 301}]}
        mock_patch.return_value.status_code = 200
        mock_patch.return_value.json.return_value = {"mensaje": "OK"}

        with pytest.raises(KeyboardInterrupt):
            listener_module.bucle_escucha(0.01)

        assert 301 in listener_module.pedidos_procesados


def test_bucle_escucha_ignora_pedidos_ya_procesados(listener_module):
    listener_module.pedidos_procesados.clear()
    listener_module.pedidos_procesados.add(401)

    with patch('requests.get') as mock_get, \
         patch('time.sleep', side_effect=[KeyboardInterrupt]):

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [
            {"id": 401},
            {"id": None}
        ]

        with pytest.raises(KeyboardInterrupt):
            listener_module.bucle_escucha(0.01)

        assert listener_module.pedidos_procesados == {401}


def test_iniciar_listener(listener_module):
    with patch('threading.Thread') as mock_thread:
        listener_module.iniciar_listener()
        assert mock_thread.called
        assert mock_thread.return_value.start.called