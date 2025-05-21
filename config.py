import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Obtener la clave secreta desde una variable de entorno
    SECRET_KEY = os.environ.get('SECRET_KEY', 'clave_por_defecto')
    
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'cafeteria.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Caché simple en memoria
    CACHE_TYPE = 'simple'
