# routes/cocina.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, DetallePedido, Pedido, LogTransaccion
from datetime import datetime

bp = Blueprint('cocina', __name__)

@bp.route('/pedidos')
def pedidos():
    detalles = DetallePedido.query.filter_by(preparado=False).all()
    return render_template("cocina_pedidos.html", detalles=detalles)

@bp.route('/preparado/<int:detalle_id>', methods=['POST'])
def preparado(detalle_id):
    detalle = DetallePedido.query.get_or_404(detalle_id)
    detalle.preparado = True
    db.session.commit()
    log = LogTransaccion(pedido_id=detalle.pedido_id, accion="Producto preparado (Cocina)",
                         detalle=f"Producto {detalle.producto.nombre} marcado como preparado.", fecha_hora=datetime.utcnow())
    db.session.add(log)
    db.session.commit()

    # Verificar si todos los detalles del pedido están preparados y actualizar estado del pedido
    pedido = detalle.pedido
    if all(d.preparado for d in pedido.detalles):
        pedido.estado = "preparado"
        db.session.commit()
    flash("Producto marcado como preparado.", "success")
    return redirect(url_for('cocina.pedidos'))
