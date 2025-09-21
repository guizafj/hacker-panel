import os
import logging

logging.basicConfig(
    filename='errors.log',
    level=logging.ERROR,
    format='%(asctime)s- %(message)s'
)

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'una-cadena-secreta-muy-dificil'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'instance', 'hacker-panel.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuración de tipos MIME
    SEND_FILE_MAX_AGE_DEFAULT = 0
    TEMPLATES_AUTO_RELOAD = True
    
    # Configuración de archivos estáticos
    STATIC_FOLDER = 'static'
    STATIC_URL_PATH = '/static'
    
    # Configuración para url_for fuera de requests
    SERVER_NAME = os.environ.get('SERVER_NAME') or 'localhost:5000'
    APPLICATION_ROOT = '/'
    PREFERRED_URL_SCHEME = 'http'
