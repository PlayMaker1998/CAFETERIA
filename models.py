from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin
from datetime import datetime

bcrypt = Bcrypt()
db = SQLAlchemy()

class Usuario(db.Model, UserMixin):
    id             = db.Column(db.Integer, primary_key=True)
    first_name     = db.Column(db.String(100), nullable=False)
    last_name      = db.Column(db.String(100), nullable=False)
    dni            = db.Column(db.String(20), nullable=False)
    email          = db.Column(db.String(120), unique=True, index=True, nullable=False)
    password       = db.Column(db.String(200), nullable=False)
    rol            = db.Column(db.String(20), default='cliente')  # 'cliente','mesero','cocinero','admin'
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, raw):
        self.password = bcrypt.generate_password_hash(raw).decode()

    def check_password(self, raw):
        return bcrypt.check_password_hash(self.password, raw)

class Producto(db.Model):
    codigo      = db.Column(db.String(10), primary_key=True)
    nombre      = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(200))
    precio      = db.Column(db.Float, nullable=False)
    categoria   = db.Column(db.String(50))
    imagen_url  = db.Column(db.String(200))

class Inventario(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.String(10), db.ForeignKey('producto.codigo'), nullable=False)
    stock       = db.Column(db.Integer, default=0)
    unidad      = db.Column(db.String(20))
    producto    = db.relationship("Producto", backref="inventario")

class Pedido(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    usuario_id    = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False, index=True)
    client_name   = db.Column(db.String(200), nullable=False)
    order_type    = db.Column(db.String(20), nullable=False)  # 'para_llevar'|'comer_aqui'
    table_number  = db.Column(db.Integer, nullable=True)
    estado        = db.Column(db.String(30), default='pendiente')  # 'pendiente','en preparación','preparado','entregado'
    fecha_hora    = db.Column(db.DateTime, default=datetime.utcnow)
    total         = db.Column(db.Float, default=0.0)
    usuario       = db.relationship("Usuario", backref="pedidos")

class DetallePedido(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    pedido_id       = db.Column(db.Integer, db.ForeignKey('pedido.id'), nullable=False, index=True)
    producto_id     = db.Column(db.String(10), db.ForeignKey('producto.codigo'), nullable=False)
    cantidad        = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    preparado       = db.Column(db.Boolean, default=False)
    entregado       = db.Column(db.Boolean, default=False)
    pedido          = db.relationship("Pedido", backref="detalles")
    producto        = db.relationship("Producto", backref="detalle_pedido")

class TicketPago(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    pedido_id     = db.Column(db.Integer, db.ForeignKey('pedido.id'), index=True)
    fecha_emision = db.Column(db.DateTime, default=datetime.utcnow)
    monto_total   = db.Column(db.Float, nullable=False)
    estado_pago   = db.Column(db.String(20), default='pendiente')
    pedido        = db.relationship("Pedido", backref="ticket_pago")

class BoletaPago(db.Model):
    id             = db.Column(db.Integer, primary_key=True)
    ticket_pago_id = db.Column(db.Integer, db.ForeignKey('ticket_pago.id'), nullable=False)
    fecha_emision  = db.Column(db.DateTime, default=datetime.utcnow)
    detalles       = db.Column(db.Text)
    metodo_pago    = db.Column(db.String(30))  # 'efectivo'|'tarjeta'
    ticket         = db.relationship("TicketPago", backref="boleta_pago")

class LogTransaccion(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    pedido_id  = db.Column(db.Integer, db.ForeignKey('pedido.id'), index=True)
    accion     = db.Column(db.String(100))
    fecha_hora = db.Column(db.DateTime, default=datetime.utcnow)
    detalle    = db.Column(db.Text)