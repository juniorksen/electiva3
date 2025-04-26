from flask import Flask, render_template
from views.usuarios import usuarios_bp
from views.transacciones import transacciones_bp
from auth_utils import login_required

app = Flask(__name__)
app.secret_key = 'clave-super-secreta'

# Registrar blueprints
app.register_blueprint(usuarios_bp, url_prefix='/usuarios')
app.register_blueprint(transacciones_bp, url_prefix='/transacciones')

@app.route('/')
@login_required
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
