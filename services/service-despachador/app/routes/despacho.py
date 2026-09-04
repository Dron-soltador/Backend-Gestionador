from flask import Blueprint, request, jsonify
import requests
import os
from app.services.dispatcher import seleccionar_dron_optimo

despacho_bp = Blueprint('despacho', __name__)

DRONES_SERVICE_URL = os.getenv('DRONES_SERVICE_URL', 'http://localhost:5001')

@despacho_bp.route('/despachar', methods=['POST'])
def despachar_pedido():
    """
    Evaluar y asignar un dron óptimo para un paquete
    ---
    tags:
      - Despachador
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - peso_kg
          properties:
            pedido_id:
              type: integer
              example: 1
            peso_kg:
              type: number
              example: 3.5
            drones:
              type: array
              description: "(Opcional) Lista de drones simulada para pruebas directas"
              items:
                type: object
    responses:
      200:
        description: Dron asignado exitosamente
      400:
        description: No hay drones aptos o la solicitud es invalida
    """
    data = request.get_json() or {}
    peso_kg = data.get('peso_kg')
    pedido_id = data.get('pedido_id')
    drones_custom = data.get('drones')

    if peso_kg is None:
        return jsonify({
            "error": "Bad Request",
            "message": "El campo 'peso_kg' es obligatorio."
        }), 400

    try:
        peso_kg = float(peso_kg)
    except (ValueError, TypeError):
        return jsonify({
            "error": "Bad Request",
            "message": "'peso_kg' debe ser un número valido."
        }), 400

    # Si no se provee una lista custom de drones, se obtienen de service-drones
    if drones_custom is None:
        try:
            resp = requests.get(f"{DRONES_SERVICE_URL}/drones?estado=DISPONIBLE", timeout=5)
            if resp.status_code == 200:
                drones_lista = resp.json()
            else:
                drones_lista = []
        except requests.exceptions.RequestException:
            return jsonify({
                "error": "Service Unavailable",
                "message": "No se pudo comunicar con el microservicio de Drones."
            }), 503
    else:
        drones_lista = drones_custom

    dron_seleccionado, error_msg = seleccionar_dron_optimo(peso_kg, drones_lista)

    if error_msg or not dron_seleccionado:
        return jsonify({
            "error": "Bad Request",
            "message": error_msg
        }), 400

    return jsonify({
        "message": "Envío autorizado y dron asignado exitosamente",
        "pedido_id": pedido_id,
        "peso_kg": peso_kg,
        "dron_asignado": dron_seleccionado
    }), 200