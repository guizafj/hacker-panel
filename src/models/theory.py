from extensions import db


class Theory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)  # Título del archivo
    file_path = db.Column(db.String(256), nullable=False)  # Ruta del archivo Markdown
    category = db.Column(db.String(64), nullable=True)  # Categoría (nombre del curso)

    def __repr__(self):
        return f"<Theory {self.title}>"
