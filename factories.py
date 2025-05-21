# factories.py
from models import Usuario

class UsuarioFactory:
    @staticmethod
    def create(role, first_name, last_name, dni, email, raw_password):
        u = Usuario(
            first_name=first_name,
            last_name=last_name,
            dni=dni,
            email=email,
            rol=role
        )
        u.set_password(raw_password)
        return u
