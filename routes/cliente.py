# routes/cliente.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, Usuario, Producto, Inventario, TicketPago, BoletaPago, LogTransaccion
from factories import UsuarioFactory
from facades import OrderFacade
from extensions import cache

bp = Blueprint('cliente', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = Usuario.query.filter_by(email=request.form['email']).first()
        if u and u.check_password(request.form['password']):
            login_user(u)
            flash("Inicio de sesión exitoso.", "success")
            if u.rol == 'cliente':
                return redirect(url_for('cliente.menu'))
            if u.rol == 'mesero':
                return redirect(url_for('mesero.pedidos'))
            if u.rol == 'cocinero':
                return redirect(url_for('cocina.pedidos'))
            if u.rol == 'admin':
                return redirect(url_for('admin.dashboard'))
        else:
            flash("Credenciales inválidas.", "danger")
    return render_template("login.html")

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('cliente.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        u = UsuarioFactory.create(
            role='cliente',
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            dni=request.form['dni'],
            email=request.form['email'],
            raw_password=request.form['password']
        )
        db.session.add(u)
        db.session.commit()
        flash("Registro exitoso.", "success")
        return redirect(url_for('cliente.login'))
    return render_template("register.html")

@bp.route('/menu')
@cache.cached(timeout=60)
def menu():
    productos = Producto.query.all()
    return render_template("menu.html", productos=productos)

@bp.route('/order', methods=['GET', 'POST'])
@login_required
def order():
    if request.method == 'POST':
        # Recolectar los ítems seleccionados: lista de tuplas (codigo, cantidad)
        items = []
        for code, qty in zip(request.form.getlist('producto_codigo[]'),
                             request.form.getlist('cantidad[]')):
            cantidad = int(qty)
            if cantidad > 0:
                items.append((code, cantidad))

        # Llamada al Facade para procesar todo el pedido
        pedido_id = OrderFacade.place_order(
            usuario_id=current_user.id,
            client_name=request.form['client_name'],
            order_type=request.form['order_type'],
            table_number=request.form.get('table_number'),
            items=items
        )

        flash("Pedido realizado y ticket generado.", "success")
        return redirect(url_for('cliente.ticket', ticket_id=pedido_id))

    # GET: mostrar formulario
    productos = Producto.query.all()
    return render_template("order.html", productos=productos)

@bp.route('/ticket/<int:ticket_id>')
@login_required
def ticket(ticket_id):
    t = TicketPago.query.get_or_404(ticket_id)
    return render_template("ticket.html", ticket=t)

@bp.route('/payment/<int:ticket_id>', methods=['POST'])
@login_required
def payment(ticket_id):
    t = TicketPago.query.get_or_404(ticket_id)
    t.estado_pago = 'pagado'
    db.session.commit()

    log = LogTransaccion(
        pedido_id=t.pedido_id,
        accion="Pago confirmado",
        detalle=""
    )
    db.session.add(log)
    db.session.commit()

    b = BoletaPago(
        ticket_pago_id=t.id,
        detalles=f"Pedido #{t.pedido_id}",
        metodo_pago=request.form['metodo_pago']
    )
    db.session.add(b)
    db.session.commit()

    flash("Pago y boleta generados.", "success")
    return redirect(url_for('cliente.boleta', boleta_id=b.id))

@bp.route('/boleta/<int:boleta_id>')
@login_required
def boleta(boleta_id):
    b = BoletaPago.query.get_or_404(boleta_id)
    return render_template("boleta.html", boleta=b)
