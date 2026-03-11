from datetime import datetime
from extensions import db


class Theory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    file_path = db.Column(db.String(256), nullable=False)
    category = db.Column(db.String(64), nullable=True)
    content_hash = db.Column(db.String(32), nullable=True)   # MD5 del archivo
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (
        db.UniqueConstraint("file_path", name="uq_theory_file_path"),
    )

    def __repr__(self):
        return f"<Theory {self.title}>"