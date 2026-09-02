from flask import Blueprint, request, jsonify
from app import db
from app.models.drone import Drone

drones_bp = Blueprint('drones', __name__)

ESTADOS_VALIDOS = ['DISPONIBLE', 'EN_MISION', 'CARGANDO']

@drones_bp.route('/drones', methods=['POST'])
def create_drone():
    """
    Registrar una nueva unidad de dron en la flota
    ---
    tags:
      - Drones
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - modelo
            - capacidad_max_kg
          properties:
            modelo:
              type: string
              example: "DJI Matrice 300 RTK"
            capacidad_max_kg:
              type: number
              example: 5.5
            bateria_porcentaje:
              type: integer
              example: 100
            estado:
              type: string
              enum: [DISPONIBLE, EN_MISION, CARGANDO]
              example: "DISPONIBLE"
    responses:
      201:
        description: Dron registrado exitosamente
      400:
        description: Datos requeridos faltantes o invalidos
    """
    data = request.get_json() or {}
    modelo = data.get('modelo')
    capacidad_max_kg = data.get('capacidad_max_kg')
    bateria_porcentaje = data.get('bateria_porcentaje', 100)
    estado = data.get('estado', 'DISPONIBLE')

    if not modelo or capacidad_max_kg is None:
        return jsonify({
            "error": "Bad Request",
            "message": "Los campos 'modelo' y 'capacidad_max_kg' son obligatorios."
        }), 400

    if estado not in ESTADOS_VALIDOS:
        return jsonify({
            "error": "Bad Request",
            "message": f"Estado invalido. Los estados permitidos son: {', '.join(ESTADOS_VALIDOS)}"
        }), 400

    try:
        capacidad_max_kg = float(capacidad_max_kg)
        bateria_porcentaje = int(bateria_porcentaje)
    except ValueError:
        return jsonify({
            "error": "Bad Request",
            "message": "'capacidad_max_kg' debe ser un numero y 'bateria_porcentaje' un entero."
        }), 400

    if not (0 <= bateria_porcentaje <= 100):
        return jsonify({
            "error": "Bad Request",
            "message": "'bateria_porcentaje' debe estar entre 0 y 100."
        }), 400

    nuevo_drone = Drone(
        modelo=modelo,
        capacidad_max_kg=capacidad_max_kg,
        bateria_porcentaje=bateria_porcentaje,
        estado=estado
    )

    db.session.add(nuevo_drone)
    db.session.commit()

    return jsonify({
        "message": "Dron registrado exitosamente",
        "drone": nuevo_drone.to_dict()
    }), 201


@drones_bp.route('/drones', methods=['GET'])
def get_drones():
    """
    Consultar la lista de drones (con filtro opcional por estado)
    ---
    tags:
      - Drones
    parameters:
      - name: estado
        in: query
        type: string
        required: false
        enum: [DISPONIBLE, EN_MISION, CARGANDO]
        description: Filtrar unidades por estado operativo
    responses:
      200:
        description: Lista de drones obtenida exitosamente
      400:
        description: Estado de filtro invalido
    """
    estado_filtro = request.args.get('estado')

    if estado_filtro:
        if estado_filtro not in ESTADOS_VALIDOS:
            return jsonify({
                "error": "Bad Request",
                "message": f"Estado de filtro invalido. Permitidos: {', '.join(ESTADOS_VALIDOS)}"
            }), 400
        drones = Drone.query.filter_by(estado=estado_filtro).all()
    else:
        drones = Drone.query.all()

    return jsonify([d.to_dict() for d in drones]), 200