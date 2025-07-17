import os
from extensions import db
from src.models.theory import Theory
from models.write_ups import WriteUps
from src.models.scripts import Scripts
from src.utils.search_utils import populate_whoosh_index  # Importar la función de indexación
import asyncio

async def scan_directory(directory, model, file_extension, category=None):
    """
    Escanea un directorio y registra los archivos en la base de datos.

    :param directory: Ruta del directorio a escanear.
    :param model: Modelo de la base de datos para registrar los archivos.
    :param file_extension: Extensión de los archivos a buscar (por ejemplo, '.md', '.py').
    :param category: Categoría opcional para los archivos.
    """
    for root, _, files in os.walk(directory):  # Usar os.walk para recorrer subdirectorios
        for filename in files:
            if filename.endswith(file_extension):
                title = os.path.splitext(filename)[0]
                file_path = os.path.join(root, filename)
                
                # Determinar la categoría a partir del subdirectorio
                if not category:
                    relative_path = os.path.relpath(root, directory)
                    category = relative_path.split(os.sep)[0]  # Primer nivel del subdirectorio
                
                # Verificar si ya existe en la base de datos
                if not db.session.query(model).filter_by(file_path=file_path).first():
                    entry = model(title=title, file_path=file_path, category=category)
                    db.session.add(entry)
    db.session.commit()
    print(f"Archivos de {model.__name__} registrados en la base de datos.")
    await populate_whoosh_index() # Actualizar el índice después de escanear

async def scan_all():
    """
    Escanea todos los directorios relevantes y registra los archivos en la base de datos.
    """
    base_dir = 'data'
    directories = {
        'theory': (Theory, '.md'),
        'write_ups': (WriteUps, '.md'),
        'scripts': (Scripts, '.py')
    }

    for subdir, (model, extension) in directories.items():
        directory = os.path.join(base_dir, subdir)
        if os.path.exists(directory):
            await scan_directory(directory, model, extension)
        else:
            print(f"Directorio {directory} no encontrado.")