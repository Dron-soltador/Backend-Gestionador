from flask import Flask
from flasgger import Swagger
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config['SWAGGER'] = {
        'title': 'API Microservicio Despachador',
        'uiversion': 3
    }
    Swagger(app)

    from app.routes.despacho import despacho_bp
    app.register_blueprint(despacho_bp)

    return app