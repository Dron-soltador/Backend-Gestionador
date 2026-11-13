from flask import Blueprint, jsonify, request
from app.services.pedidos_client import obtener_pedidos_pendientes, obtener_detalle_pedido, actualizar_estado_pedido
import app.services.listener as listener_module

despacho_bp = Blueprint('despacho', __name__)

@despacho_bp.route('/despachar', methods=['POST'])
def despachar():
    """
    Despachar un pedido asignando dron
    ---
    tags:
      - Despacho
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            pedido_id:
              type: integer
              example: 101
    responses:
      200:
        description: Despacho procesado exitosamente
      400:
        description: Falta pedido_id
      404:
        description: Pedido no encontrado
    """
    data = request.get_json() or {}
    pedido_id = data.get('pedido_id')
    if not pedido_id:
        return jsonify({"error": "Falta pedido_id"}), 400
        
    pedido, status = obtener_detalle_pedido(pedido_id)
    if status != 200 or not pedido:
        return jsonify({"error": f"Pedido #{pedido_id} no encontrado"}), 404
        
    return jsonify({"mensaje": "Procesando despacho", "pedido_id": pedido_id}), 200

@despacho_bp.route('/pedidos-activos', methods=['GET'])
def obtener_activos():
    """
    Obtener lista de pedidos activos (no entregados)
    ---
    tags:
      - Despacho
    responses:
      200:
        description: Lista de pedidos activos para el frontend
    """
    memoria = getattr(listener_module, 'pedidos_memoria', {})
    activos = [p for p in memoria.values() if p.get('estado') != 'ENTREGADO']
    
    if not activos:
        pedidos, status = obtener_pedidos_pendientes()
        if status == 200:
            lista = pedidos if isinstance(pedidos, list) else pedidos.get('data', [])
            activos = [p for p in lista if p.get('estado') != 'ENTREGADO']
            
    return jsonify(activos), 200

@despacho_bp.route('/pedidos/<int:pedido_id>/en-camino', methods=['PUT', 'POST'])
def cambiar_en_camino(pedido_id):
    """
    Actualizar estado de pedido a EN_CAMINO
    ---
    tags:
      - Despacho
    parameters:
      - name: pedido_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Pedido puesto en camino
    """
    res, status = actualizar_estado_pedido(pedido_id, 'EN_CAMINO')
    memoria = getattr(listener_module, 'pedidos_memoria', {})
    if pedido_id in memoria:
        memoria[pedido_id]['estado'] = 'EN_CAMINO'
    return jsonify({"mensaje": f"Pedido #{pedido_id} marcado como EN_CAMINO"}), 200

@despacho_bp.route('/pedidos/<int:pedido_id>/entregar', methods=['PUT', 'POST'])
def entregar_pedido(pedido_id):
    """
    Actualizar estado de pedido a ENTREGADO
    ---
    tags:
      - Despacho
    parameters:
      - name: pedido_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Pedido entregado exitosamente
    """
    res, status = actualizar_estado_pedido(pedido_id, 'ENTREGADO')
    memoria = getattr(listener_module, 'pedidos_memoria', {})
    if pedido_id in memoria:
        memoria[pedido_id]['estado'] = 'ENTREGADO'
    return jsonify({"mensaje": f"Pedido #{pedido_id} marcado como ENTREGADO"}), 200