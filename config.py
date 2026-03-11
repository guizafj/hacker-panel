import os
import logging

# FIX: se elimina el basicConfig de aquí. app.py gestiona su propio FileHandler
# para el logger de Flask. Tener basicConfig aquí causaba entradas duplicadas en
# errors.log porque configuraba el logger raíz Y app.py añadía otro handler encima.
logging.basicConfig(level=logging.WARNING)

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "una-cadena-secreta-muy-dificil"
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "instance", "hacker-panel.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SEND_FILE_MAX_AGE_DEFAULT = 0
    TEMPLATES_AUTO_RELOAD = True

    STATIC_FOLDER = "static"
    STATIC_URL_PATH = "/static"

    # FIX: SERVER_NAME eliminado. Con SERVER_NAME seteado, Flask rechaza peticiones
    # de cualquier host que no coincida exactamente (falla en Docker, con IP de red,
    # o si el puerto cambia). Para desarrollo local no aporta ningún beneficio.
    # Si se necesita para url_for() fuera de request context, usar app.test_request_context()
    # o pasar _external=False explícitamente.
    APPLICATION_ROOT = "/"
    PREFERRED_URL_SCHEME = "http"