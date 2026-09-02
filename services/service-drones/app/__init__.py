from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_user = os.getenv('POSTGRES_USER', 'admin_user')
    db_pass = os.getenv('POSTGRES_PASSWORD', 'admin_password')
    db_name = os.getenv('DB_DRONES_NAME', 'drones_db')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['SWAGGER'] = {
        'title': 'API de Gestion - Servicio Drones',
        'uiversion': 3
    }
    Swagger(app)

    db.init_app(app)

    from app.routes.drones import drones_bp
    app.register_blueprint(drones_bp)

    with app.app_context():
        from app.models.drone import Drone
        db.create_all()

    return app