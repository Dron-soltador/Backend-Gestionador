from flask import Flask, jsonify, request
from flask_cors import CORS
from flasgger import Swagger

app = Flask(__name__)
CORS(app)
swagger = Swagger(app)

drones = [
    {"id": 1, "modelo": "DJI Matrice 300 RTK", "capacidad_maxima_kg": 2.7, "bateria": 85, "estado": "DISPONIBLE"},
    {"id": 2, "modelo": "Flycart 30 Heavy", "capacidad_maxima_kg": 30.0, "bateria": 100, "estado": "DISPONIBLE"},
    {"id": 3, "modelo": "Mavic 3 Enterprise", "capacidad_maxima_kg": 0.9, "bateria": 62, "estado": "DISPONIBLE"}
]

@app.route('/drones', methods=['GET'])
def get_drones():
    """Obtener lista de drones
    ---
    responses:
      200:
        description: Lista de drones devuelta
    """
    return jsonify(drones), 200

@app.route('/drones', methods=['POST'])
def create_drone():
    """Registrar un nuevo dron
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            modelo:
              type: string
            capacidad_maxima_kg:
              type: number
            bateria:
              type: integer
            estado:
              type: string
    responses:
      201:
        description: Dron registrado
    """
    data = request.get_json() or {}
    nuevo_id = max([d['id'] for d in drones], default=0) + 1
    nuevo_dron = {
        "id": nuevo_id,
        "modelo": data.get("modelo", f"Dron #{nuevo_id}"),
        "capacidad_maxima_kg": float(data.get("capacidad_maxima_kg") or 2.5),
        "bateria": int(data.get("bateria") or 100),
        "estado": (data.get("estado") or "DISPONIBLE").upper()
    }
    drones.append(nuevo_dron)
    return jsonify(nuevo_dron), 201

@app.route('/drones/<int:drone_id>/telemetria', methods=['PUT'])
def update_telemetria(drone_id):
    """Actualizar telemetria de dron
    ---
    parameters:
      - name: drone_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            bateria:
              type: integer
            estado:
              type: string
    responses:
      200:
        description: Telemetria actualizada
    """
    data = request.get_json() or {}
    for drone in drones:
        if drone['id'] == drone_id:
            if 'bateria' in data: drone['bateria'] = int(data['bateria'])
            if 'estado' in data: drone['estado'] = str(data['estado']).upper()
            return jsonify(drone), 200
    return jsonify({"error": "Dron no encontrado"}), 404

if __name__ == '__main__':
    print("Servidor corriendo. Swagger en http://localhost:5001/apidocs")
    app.run(host='0.0.0.0', port=5001, debug=True)