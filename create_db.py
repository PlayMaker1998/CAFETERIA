# create_db.py
from app import app
from models import db, Usuario, Producto, Inventario
from datetime import datetime

def init_db():
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Agregar usuarios de prueba
        admin = Usuario(
            first_name="Admin",
            last_name="Cafeteria",
            dni="00000000",
            email="admin@cafeteria.com",
            password="admin",  # En producción: usar hash
            rol="admin",
            fecha_registro=datetime.utcnow()
        )
        mesero = Usuario(
            first_name="Mesero",
            last_name="Uno",
            dni="11111111",
            email="mesero@cafeteria.com",
            password="mesero",  # En producción: usar hash
            rol="mesero",
            fecha_registro=datetime.utcnow()
        )
        cocinero = Usuario(
            first_name="Cocinero",
            last_name="Uno",
            dni="22222222",
            email="cocinero@cafeteria.com",
            password="cocinero",  # En producción: usar hash
            rol="cocinero",
            fecha_registro=datetime.utcnow()
        )
        cliente = Usuario(
            first_name="Cliente",
            last_name="Ejemplo",
            dni="33333333",
            email="cliente@cafeteria.com",
            password="cliente",  # En producción: usar hash
            rol="cliente",
            fecha_registro=datetime.utcnow()
        )
        db.session.add_all([admin, mesero, cocinero, cliente])

        # Agregar productos y su inventario
        productos = [
            Producto(codigo="BC01", nombre="Espresso", precio=6.00, categoria="Bebida Caliente",
                     descripcion="Café negro concentrado.", imagen_url="https://via.placeholder.com/150"),
            Producto(codigo="BC02", nombre="Americano", precio=7.00, categoria="Bebida Caliente",
                     descripcion="Café con más agua.", imagen_url="https://via.placeholder.com/150"),
            Producto(codigo="BF01", nombre="Café Helado", precio=10.00, categoria="Bebida Fría",
                     descripcion="Café frío con hielo.", imagen_url="https://via.placeholder.com/150"),
            Producto(codigo="C01", nombre="Croissant de Mantequilla", precio=7.00, categoria="Comida",
                     descripcion="Delicioso croissant hojaldrado.", imagen_url="https://via.placeholder.com/150")
        ]
        for prod in productos:
            db.session.add(prod)
            inv = Inventario(producto_id=prod.codigo, stock=10, unidad="unidades")
            db.session.add(inv)

        db.session.commit()
        print("Base de datos creada y poblada con datos iniciales.")

if __name__ == '__main__':
    init_db()
