from flask import Blueprint, request, jsonify
from app import db
from app.models.user import User
import jwt
import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
SECRET_KEY = "tu_clave_secreta_jwt"

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Registro de nuevos usuarios (Cliente u Operador)
    ---
    tags:
      - Autenticación
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - username
            - email
            - password
          properties:
            username:
              type: string
              example: operador1
            email:
              type: string
              example: operador@drones.com
            password:
              type: string
              example: Password123
            role:
              type: string
              example: Operador
    responses:
      201:
        description: Usuario registrado exitosamente
      400:
        description: Datos faltantes o el correo ya se encuentra registrado
    """
    data = request.get_json() or {}

    if not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({
            "code": 400,
            "error": "Bad Request",
            "message": "Faltan campos obligatorios: username, email y password"
        }), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({
            "code": 400,
            "error": "Bad Request",
            "message": "El correo electrónico ya está registrado"
        }), 400

    new_user = User(
        username=data['username'],
        email=data['email'],
        role=data.get('role', 'Cliente')
    )
    new_user.set_password(data['password'])

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "Usuario registrado exitosamente",
        "user": new_user.to_dict()
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Inicio de sesión y obtención de Token JWT
    ---
    tags:
      - Autenticación
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              example: operador@drones.com
            password:
              type: string
              example: Password123
    responses:
      200:
        description: Autenticación exitosa y devolución de token JWT
      401:
        description: Credenciales inválidas
    """
    data = request.get_json() or {}

    if not data.get('email') or not data.get('password'):
        return jsonify({
            "code": 400,
            "error": "Bad Request",
            "message": "Se requiere email y password"
        }), 400

    user = User.query.filter_by(email=data['email']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({
            "code": 401,
            "error": "Unauthorized",
            "message": "Credenciales inválidas"
        }), 401

    payload = {
        "user_id": user.id,
        "email": user.email,
        "role": user.role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    return jsonify({
        "message": "Inicio de sesión exitoso",
        "token": token,
        "user": user.to_dict()
    }), 200