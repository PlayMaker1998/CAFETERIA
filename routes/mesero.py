# routes/mesero.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Pedido, DetallePedido, TicketPago, BoletaPago, LogTransaccion
from datetime import datetime

bp = Blueprint('mesero', __name__)

@bp.route('/pedidos')
def pedidos():
    # Mostrar todos los pedidos para visualización, sin importar su estado
    pedidos = Pedido.query.all()
    return render_template("mesero_pedidos.html", pedidos=pedidos)

@bp.route('/detalle/<int:pedido_id>')
def detalle(pedido_id):
    # Visualiza el detalle de un pedido específico (incluye el número de mesa)
    pedido = Pedido.query.get_or_404(pedido_id)
    return render_template("mesero_detalle.html", pedido=pedido)

@bp.route('/entregar/<int:pedido_id>', methods=['POST'])
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

    log = LogTransaccion(pedido_id=pedido.id, accion="Pedido entregado (Mesero)",
                         detalle="El mesero marcó el pedido como entregado.", fecha_hora=datetime.utcnow())
    db.session.add(log)
    db.session.commit()
    flash("Productos entregados. Pedido marcado para cobro.", "success")
    return redirect(url_for('mesero.pedidos'))

@bp.route('/por_cobrar')
def por_cobrar():
    # Mostrar los pedidos que han sido entregados y están pendientes de cobro
    pedidos = Pedido.query.filter_by(estado="entregado").all()
    return render_template("mesero_pedidos_por_cobrar.html", pedidos=pedidos)

@bp.route('/cobrar', methods=['POST'])
def cobrar():
    # Obtener la lista de pedidos seleccionados y el método de pago
    selected_ids = request.form.getlist('pedido_id')
    metodo_pago = request.form.get("metodo_pago", "efectivo")  # Solo se permite 'efectivo' o 'tarjeta'
    
    if not selected_ids:
        flash("No se han seleccionado pedidos para cobrar.", "warning")
        return redirect(url_for('mesero.por_cobrar'))
    
    total_cobrado = 0.0
    pedidos_seleccionados = []
    detalles_text_list = []
    
    # Actualizar el estado de cada pedido a "cobrado" y acumular detalles individuales
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
    
    # Consolidar la información de los pedidos, cada uno en una línea y al final el total consolidado
    detalles_consolidados = "\n".join(detalles_text_list) + f"\nTOTAL: S/ {total_cobrado:.2f}"
    
    # Se crea un único ticket consolidado usando el primer pedido seleccionado como referencia
    ticket = TicketPago(
        pedido_id=pedidos_seleccionados[0].id,  # Se usa el primer pedido
        monto_total=total_cobrado,
        estado_pago='pagado'
    )
    db.session.add(ticket)
    db.session.commit()
    
    # Crear la boleta consolidada con los detalles de cada pedido y el total final
    boleta = BoletaPago(
        ticket_pago_id=ticket.id,
        detalles=detalles_consolidados,
        metodo_pago=metodo_pago
    )
    db.session.add(boleta)
    db.session.commit()
    
    # Registrar la transacción en el log
    log = LogTransaccion(
        pedido_id=pedidos_seleccionados[0].id,
        accion="Cobro Consolidado (Mesero)",
        detalle=f"Pedidos cobrados con método {metodo_pago}: {', '.join(selected_ids)}.",
        fecha_hora=datetime.utcnow()
    )
    db.session.add(log)
    db.session.commit()
    
    flash(f"Se ha cobrado un total de S/ {total_cobrado} en una boleta consolidada.", "success")
    return redirect(url_for('mesero.boletas'))



# Ruta para visualizar una boleta individual
@bp.route('/boleta/<int:boleta_id>')
def boleta(boleta_id):
    boleta = BoletaPago.query.get_or_404(boleta_id)
    return render_template("boleta.html", boleta=boleta)

# Ruta para listar todas las boletas generadas
@bp.route('/boletas')
def boletas():
    boletas = BoletaPago.query.all()
    return render_template("mesero_boletas.html", boletas=boletas)
