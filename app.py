from flask import Flask, session
from flask.cli import with_appcontext
from flask_migrate import Migrate
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
import os
import click
import logging
from config import Config
from extensions import db
from src.routes.general_routes import general_bp
from src.routes.task_routes import task_bp
from src.routes.data_routes import data_bp
from src.utils.search_utils import initialize_search_index

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

csrf = CSRFProtect()
talisman = Talisman()


def initialize_extensions(app):
    """Inicializa las extensiones de Flask."""
    db.init_app(app)
    Migrate(app, db)
    csrf.init_app(app)
    app.url_map.strict_slashes = False


initialize_extensions(app)

app.register_blueprint(general_bp)
app.register_blueprint(task_bp, url_prefix="/task")
app.register_blueprint(data_bp, url_prefix="/data")


@app.errorhandler(415)
def unsupported_media_type(error):
    return {
        "error": "El tipo de contenido no es soportado. Usa 'application/json' o un formulario HTML."
    }, 415


talisman.init_app(
    app,
    content_security_policy={
        "default-src": ["'self'"],
        "script-src": [
            "'self'",
            "'unsafe-inline'",
            "'unsafe-eval'",
            "https://cdn.jsdelivr.net",
            "https://*.jsdelivr.net",
        ],
        "style-src": [
            "'self'",
            "'unsafe-inline'",
            "https://cdn.jsdelivr.net",
            "https://*.jsdelivr.net",
        ],
        "font-src": [
            "'self'",
            "data:",
            "https://cdn.jsdelivr.net",
            "https://*.jsdelivr.net",
        ],
        "img-src": ["'self'", "data:", "https:"],
        "connect-src": ["'self'", "https://cdn.jsdelivr.net"],
    },
    force_https=False,
    frame_options="DENY",
)


@app.after_request
def add_csrf_header(response):
    response.headers.set("X-CSRFToken", session.get("_csrf_token"))
    return response


# --- Logging (una sola vez) ---
if not app.logger.handlers:
    file_handler = logging.FileHandler("errors.log")
    file_handler.setLevel(logging.ERROR)
    formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.ERROR)


# ---------------------------------------------------------------------------
# Comandos CLI
# ---------------------------------------------------------------------------

@click.command("scan-directories")
@with_appcontext
def scan_directories_command():
    """
    Escanea los directorios data/ y sincroniza BD + índice FTS5.
    Solo re-indexa archivos que hayan cambiado (por hash MD5).

    Uso: flask scan-directories
    """
    from src.utils.scanner import scan_all
    scan_all(app)
    click.echo("Escaneo completado.")


@click.command("rebuild-index")
@with_appcontext
def rebuild_index_command():
    """
    Reconstruye el índice FTS5 completo desde cero.
    Usar cuando el índice esté corrupto o tras cambios en el schema FTS.

    Uso: flask rebuild-index
    """
    from src.utils.search_utils import populate_fts_index
    click.echo("Reconstruyendo índice FTS5...")
    counts = populate_fts_index(app)
    click.echo(
        f"Listo — theory: {counts['theory']}, writeup: {counts['writeup']}, "
        f"script: {counts['script']}, glossary: {counts['glossary']}, "
        f"checklist: {counts['checklist']}"
    )


app.cli.add_command(scan_directories_command)
app.cli.add_command(rebuild_index_command)


# ---------------------------------------------------------------------------
# Arranque
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if not os.path.exists("instance"):
        os.makedirs("instance")

    with app.app_context():
        # Crear tablas FTS5 si no existen (no re-indexa, solo estructura)
        initialize_search_index(app)

    app.run(debug=True, ssl_context=("cert.pem", "key.pem"))