# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Usuario: Se solicitan nombres, apellidos y DNI.
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    dni = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # En producción, usar hash
    rol = db.Column(db.String(20), default='cliente')       # 'cliente', 'mesero', 'cocinero', 'admin'
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

# Producto del menú
class Producto(db.Model):
    codigo = db.Column(db.String(10), primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(200))
    precio = db.Column(db.Float, nullable=False)
    categoria = db.Column(db.String(50))
    imagen_url = db.Column(db.String(200))

# Inventario
class Inventario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.String(10), db.ForeignKey('producto.codigo'), nullable=False)
    stock = db.Column(db.Integer, default=0)
    unidad = db.Column(db.String(20))
    producto = db.relationship("Producto", backref="inventario")

# Pedido (Order)  
class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    client_name = db.Column(db.String(200), nullable=False)   # Nombre completo del cliente
    order_type = db.Column(db.String(20), nullable=False)       # "para_llevar" o "comer_aqui"
    table_number = db.Column(db.Integer, nullable=True)         # Sólo si es "comer_aqui"
    estado = db.Column(db.String(30), default='pendiente')        # 'pendiente', 'en preparación', 'preparado', 'entregado'
    fecha_hora = db.Column(db.DateTime, default=datetime.utcnow)
    total = db.Column(db.Float, default=0.0)
    usuario = db.relationship("Usuario", backref="pedidos")

# Detalle del pedido (Order Details)
class DetallePedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedido.id'), nullable=False)
    producto_id = db.Column(db.String(10), db.ForeignKey('producto.codigo'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    preparado = db.Column(db.Boolean, default=False)    # Marcado por el cocinero
    entregado = db.Column(db.Boolean, default=False)    # Marcado por el mesero
    pedido = db.relationship("Pedido", backref="detalles")
    producto = db.relationship("Producto", backref="detalle_pedido")

# Ticket de Pago
class TicketPago(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedido.id'), nullable=False)
    fecha_emision = db.Column(db.DateTime, default=datetime.utcnow)
    monto_total = db.Column(db.Float, nullable=False)
    estado_pago = db.Column(db.String(20), default='pendiente')  # 'pendiente', 'pagado'
    pedido = db.relationship("Pedido", backref="ticket_pago")

# Boleta de Pago
class BoletaPago(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_pago_id = db.Column(db.Integer, db.ForeignKey('ticket_pago.id'), nullable=False)
    fecha_emision = db.Column(db.DateTime, default=datetime.utcnow)
    detalles = db.Column(db.Text)   # Detalle (por ejemplo, JSON con productos entregados)
    metodo_pago = db.Column(db.String(30))  # 'efectivo', 'tarjeta', 'online'
    ticket = db.relationship("TicketPago", backref="boleta_pago")

# Log de transacciones (auditoría)
class LogTransaccion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedido.id'))
    accion = db.Column(db.String(100))
    fecha_hora = db.Column(db.DateTime, default=datetime.utcnow)
    detalle = db.Column(db.Text)
