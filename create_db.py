# create_db.py
from app import app
from models import db, Producto, Inventario
from factories import UsuarioFactory
from datetime import datetime

def init_db():
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Agregar usuarios de prueba usando UserFactory
        admin = UsuarioFactory.create(
            role="admin",
            first_name="Admin",
            last_name="Cafeteria",
            dni="00000000",
            email="admin@cafeteria.com",
            raw_password="admin"
        )
        mesero = UsuarioFactory.create(
            role="mesero",
            first_name="Mesero",
            last_name="Uno",
            dni="11111111",
            email="mesero@cafeteria.com",
            raw_password="mesero"
        )
        cocinero = UsuarioFactory.create(
            role="cocinero",
            first_name="Cocinero",
            last_name="Uno",
            dni="22222222",
            email="cocinero@cafeteria.com",
            raw_password="cocinero"
        )
        cliente = UsuarioFactory.create(
            role="cliente",
            first_name="Cliente",
            last_name="Ejemplo",
            dni="33333333",
            email="cliente@cafeteria.com",
            raw_password="cliente"
        )
        db.session.add_all([admin, mesero, cocinero, cliente])

        # Agregar productos y su inventario
        productos = [
            ("BC01","Espresso",      6.00,"Bebida Caliente","Café negro concentrado.","https://via.placeholder.com/150"),
            ("BC02","Americano",      7.00,"Bebida Caliente","Café con más agua.","https://via.placeholder.com/150"),
            ("BF01","Café Helado",   10.00,"Bebida Fría",    "Café frío con hielo.","https://via.placeholder.com/150"),
            ("C01","Croissant Mantequilla",7.00,"Comida","Croissant hojaldrado.","https://via.placeholder.com/150"),
        ]
        for code, name, price, cat, desc, url in productos:
            p = Producto(
                codigo=code,
                nombre=name,
                precio=price,
                categoria=cat,
                descripcion=desc,
                imagen_url=url
            )
            db.session.add(p)
            inv = Inventario(producto_id=code, stock=10, unidad="unidades")
            db.session.add(inv)

        db.session.commit()
        print("Base de datos creada y poblada con datos iniciales.")

if __name__ == '__main__':
    init_db()
