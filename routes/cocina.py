# routes/cocina.py
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from models import db, DetallePedido, LogTransaccion
from datetime import datetime
from observer import publish

bp = Blueprint('cocina', __name__)

@bp.route('/pedidos')
@login_required
def pedidos():
    detalles = DetallePedido.query.filter_by(preparado=False).all()
    return render_template("cocina_pedidos.html", detalles=detalles)

@bp.route('/preparado/<int:detalle_id>', methods=['POST'])
@login_required
def preparado(detalle_id):
    d = DetallePedido.query.get_or_404(detalle_id)
    d.preparado = True
    db.session.commit()

    # Log interno
    log = LogTransaccion(
        pedido_id=d.pedido_id,
        accion="Producto preparado (Cocina)",
        detalle=f"Detalle ID {d.id} marcado como preparado"
    )
    db.session.add(log)
    db.session.commit()

    # Publicar el evento para todos los observers
    publish('detalle_preparado', {
        'pedido_id':  d.pedido_id,
        'detalle_id': d.id
    })

    # Si todos los ítems del pedido están preparados, actualiza estado
    p = d.pedido
    if all(item.preparado for item in p.detalles):
        p.estado = 'preparado'
        db.session.commit()

    flash("Producto marcado como preparado.", "success")
    return redirect(url_for('cocina.pedidos'))
