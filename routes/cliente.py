# routes/cliente.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Usuario, Producto, Inventario, Pedido, DetallePedido, LogTransaccion
from datetime import datetime

bp = Blueprint('cliente', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        usuario = Usuario.query.filter_by(email=email, password=password).first()
        if usuario:
            flash("Inicio de sesión exitoso.", "success")
            # Redireccionar según rol:
            if usuario.rol == "cliente":
                return redirect(url_for('cliente.menu'))
            elif usuario.rol == "mesero":
                return redirect(url_for('mesero.pedidos'))
            elif usuario.rol == "cocinero":
                return redirect(url_for('cocina.pedidos'))
            elif usuario.rol == "admin":
                return redirect(url_for('admin.dashboard'))
        else:
            flash("Credenciales incorrectas.", "danger")
    return render_template("login.html")

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name  = request.form.get('last_name')
        dni        = request.form.get('dni')
        email      = request.form.get('email')
        password   = request.form.get('password')
        nuevo_usuario = Usuario(first_name=first_name, last_name=last_name, dni=dni,
                                email=email, password=password, rol="cliente")
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash("Registro exitoso. Inicia sesión.", "success")
        return redirect(url_for('cliente.login'))
    return render_template("register.html")

@bp.route('/menu')
def menu():
    productos = Producto.query.all()
    return render_template("menu.html", productos=productos)

@bp.route('/order', methods=['GET', 'POST'])
def order():
    if request.method == 'POST':
        client_name = request.form.get('client_name')
        order_type = request.form.get('order_type')  # "para_llevar" o "comer_aqui"
        table_number = request.form.get('table_number') if order_type == 'comer_aqui' else None
        usuario_id = 4  # Simulación: asumimos que el cliente "Cliente Ejemplo" (ID 4) está logueado

        # Crear el pedido sin generar ticket ni procesar pago (esto lo hace el mesero luego)
        pedido = Pedido(usuario_id=usuario_id, client_name=client_name,
                        order_type=order_type, table_number=table_number,
                        estado='pendiente', fecha_hora=datetime.utcnow())
        db.session.add(pedido)
        db.session.commit()

        productos_seleccionados = request.form.getlist('producto_codigo[]')
        cantidades = request.form.getlist('cantidad[]')
        total = 0.0

        for prod_codigo, cantidad_str in zip(productos_seleccionados, cantidades):
            cantidad = int(cantidad_str)
            if cantidad > 0:
                producto = Producto.query.filter_by(codigo=prod_codigo).first()
                inv = Inventario.query.filter_by(producto_id=prod_codigo).first()
                if not producto:
                    flash(f"Producto {prod_codigo} no encontrado.", "danger")
                    continue
                if not inv or inv.stock < cantidad:
                    flash(f"No hay suficiente stock de {producto.nombre}.", "warning")
                    continue
                detalle = DetallePedido(pedido_id=pedido.id, producto_id=prod_codigo,
                                         cantidad=cantidad, precio_unitario=producto.precio)
                db.session.add(detalle)
                inv.stock -= cantidad
                total += producto.precio * cantidad

        pedido.total = total
        log = LogTransaccion(pedido_id=pedido.id, accion="Pedido creado",
                             detalle=f"Cliente: {client_name}, Total: {total}", fecha_hora=datetime.utcnow())
        db.session.add(log)
        db.session.commit()

        flash("Pedido tomado. Espera a que el mesero gestione el cobro.", "success")
        return redirect(url_for('cliente.menu'))

    productos = Producto.query.all()
    return render_template("order.html", productos=productos)
