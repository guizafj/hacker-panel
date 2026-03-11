from extensions import db
from datetime import datetime


# Nota: el nombre "Objective" es un typo histórico (debería ser "Objective" o "Objetivo").
# Se mantiene para no romper la migración y la base de datos existente.
# Si se quiere renombrar en el futuro, hay que generar una nueva migración con Alembic.
class Objective(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    objective = db.Column(db.String(128), nullable=False)
    methodology = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    date_target = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(64), default="Pendiente")
    color = db.Column(db.String(7), default="#007bff")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Objective {self.objective}>"

    def to_dict(self):
        return {
            "id": self.id,
            "objective": self.objective,
            "methodology": self.methodology,
            "description": self.description,
            # FIX: date_target era un objeto datetime crudo, jsonify fallaba.
            # Ahora se serializa a string ISO 8601 igual que en task.py.
            "date_target": self.date_target.isoformat() if self.date_target else None,
            "status": self.status,
            "color": self.color,
        }
