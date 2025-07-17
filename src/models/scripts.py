from extensions import db

class Scripts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)  # Nombre del script
    file_path = db.Column(db.String(256), nullable=False)  # Ruta del archivo Python
    description = db.Column(db.Text, nullable=True)  # Descripción opcional
    category = db.Column(db.String(64), nullable=True) # Categorias obtenidas de los directorios 

    def __repr__(self):
        return f"<Scripts {self.title}>"