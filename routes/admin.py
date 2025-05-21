from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models import db, Usuario, Producto, Inventario
from datetime import datetime

bp = Blueprint('admin', __name__)

@bp.route('/dashboard')
@login_required
def dashboard():
    usuarios=Usuario.query.all()
    productos=Producto.query.all()
    inventario=Inventario.query.all()
    return render_template("admin_dashboard.html", usuarios=usuarios,
                           productos=productos, inventario=inventario)

@bp.route('/crear_producto', methods=['GET','POST'])
@login_required
def crear_producto():
    if request.method=='POST':
        from models import Producto, Inventario
        p=Producto(codigo=request.form['codigo'],
                  nombre=request.form['nombre'],
                  precio=float(request.form['precio']),
                  categoria=request.form['categoria'],
                  descripcion=request.form['descripcion'],
                  imagen_url=request.form['imagen_url'])
        db.session.add(p)
        db.session.add(Inventario(producto_id=p.codigo, stock=int(request.form['stock']), unidad='unidades'))
        db.session.commit()
        flash("Producto creado.","success")
        return redirect(url_for('admin.dashboard'))
    return render_template("crear_producto.html")

@bp.route('/editar_usuario/<int:user_id>', methods=['GET','POST'])
@login_required
def editar_usuario(user_id):
    u=Usuario.query.get_or_404(user_id)
    if request.method=='POST':
        u.first_name=request.form['first_name']
        u.last_name=request.form['last_name']
        u.dni=request.form['dni']
        u.email=request.form['email']
        u.rol=request.form['rol']
        if request.form['password']:
            u.set_password(request.form['password'])
        db.session.commit()
        flash("Usuario actualizado.","success")
        return redirect(url_for('admin.dashboard'))
    return render_template("editar_usuario.html", usuario=u)

@bp.route('/eliminar_usuario/<int:user_id>', methods=['POST'])
@login_required
def eliminar_usuario(user_id):
    u=Usuario.query.get_or_404(user_id)
    db.session.delete(u); db.session.commit()
    flash("Usuario eliminado.","success")
    return redirect(url_for('admin.dashboard'))
