# routes/admin.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Usuario, Producto, Inventario
from datetime import datetime

bp = Blueprint('admin', __name__)

@bp.route('/dashboard')
def dashboard():
    usuarios = Usuario.query.all()
    productos = Producto.query.all()
    inventario = Inventario.query.all()
    return render_template("admin_dashboard.html", usuarios=usuarios, productos=productos, inventario=inventario)

@bp.route('/crear_producto', methods=['GET', 'POST'])
def crear_producto():
    if request.method == 'POST':
        codigo = request.form.get('codigo')
        nombre = request.form.get('nombre')
        precio = float(request.form.get('precio'))
        categoria = request.form.get('categoria')
        descripcion = request.form.get('descripcion')
        imagen_url = request.form.get('imagen_url')
        nuevo_producto = Producto(codigo=codigo, nombre=nombre, precio=precio, categoria=categoria,
                                    descripcion=descripcion, imagen_url=imagen_url)
        db.session.add(nuevo_producto)
        inventario = Inventario(producto_id=codigo, stock=int(request.form.get('stock', 0)), unidad="unidades")
        db.session.add(inventario)
        db.session.commit()
        flash("Producto creado.", "success")
        return redirect(url_for('admin.dashboard'))
    return render_template("crear_producto.html")

@bp.route('/editar_usuario/<int:user_id>', methods=['GET', 'POST'])
def editar_usuario(user_id):
    usuario = Usuario.query.get_or_404(user_id)
    if request.method == 'POST':
        usuario.first_name = request.form.get('first_name')
        usuario.last_name  = request.form.get('last_name')
        usuario.email      = request.form.get('email')
        usuario.password   = request.form.get('password')
        usuario.dni        = request.form.get('dni')
        usuario.rol        = request.form.get('rol')
        db.session.commit()
        flash("Usuario actualizado.", "success")
        return redirect(url_for('admin.dashboard'))
    return render_template("editar_usuario.html", usuario=usuario)

@bp.route('/eliminar_usuario/<int:user_id>', methods=['POST'])
def eliminar_usuario(user_id):
    usuario = Usuario.query.get_or_404(user_id)
    db.session.delete(usuario)
    db.session.commit()
    flash("Usuario eliminado.", "success")
    return redirect(url_for('admin.dashboard'))
