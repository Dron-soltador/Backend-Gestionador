from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger
from flask_cors import CORS
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    CORS(app)

    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'postgres')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'drones_db')

    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///drones.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['SWAGGER'] = {
        'title': 'API Microservicio Drones',
        'uiversion': 3
    }
    Swagger(app)

    db.init_app(app)

    from app.routes.drones import drones_bp
    app.register_blueprint(drones_bp)

    with app.app_context():
        db.create_all()

    return app
