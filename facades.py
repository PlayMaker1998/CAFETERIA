# facades.py
from models import Pedido, DetallePedido, Inventario, TicketPago, LogTransaccion, db
from datetime import datetime

class OrderFacade:
    @staticmethod
    def place_order(usuario_id, client_name, order_type, table_number, items):
        # Crear pedido
        p = Pedido(
            usuario_id=usuario_id,
            client_name=client_name,
            order_type=order_type,
            table_number=table_number,
            estado='pendiente',
            fecha_hora=datetime.utcnow()
        )
        db.session.add(p)
        db.session.flush()  # para obtener p.id

        total = 0
        for codigo, cantidad in items:
            dp = DetallePedido(
                pedido_id=p.id,
                producto_id=codigo,
                cantidad=cantidad,
                precio_unitario=Inventario.query.filter_by(producto_id=codigo).first().producto.precio
            )
            db.session.add(dp)
            inv = Inventario.query.filter_by(producto_id=codigo).first()
            inv.stock -= cantidad
            total += dp.precio_unitario * cantidad

        p.total = total
        db.session.commit()

        # Generar ticket
        t = TicketPago(pedido_id=p.id, monto_total=total, estado_pago='pendiente')
        db.session.add(t)
        db.session.commit()

        # Log
        log = LogTransaccion(
            pedido_id=p.id,
            accion="Pedido creado",
            detalle=f"Total={total}",
            fecha_hora=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()

        return p.id
