"""
search_utils.py — Motor de búsqueda unificado usando SQLite FTS5.

Reemplaza Whoosh por SQLite FTS5, que:
- Viene incluido en Python (sin dependencias externas)
- Es significativamente más rápido con volúmenes grandes
- Vive en la misma base de datos que el resto de la app
- Soporta ranking BM25 nativo, búsqueda por prefijo y snippets

Tablas que gestiona este módulo (fuera del ORM, SQL directo):
  - fts_documents      → tabla virtual FTS5 (índice de búsqueda)
  - fts_documents_meta → tabla auxiliar con model_type, object_id y category
"""

import hashlib
import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers de conexión
# ---------------------------------------------------------------------------


def _get_db_path(app) -> str:
    """Devuelve la ruta al archivo SQLite desde la config de Flask."""
    uri: str = app.config["SQLALCHEMY_DATABASE_URI"]
    return uri.replace("sqlite:///", "")


def _connect(app) -> sqlite3.Connection:
    conn = sqlite3.connect(_get_db_path(app))
    conn.row_factory = sqlite3.Row
    # WAL mejora la concurrencia entre FTS5 (conexión directa) y SQLAlchemy
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


# ---------------------------------------------------------------------------
# Creación del esquema FTS5
# ---------------------------------------------------------------------------


def create_fts_tables(app) -> None:
    """
    Crea las tablas FTS5 si no existen.
    Seguro llamarlo en cada arranque (IF NOT EXISTS).
    """
    with _connect(app) as conn:
        conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS fts_documents
            USING fts5(
                doc_id,
                title,
                content,
                tokenize = 'unicode61 remove_diacritics 1'
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS fts_documents_meta (
                doc_id      TEXT PRIMARY KEY,
                model_type  TEXT NOT NULL,
                object_id   INTEGER NOT NULL,
                category    TEXT,
                indexed_at  TEXT NOT NULL
            )
        """)
        conn.commit()
    logger.info("Tablas FTS5 verificadas/creadas.")


# ---------------------------------------------------------------------------
# Operaciones de indexación
# ---------------------------------------------------------------------------


def _upsert_document(
    conn: sqlite3.Connection,
    doc_id: str,
    title: str,
    content: str,
    model_type: str,
    object_id: int,
    category: str,
) -> None:
    """Inserta o reemplaza un documento en el índice FTS5."""
    # FTS5 no tiene UPSERT nativo: borrar + insertar
    conn.execute("DELETE FROM fts_documents WHERE doc_id = ?", (doc_id,))
    conn.execute(
        "INSERT INTO fts_documents (doc_id, title, content) VALUES (?, ?, ?)",
        (doc_id, title, content),
    )
    conn.execute(
        """
        INSERT INTO fts_documents_meta (doc_id, model_type, object_id, category, indexed_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(doc_id) DO UPDATE SET
            model_type = excluded.model_type,
            object_id  = excluded.object_id,
            category   = excluded.category,
            indexed_at = excluded.indexed_at
    """,
        (doc_id, model_type, object_id, category or "", datetime.utcnow().isoformat()),
    )


def _compute_hash(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Indexación incremental de archivos .md / .py
# ---------------------------------------------------------------------------


def index_file_entry(app, entry, model_type: str) -> bool:
    """
    Indexa un registro de Theory / WriteUps / Scripts si su contenido cambió.

    Compara el MD5 del archivo en disco con entry.content_hash.
    Solo re-indexa si el hash es diferente (indexación incremental).
    Actualiza entry.content_hash y entry.updated_at — el caller hace commit().

    Returns:
        True  si el documento fue re-indexado.
        False si el contenido no cambió.
    """
    try:
        content = Path(entry.file_path).read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.warning(f"Archivo no encontrado, omitiendo: {entry.file_path}")
        return False
    except Exception as e:
        logger.error(f"Error leyendo {entry.file_path}: {e}")
        return False

    current_hash = _compute_hash(content)

    if entry.content_hash == current_hash:
        return False  # Sin cambios, nada que hacer

    doc_id = f"{model_type}-{entry.id}"

    with _connect(app) as conn:
        _upsert_document(
            conn,
            doc_id=doc_id,
            title=entry.title,
            content=content,
            model_type=model_type,
            object_id=entry.id,
            category=entry.category or "",
        )
        conn.commit()

    entry.content_hash = current_hash
    entry.updated_at = datetime.utcnow()

    logger.debug(f"Re-indexado: {doc_id} ({entry.title})")
    return True


def index_structured_entry(app, entry, model_type: str) -> None:
    """
    Indexa un registro de Glosario o Checklist.
    Siempre re-indexa (son pequeños y se modifican por formulario).
    Llamar después de cada create/update de estos modelos.
    """
    if model_type == "glossary":
        doc_id = f"glossary-{entry.id}"
        title = entry.term
        content = f"{entry.term} {entry.translation} {entry.description or ''}"
        category = "glosario"
    elif model_type == "checklist":
        doc_id = f"checklist-{entry.id}"
        title = entry.objective
        content = f"{entry.objective} {entry.methodology} {entry.description or ''}"
        category = "checklist"
    else:
        raise ValueError(f"model_type no reconocido: {model_type}")

    with _connect(app) as conn:
        _upsert_document(
            conn,
            doc_id=doc_id,
            title=title,
            content=content,
            model_type=model_type,
            object_id=entry.id,
            category=category,
        )
        conn.commit()


def remove_from_index(app, model_type: str, object_id: int) -> None:
    """
    Elimina un documento del índice FTS5.
    Llamar al borrar un registro de la BD para mantener el índice limpio.
    """
    doc_id = f"{model_type}-{object_id}"
    with _connect(app) as conn:
        conn.execute("DELETE FROM fts_documents WHERE doc_id = ?", (doc_id,))
        conn.execute("DELETE FROM fts_documents_meta WHERE doc_id = ?", (doc_id,))
        conn.commit()
    logger.debug(f"Eliminado del índice: {doc_id}")


# ---------------------------------------------------------------------------
# Búsqueda
# ---------------------------------------------------------------------------


def search_fts(app, query: str, limit: int = 20) -> list[dict]:
    """
    Búsqueda FTS5 con expansión de sinónimos y snippets resaltados.

    Soporta:
      - Palabra simple:   "router"
      - Frase exacta:     '"SYN flood"'  (comillas en la query)
      - Prefijo:          "arp*"
      - Múltiples OR:     "router switch"

    Returns:
        Lista de dicts: {title, category, model_type, object_id, snippet}
    """
    if not query or not query.strip():
        return []

    # Cargar sinónimos
    try:
        syn_path = Path("src/utils/synonyms.json")
        sinonimos: dict = json.loads(syn_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        sinonimos = {}

    # Construir términos con sinónimos
    terms = [query.strip()]
    for palabra, lista_sinonimos in sinonimos.items():
        if palabra in query.lower():
            terms.extend(lista_sinonimos)

    # Escapar para FTS5: frases con espacios van entre comillas dobles
    def _fts_term(t: str) -> str:
        t = t.replace('"', '""')
        return f'"{t}"' if " " in t else t

    fts_query = " OR ".join(_fts_term(t) for t in terms)

    try:
        with _connect(app) as conn:
            rows = conn.execute(
                """
                SELECT
                    m.doc_id,
                    m.model_type,
                    m.object_id,
                    m.category,
                    d.title,
                    snippet(fts_documents, 2, '<mark>', '</mark>', '…', 20) AS snippet,
                    rank
                FROM fts_documents d
                JOIN fts_documents_meta m ON d.doc_id = m.doc_id
                WHERE fts_documents MATCH ?
                ORDER BY rank
                LIMIT ?
            """,
                (fts_query, limit),
            ).fetchall()

    except sqlite3.OperationalError as e:
        logger.error(f"Error en búsqueda FTS5 (query='{fts_query}'): {e}")
        return []

    return [
        {
            "title": row["title"],
            "category": row["category"],
            "model_type": row["model_type"],
            "object_id": row["object_id"],
            "snippet": row["snippet"],
        }
        for row in rows
    ]


def resolve_search_objects(results: list[dict]) -> list[dict]:
    """
    Añade el objeto ORM completo a cada resultado de search_fts().
    Separado para poder testear search_fts() sin contexto de app.
    """
    from extensions import db
    from src.models.theory import Theory
    from src.models.write_ups import WriteUps
    from src.models.scripts import Scripts
    from src.models.glossary import Term
    from src.models.checklist import Objective

    model_map = {
        "theory": Theory,
        "writeup": WriteUps,
        "script": Scripts,
        "glossary": Term,
        "checklist": Objective,
    }

    enriched = []
    for r in results:
        model_cls = model_map.get(r["model_type"])
        if model_cls is None:
            continue
        obj = db.session.get(model_cls, r["object_id"])
        if obj:
            enriched.append({**r, "object": obj})

    return enriched


# ---------------------------------------------------------------------------
# Poblado completo (rebuild-index)
# ---------------------------------------------------------------------------


def populate_fts_index(app) -> dict[str, int]:
    """
    Re-indexa todos los documentos.
    Útil para el comando `flask rebuild-index` y la primera ejecución.
    Crea las tablas FTS5 si no existen, por lo que es seguro llamarla
    directamente sin haber arrancado la app previamente.

    Returns:
        Conteo de documentos indexados por tipo.
    """
    # Garantizar que las tablas existen antes de escribir en ellas.
    # Necesario cuando se llama desde CLI sin pasar por initialize_search_index().
    create_fts_tables(app)

    from extensions import db
    from src.models.theory import Theory
    from src.models.write_ups import WriteUps
    from src.models.scripts import Scripts
    from src.models.glossary import Term
    from src.models.checklist import Objective

    counts = {"theory": 0, "writeup": 0, "script": 0, "glossary": 0, "checklist": 0}

    # Archivos .md y .py — indexación incremental por hash
    for model_cls, model_type, key in [
        (Theory, "theory", "theory"),
        (WriteUps, "writeup", "writeup"),
        (Scripts, "script", "script"),
    ]:
        for entry in model_cls.query.all():
            if index_file_entry(app, entry, model_type):
                counts[key] += 1
        db.session.commit()

    # Glosario y Checklist — siempre re-indexar completo
    for entry in Term.query.all():
        index_structured_entry(app, entry, "glossary")
        counts["glossary"] += 1

    for entry in Objective.query.all():
        index_structured_entry(app, entry, "checklist")
        counts["checklist"] += 1

    logger.info(f"Índice FTS5 reconstruido: {counts}")
    return counts


# ---------------------------------------------------------------------------
# Inicialización
# ---------------------------------------------------------------------------


def initialize_search_index(app) -> None:
    """
    Punto de entrada. Llamar una vez al arrancar la app (dentro de app_context).
    Crea las tablas FTS5 si no existen. No re-indexa contenido.
    """
    create_fts_tables(app)
    logger.info("Motor de búsqueda FTS5 listo.")
