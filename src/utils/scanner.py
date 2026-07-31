import os
import logging
from extensions import db
from src.models.theory import Theory
from src.models.write_ups import WriteUps
from src.models.scripts import Scripts
from src.utils.search_utils import index_file_entry, initialize_search_index

logger = logging.getLogger(__name__)


def scan_directory(app, directory: str, model, file_extension: str) -> dict[str, int]:
    """Escanea un directorio recursivamente y sincroniza con la base de datos.

    Para cada archivo encontrado:
        - Si no existe en BD → lo registra y lo indexa en FTS5.
        - Si ya existe en BD → solo re-indexa si el contenido cambió (por hash MD5).
        - Si un registro en BD apunta a un archivo que ya no existe → lo elimina.

    Returns:
        {"added": N, "updated": N, "removed": N}
    """
    model_type_map = {
        Theory: "theory",
        WriteUps: "writeup",
        Scripts: "script",
    }
    model_type = model_type_map[model]
    counts = {"added": 0, "updated": 0, "removed": 0}

    # --- Paso 1: escanear disco y sincronizar con BD ---
    found_paths = set()

    for root, _, files in os.walk(directory):
        for filename in files:
            if not filename.endswith(file_extension):
                continue

            file_path = os.path.join(root, filename)
            found_paths.add(file_path)
            title = os.path.splitext(filename)[0]

            # Calcular categoría desde el subdirectorio relativo
            relative = os.path.relpath(root, directory)
            category = relative.split(os.sep)[0]
            if category == ".":
                category = ""

            existing = db.session.query(model).filter_by(file_path=file_path).first()

            if not existing:
                # Archivo nuevo: registrar en BD
                entry = model(
                    title=title,
                    file_path=file_path,
                    category=category,
                )
                db.session.add(entry)
                db.session.flush()  # Obtener el ID antes de poder indexar
                # Commit: sin esto, la transacción ORM mantiene un lock de
                # escritura que bloquea la conexión sqlite3 directa de FTS5
                # ("database is locked") al indexar el archivo nuevo.
                db.session.commit()

                # Indexar en FTS5
                index_file_entry(app, entry, model_type)
                counts["added"] += 1
                logger.info(f"Nuevo archivo registrado: {file_path}")
            else:
                # Archivo existente: re-indexar solo si cambió el contenido
                reindexed = index_file_entry(app, existing, model_type)
                if reindexed:
                    counts["updated"] += 1
                    logger.info(f"Archivo re-indexado (cambió): {file_path}")

    db.session.commit()

    # --- Paso 2: limpiar registros huérfanos (archivo eliminado del disco) ---
    from src.utils.search_utils import remove_from_index

    all_entries = db.session.query(model).all()
    for entry in all_entries:
        if entry.file_path not in found_paths:
            logger.info(f"Archivo eliminado del disco, limpiando BD: {entry.file_path}")
            remove_from_index(app, model_type, entry.id)
            db.session.delete(entry)
            counts["removed"] += 1

    db.session.commit()
    return counts


def scan_all(app) -> None:
    """Escanea todos los directorios y sincroniza BD + índice FTS5.

    Llamado por `flask scan-directories`.
    """
    base_dir = "data"
    directories = {
        "theory": (Theory, ".md"),
        "write_ups": (WriteUps, ".md"),
        "scripts": (Scripts, ".py"),
    }

    # Garantizar que las tablas FTS5 existan antes de indexar,
    # para que scan-directories sea autocontenido en despliegues limpios.
    initialize_search_index(app)

    total = {"added": 0, "updated": 0, "removed": 0}

    for subdir, (model, extension) in directories.items():
        directory = os.path.join(base_dir, subdir)
        if not os.path.exists(directory):
            logger.warning(f"Directorio no encontrado: {directory}")
            continue

        counts = scan_directory(app, directory, model, extension)
        for k in total:
            total[k] += counts[k]
        logger.info(
            f"{model.__name__}: +{counts['added']} nuevos, "
            f"~{counts['updated']} actualizados, "
            f"-{counts['removed']} eliminados"
        )

    logger.info(
        f"Escaneo completado — Total: "
        f"+{total['added']} nuevos, ~{total['updated']} actualizados, "
        f"-{total['removed']} eliminados"
    )
