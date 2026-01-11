from extensions import db
from datetime import datetime


class Objetive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    objetive = db.Column(db.String(128), nullable=False)  # Objetivo
    methodology = db.Column(db.String(128), nullable=False)  # Metodologia usada
    description = db.Column(db.Text)  # Descripción del objetivo
    date_target = db.Column(db.DateTime, nullable=True)  # Fecha pensada para alcanzarlo
    status = db.Column(db.String(64), default="Pendiente")  # Estado del objetivo
    color = db.Column(db.String(7), default="#007bff")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Objetive {self.objetive}>"

    def to_dict(self):
        return {
            "id": self.id,
            "objetive": self.objetive,
            "methodology": self.methodology,
            "description": self.description,
            "date_target": self.date_target,
            "status": self.status,
            "color": self.color,
        }
