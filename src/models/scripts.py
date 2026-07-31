from extensions import db
from src.utils.time_utils import utcnow


class Scripts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    file_path = db.Column(db.String(256), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(64), nullable=True)
    content_hash = db.Column(db.String(32), nullable=True)  # MD5 del archivo
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)

    __table_args__ = (db.UniqueConstraint("file_path", name="uq_scripts_file_path"),)

    def __repr__(self):
        return f"<Scripts {self.title}>"
