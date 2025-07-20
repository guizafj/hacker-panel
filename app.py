import asyncio
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
from src.utils.scanner import scan_all
from src.utils.search_utils import initialize_search_index

# Cargar variables de entorno desde .env
load_dotenv()

app = Flask(__name__)

app.config.from_object(Config)
talisman = Talisman()
csrf = CSRFProtect(app)

def initialize_extensions(app):
    """
    Inicializa las extensiones de Flask (DB, Mail, Migrate, LoginManager).

    Args:
        app (Flask): Instancia de la aplicación Flask.
    """
    db.init_app(app)
    Migrate(app, db)

    # Deshabilitar strict_slashes para mayor flexibilidad en rutas
    app.url_map.strict_slashes = False

initialize_extensions(app)

app.register_blueprint(general_bp)
app.register_blueprint(task_bp, url_prefix = '/task')
app.register_blueprint(data_bp, url_prefix = '/data')

@app.errorhandler(415)
def unsupported_media_type(error):
    return {"error": "El tipo de contenido no es soportado. Usa 'application/json' o un formulario HTML."}, 415

talisman.init_app(
    app,
    content_security_policy={
        'default-src': ["'self'"],
        'script-src': [
            "'self'",
            "'unsafe-inline'",
            "'unsafe-eval'",
            "https://cdn.jsdelivr.net",
            "https://*.jsdelivr.net"
        ],
        'style-src': [
            "'self'",
            "'unsafe-inline'",
            "https://cdn.jsdelivr.net",
            "https://*.jsdelivr.net",
        ],
        'font-src': [
            "'self'", 
            "data:", 
            "https://cdn.jsdelivr.net",
            "https://*.jsdelivr.net"
        ],
        'img-src': ["'self'", "data:", "https:"],
        'connect-src': ["'self'", "https://cdn.jsdelivr.net"]
    },
    force_https=False,
    frame_options='DENY'
)
csrf.init_app(app)

@app.after_request
def add_csrf_header(response):
    response.headers.set('X-CSRFToken', session.get('_csrf_token'))
    return response

# Comando personalizado para ejectutar el escáner / ejecutar -> flask scan-directories
@click.command('scan-directories')
@with_appcontext
def scan_directories_command():
    """Escanea los directorios y registra los cambios en la base de datos"""
    asyncio.run(scan_all())
    click.echo("Escaneo de directorios completado")
    
# Registrar el comando en la aplicación
app.cli.add_command(scan_directories_command)

file_handler = logging.FileHandler('errors.log')
file_handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
file_handler.setFormatter(formatter)

logging.getLogger().addHandler(file_handler)
logging.getLogger().setLevel(logging.ERROR)

if __name__ == '__main__':
    # Asegurarse de que la carpeta instance exista
    if not os.path.exists('instance'):
        os.makedirs('instance')

    # Inicializar el índice de búsqueda
    with app.app_context():
        asyncio.run(initialize_search_index())
        
    app.run(debug=True, ssl_context=('cert.pem', 'key.pem'))
    
    # python app.py / -> Entra en modo debug on
    # Usar flask run / -> se salta el debug y da error con el certificado ssl flask run --debug --cert=cert.pem --key=key.pem