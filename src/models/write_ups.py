from extensions import db

class WriteUps(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)  # Título del archivo
    file_path = db.Column(db.String(256), nullable=False)  # Ruta del archivo Markdown
    category = db.Column(db.String(64), nullable=True)  # Categoría obtenidas de los subdirectorios

    def __repr__(self):
        return f"<WriteUps {self.title}>"