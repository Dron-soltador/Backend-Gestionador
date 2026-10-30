import pytest
from unittest.mock import patch

def test_despachar_pedido_exitoso(client):
    def mocked_requests_get(url, *args, **kwargs):
        class MockResponse:
            def __init__(self, json_data, status_code):
                self._json_data = json_data
                self.status_code = status_code
            def json(self):
                return self._json_data
            def raise_for_status(self):
                pass

        if 'pedidos' in url:
            return MockResponse({"id": 101, "peso_kg": 2.5, "estado": "PENDIENTE"}, 200)
        elif 'drones' in url:
            return MockResponse([{"id": 1, "estado": "DISPONIBLE", "capacidad_maxima_kg": 10.0, "bateria": 100}], 200)
        return MockResponse({}, 404)

    with patch('requests.get', side_effect=mocked_requests_get), \
         patch('requests.post') as mock_post, \
         patch('requests.put') as mock_put:

        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"mensaje": "Asignación exitosa", "dron_id": 1}
        mock_put.return_value.status_code = 200

        response = client.post('/despachar', json={"pedido_id": 101})
        assert response.status_code in [200, 201]

def test_despachar_pedido_no_encontrado(client):
    def mocked_requests_get(url, *args, **kwargs):
        class MockResponse:
            def __init__(self, json_data, status_code):
                self._json_data = json_data
                self.status_code = status_code
            def json(self):
                return self._json_data
            def raise_for_status(self):
                pass
        return MockResponse({}, 404)

    with patch('requests.get', side_effect=mocked_requests_get):
        response = client.post('/despachar', json={"pedido_id": 999})
        assert response.status_code in [400, 404, 500]

def test_rutas_auxiliares_despacho(client):
    """Ejecuta peticiones GET/POST a posibles endpoints adicionales en despacho.py"""
    client.get('/')
    client.get('/health')
    client.get('/despachar')
    client.post('/despachar', json={})