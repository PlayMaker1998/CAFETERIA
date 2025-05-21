# routes/mesero.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models import db, Pedido, DetallePedido, TicketPago, BoletaPago, LogTransaccion
from datetime import datetime
from observer import subscribe  # <-- importamos el mecanismo Observer

bp = Blueprint('mesero', __name__)

# 1) Definimos el handler que se ejecutará cuando la cocina publique un detalle preparado.
def on_detalle_preparado(data):
    pedido_id = data.get('pedido_id')
    detalle_id = data.get('detalle_id')
    # Aquí podemos, por ejemplo, escribir en el log, enviar un websocket, o simplemente imprimir:
    print(f"[Observer] Notificación: detalle {detalle_id} del pedido {pedido_id} está preparado.")

# 2) Nos suscribimos al evento 'detalle_preparado' para recibir notificaciones.
subscribe('detalle_preparado', on_detalle_preparado)

@bp.route('/pedidos')
@login_required
def pedidos():
    # Mostrar todos los pedidos para visualización, sin importar su estado
    pedidos = Pedido.query.all()
    return render_template("mesero_pedidos.html", pedidos=pedidos)

@bp.route('/detalle/<int:pedido_id>')
@login_required
def detalle(pedido_id):
    # Visualiza el detalle de un pedido específico (incluye el número de mesa)
    pedido = Pedido.query.get_or_404(pedido_id)
    return render_template("mesero_detalle.html", pedido=pedido)

@bp.route('/entregar/<int:pedido_id>', methods=['POST'])
@login_required
def entregar(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    # Recoger las IDs de los detalles que el mesero marca como entregados
    entregados = request.form.getlist('entregado[]')
    for det in pedido.detalles:
        if str(det.id) in entregados:
            det.entregado = True
    db.session.commit()

    # Si todos los detalles han sido entregados, se actualiza el estado a "entregado"
    if all(d.entregado for d in pedido.detalles):
        pedido.estado = "entregado"
    db.session.commit()

    log = LogTransaccion(
        pedido_id=pedido.id,
        accion="Pedido entregado (Mesero)",
        detalle="El mesero marcó el pedido como entregado.",
        fecha_hora=datetime.utcnow()
    )
    db.session.add(log)
    db.session.commit()
    flash("Productos entregados. Pedido marcado para cobro.", "success")
    return redirect(url_for('mesero.pedidos'))

@bp.route('/por_cobrar')
@login_required
def por_cobrar():
    # Mostrar los pedidos que han sido entregados y están pendientes de cobro
    pedidos = Pedido.query.filter_by(estado="entregado").all()
    return render_template("mesero_pedidos_por_cobrar.html", pedidos=pedidos)

@bp.route('/cobrar', methods=['POST'])
@login_required
def cobrar():
    # Obtener la lista de pedidos seleccionados y el método de pago
    selected_ids = request.form.getlist('pedido_id')
    metodo_pago = request.form.get("metodo_pago", "efectivo")  # Solo 'efectivo' o 'tarjeta'
    
    if not selected_ids:
        flash("No se han seleccionado pedidos para cobrar.", "warning")
        return redirect(url_for('mesero.por_cobrar'))
    
    total_cobrado = 0.0
    pedidos_seleccionados = []
    detalles_text_list = []
    
    # Actualizar el estado de cada pedido a "cobrado" y acumular detalles
    for pedido_id in selected_ids:
        pedido = Pedido.query.get(int(pedido_id))
        if pedido:
            pedido.estado = "cobrado"
            db.session.commit()
            total_cobrado += pedido.total
            detalles_text_list.append(
                f"Pedido #{pedido.id}: Mesa: {pedido.table_number or 'N/A'}, Total: S/ {pedido.total:.2f}"
            )
            pedidos_seleccionados.append(pedido)
    
    # Consolidar la información
    detalles_consolidados = "\n".join(detalles_text_list) + f"\nTOTAL: S/ {total_cobrado:.2f}"
    
    # Crear ticket consolidado (usando el primer pedido como referencia)
    ticket = TicketPago(
        pedido_id=pedidos_seleccionados[0].id,
        monto_total=total_cobrado,
        estado_pago='pagado'
    )
    db.session.add(ticket)
    db.session.commit()
    
    # Crear la boleta consolidada
    boleta = BoletaPago(
        ticket_pago_id=ticket.id,
        detalles=detalles_consolidados,
        metodo_pago=metodo_pago
    )
    db.session.add(boleta)
    db.session.commit()
    
    # Registrar en el log
    log = LogTransaccion(
        pedido_id=pedidos_seleccionados[0].id,
        accion="Cobro Consolidado (Mesero)",
        detalle=f"Pedidos cobrados: {', '.join(selected_ids)}; Monto: S/ {total_cobrado:.2f}",
        fecha_hora=datetime.utcnow()
    )
    db.session.add(log)
    db.session.commit()
    
    flash(f"Se ha cobrado un total de S/ {total_cobrado:.2f} en una boleta consolidada.", "success")
    return redirect(url_for('mesero.boletas'))

@bp.route('/boleta/<int:boleta_id>')
@login_required
def boleta(boleta_id):
    boleta = BoletaPago.query.get_or_404(boleta_id)
    return render_template("boleta.html", boleta=boleta)

@bp.route('/boletas')
@login_required
def boletas():
    boletas = BoletaPago.query.all()
    return render_template("mesero_boletas.html", boletas=boletas)
