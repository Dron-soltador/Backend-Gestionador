from app import db
from datetime import datetime

class Drone(db.Model):
    __tablename__ = 'drones'

    id = db.Column(db.Integer, primary_key=True)
    modelo = db.Column(db.String(100), nullable=False)
    capacidad_max_kg = db.Column(db.Float, nullable=False)
    bateria_porcentaje = db.Column(db.Integer, nullable=False, default=100)
    estado = db.Column(db.String(20), nullable=False, default='DISPONIBLE')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "modelo": self.modelo,
            "capacidad_max_kg": self.capacidad_max_kg,
            "bateria_porcentaje": self.bateria_porcentaje,
            "estado": self.estado,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }