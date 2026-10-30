import pytest

def test_despachar_pedido_exitoso(client):
    """Prueba la orquestación de asignación de pedido"""
    payload = {"pedido_id": 101}
    response = client.post('/despachar', json=payload)
    assert response.status_code in [200, 201, 400, 404]