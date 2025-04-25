# config.py
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'tu_secreto_aqui'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'cafeteria.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
