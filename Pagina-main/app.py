from flask import Flask, render_template
from views.usuarios import usuarios_bp

app = Flask(__name__)
app.secret_key = 'clave-super-secreta'  # Necesaria para mensajes flash, sesiones, etc.

# Ruta para la raíz "/"
@app.route('/')
def home():
    return render_template('index.html')  # Asegúrate de que 'index.html' exista en la carpeta 'templates'

# Registrar blueprint de usuarios
app.register_blueprint(usuarios_bp, url_prefix='/usuarios')

if __name__ == '__main__':
    app.run(debug=True)
