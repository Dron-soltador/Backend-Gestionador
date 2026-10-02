import os
import requests

PEDIDOS_API_URL = os.getenv('PEDIDOS_API_URL', 'http://192.168.220.109:3001/api/v1/pedidos/para-despachador')
TIMEOUT = int(os.getenv('REMOTE_API_TIMEOUT', 5))

def obtener_pedidos_pendientes():
    """
    Ruta 1: Consultar pedidos pendientes
    GET http://192.168.220.109:3001/api/v1/pedidos/para-despachador?estado=PENDIENTE
    """
    try:
        response = requests.get(f"{PEDIDOS_API_URL}?estado=PENDIENTE", timeout=TIMEOUT)
        response.raise_for_status()
        return response.json(), 200
    except requests.exceptions.RequestException as e:
        return {"error": "Error al obtener pedidos pendientes", "details": str(e)}, 500

def obtener_todos_los_pedidos():
    """
    Ruta 2: Consultar todos los pedidos
    GET http://192.168.220.109:3001/api/v1/pedidos/para-despachador
    """
    try:
        response = requests.get(PEDIDOS_API_URL, timeout=TIMEOUT)
        response.raise_for_status()
        return response.json(), 200
    except requests.exceptions.RequestException as e:
        return {"error": "Error al obtener todos los pedidos", "details": str(e)}, 500

def obtener_detalle_pedido(pedido_id):
    """
    Ruta 3: Consultar un pedido específico
    GET http://192.168.220.109:3001/api/v1/pedidos/para-despachador/<pedido_id>
    """
    try:
        response = requests.get(f"{PEDIDOS_API_URL}/{pedido_id}", timeout=TIMEOUT)
        if response.status_code == 404:
            return None, 404
        response.raise_for_status()
        
        data = response.json()
        
        pedido_procesado = {
            "id": data.get("id", pedido_id),
            "peso_kg": data.get("peso_kg") or data.get("peso", 0.0),
            "es_urgente": data.get("es_urgente", False),
            "es_fragil": data.get("es_fragil", False),
            "fecha_creacion": data.get("fecha_creacion") or data.get("created_at"),
            "origen": data.get("origen") or {
                "lat": data.get("lat_origen"),
                "lon": data.get("lon_origen")
            },
            "destino": data.get("destino") or {
                "lat": data.get("lat_destino"),
                "lon": data.get("lon_destino")
            },
            "estado": data.get("estado")
        }
        return pedido_procesado, 200

    except requests.exceptions.RequestException as e:
        return {"error": "Fallo la comunicación con la API del compañero", "details": str(e)}, 500

def actualizar_estado_pedido(pedido_id, nuevo_estado):
    """
    Actualiza el estado de un pedido en la base de datos del compañero.
    Ruta: PATCH / PUT http://192.168.220.109:3001/api/v1/pedidos/<pedido_id>/estado
    """
    # Se extrae la URL base /api/v1/pedidos reemplazando /para-despachador
    base_url = PEDIDOS_API_URL.replace('/para-despachador', '')
    url = f"{base_url}/{pedido_id}/estado"
    payload = {"estado": nuevo_estado}

    try:
        # Intenta primero con PATCH y si el servidor exige PUT, hace fallback automático
        response = requests.patch(url, json=payload, timeout=TIMEOUT)
        if response.status_code == 405:
            response = requests.put(url, json=payload, timeout=TIMEOUT)
        response.raise_for_status()
        return response.json(), response.status_code
    except requests.exceptions.RequestException as e:
        return {"error": "Error al actualizar estado en la API de Pedidos", "details": str(e)}, 500