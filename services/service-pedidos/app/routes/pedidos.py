from flask import Blueprint, request, jsonify
from app import db
from app.models.pedido import Pedido

pedidos_bp = Blueprint('pedidos', __name__)

ESTADOS_VALIDOS = ['PENDIENTE', 'EN_CAMINO', 'ENTREGADO', 'RECHAZADO']

@pedidos_bp.route('/pedidos/usuario/<int:usuario_id>', methods=['GET'])
def get_pedidos_usuario(usuario_id):
    """
    Obtener el historial de pedidos de un usuario
    ---
    tags:
      - Pedidos
    parameters:
      - name: usuario_id
        in: path
        type: integer
        required: true
        description: ID del usuario para consultar sus pedidos
    responses:
      200:
        description: Lista de pedidos pertenecientes al usuario
    """
    pedidos = Pedido.query.filter_by(usuario_id=usuario_id).all()
    return jsonify([p.to_dict() for p in pedidos]), 200


@pedidos_bp.route('/pedidos/<int:pedido_id>/estado', methods=['PUT'])
def update_estado_pedido(pedido_id):
    """
    Actualizar el estado operativo de un pedido
    ---
    tags:
      - Pedidos
    parameters:
      - name: pedido_id
        in: path
        type: integer
        required: true
        description: ID del pedido a actualizar
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - estado
          properties:
            estado:
              type: string
              enum: [PENDIENTE, EN_CAMINO, ENTREGADO, RECHAZADO]
              example: "EN_CAMINO"
    responses:
      200:
        description: Estado del pedido actualizado exitosamente
      400:
        description: Estado invalido o faltante en la peticion
      404:
        description: Pedido no encontrado
    """
    data = request.get_json() or {}
    nuevo_estado = data.get('estado')

    if not nuevo_estado or nuevo_estado not in ESTADOS_VALIDOS:
        return jsonify({
            "error": "Bad Request",
            "message": f"Estado invalido. Los estados permitidos son: {', '.join(ESTADOS_VALIDOS)}"
        }), 400

    pedido = Pedido.query.get(pedido_id)
    if not pedido:
        return jsonify({
            "error": "Not Found",
            "message": f"No se encontro el pedido con ID {pedido_id}"
        }), 404

    pedido.estado = nuevo_estado
    db.session.commit()

    return jsonify({
        "message": "Estado del pedido actualizado exitosamente",
        "pedido": pedido.to_dict()
    }), 200