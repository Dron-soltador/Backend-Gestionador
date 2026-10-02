from flask import Blueprint, request, jsonify
from app.services.pedidos_client import obtener_detalle_pedido, actualizar_estado_pedido

despacho_bp = Blueprint('despacho', __name__)

@despacho_bp.route('/despachar', methods=['POST'])
def despachar():
    """
    Solicitar despacho de un pedido y actualizar su estado en Pedidos
    ---
    tags:
      - Despacho
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - pedido_id
          properties:
            pedido_id:
              type: integer
              example: 1
    responses:
      200:
        description: Pedido procesado y estado actualizado en Pedidos
      400:
        description: El campo pedido_id es obligatorio
      500:
        description: Falló la comunicación con el servicio de Pedidos
    """
    data = request.get_json() or {}
    pedido_id = data.get('pedido_id')

    if not pedido_id:
        return jsonify({"error": "Bad Request", "message": "El campo 'pedido_id' es obligatorio."}), 400

    pedido, status_code = obtener_detalle_pedido(pedido_id)
    if status_code != 200:
        return jsonify(pedido), status_code

    # Notificar cambio de estado a la BD del compañero
    actualizar_estado_pedido(pedido_id, "EN_CAMINO")

    return jsonify({
        "message": "Pedido recibido, asignado a dron y estado actualizado a EN_CAMINO.",
        "pedido_id": pedido_id,
        "caracteristicas_paquete": pedido,
        "nuevo_estado": "EN_CAMINO"
    }), 200


@despacho_bp.route('/despachar/pedidos/<int:pedido_id>/estado', methods=['PUT', 'PATCH'])
def modificar_estado_pedido(pedido_id):
    """
    Modificar manualmente el estado de un pedido en la base de datos de Pedidos
    ---
    tags:
      - Despacho (Administrador)
    parameters:
      - in: path
        name: pedido_id
        type: integer
        required: true
        description: ID del pedido a modificar
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - estado
          properties:
            estado:
              type: string
              example: "EN_CAMINO"
              description: Nuevo estado (PENDIENTE, EN_CAMINO, ENTREGADO, CANCELADO)
    responses:
      200:
        description: Estado modificado correctamente en la BD de Pedidos
      400:
        description: Se requiere el parámetro estado
      500:
        description: Error al comunicarse con la API de Pedidos
    """
    data = request.get_json() or {}
    nuevo_estado = data.get('estado')

    if not nuevo_estado:
        return jsonify({"error": "Bad Request", "message": "El campo 'estado' es obligatorio."}), 400

    respuesta, status_code = actualizar_estado_pedido(pedido_id, nuevo_estado)
    return jsonify(respuesta), status_code


@despacho_bp.route('/despachar/consultar-pedido/<int:pedido_id>', methods=['GET'])
def inspeccionar_pedido(pedido_id):
    """
    Ver características completas de un paquete desde la API de Pedidos
    ---
    tags:
      - Despacho
    parameters:
      - in: path
        name: pedido_id
        type: integer
        required: true
    responses:
      200:
        description: Retorna peso, urgencia, fragilidad, origen y destino
    """
    pedido, status_code = obtener_detalle_pedido(pedido_id)
    return jsonify(pedido), status_code