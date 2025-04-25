from flask import Flask
from config import Config
from models import db
from routes import cliente, mesero, cocina, admin
from flask import Flask, render_template

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# Registro de Blueprints
app.register_blueprint(cliente.bp)
app.register_blueprint(mesero.bp, url_prefix='/mesero')
app.register_blueprint(cocina.bp, url_prefix='/cocina')
app.register_blueprint(admin.bp, url_prefix='/admin')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
