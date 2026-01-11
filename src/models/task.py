from datetime import datetime
from dateutil.parser import isoparse
from extensions import db


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)
    color = db.Column(db.String(7), default="#007bff")
    type = db.Column(db.String(20))

    # Campos para recurrencia
    recurring = db.Column(db.Boolean, default=False)
    days_of_week = db.Column(
        db.String(14), default=""
    )  # Ej: "1,3,5" para Lunes, Miércoles, Viernes
    start_recur = db.Column(db.DateTime, nullable=True)
    end_recur = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<Task {self.title}>"

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "start": self.start_date.isoformat() if self.start_date else None,
            "end": self.end_date.isoformat() if self.end_date else None,
            "color": "#28a745" if self.completed else self.color,
            "type": self.type,
            "completed": self.completed,
            "recurring": self.recurring,
            "daysOfWeek": self.days_of_week.split(",") if self.days_of_week else [],
            "startRecur": self.start_recur.isoformat() if self.start_recur else None,
            "endRecur": self.end_recur.isoformat() if self.end_recur else None,
        }

    @staticmethod
    def parse_date(date_str):
        """Parsea una fecha ISO 8601 a datetime"""
        try:
            return isoparse(date_str)
        except Exception as e:
            raise ValueError(f"Error parsing date: {date_str}. Error: {str(e)}")

    def update_dates(self, start=None, end=None):
        """Actualiza las fechas de la tarea de forma segura"""
        if start:
            self.start_date = self.parse_date(start)
        if end:
            self.end_date = self.parse_date(end) if end else None
