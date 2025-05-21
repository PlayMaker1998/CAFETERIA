from flask import Flask
from extensions import cache
from config import Config
from models import db, bcrypt, Usuario
from routes import cliente, mesero, cocina, admin
from flask import Flask, render_template
from flask_login import LoginManager
from flask import redirect, url_for, session, flash


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'cliente.login'

app.config['CACHE_TYPE'] = 'SimpleCache'
cache.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


# Registro de Blueprints
app.register_blueprint(cliente.bp)
app.register_blueprint(mesero.bp, url_prefix='/mesero')
app.register_blueprint(cocina.bp, url_prefix='/cocina')
app.register_blueprint(admin.bp, url_prefix='/admin')

@app.route('/logout')
def logout():
    session.clear()  # o session.pop('usuario_id', None)
    flash("Sesión cerrada correctamente", "success")
    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=False)

