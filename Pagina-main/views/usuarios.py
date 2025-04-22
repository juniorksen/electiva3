from flask import Blueprint, render_template, request, redirect, url_for, flash
import psycopg2
from psycopg2 import sql

usuarios_bp = Blueprint('usuarios', __name__)

# Conexión a la base de datos
def get_db_connection():
    conn = psycopg2.connect(
        host='localhost',
        database='finanzas_personales',  # Nombre correcto de tu base de datos
        user='postgres',                 # Usuario que usaste en el primer código
        password='12345678'              # Contraseña que usaste en el primer código
    )
    conn.set_client_encoding('UTF8')     # Establecer la codificación UTF-8
    return conn

@usuarios_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']  # Aquí deberías agregar la lógica de encriptación

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Verificar si el correo ya existe
            cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
            user_exists = cursor.fetchone()
            if user_exists:
                flash('El correo electrónico ya está registrado.', 'error')
                return redirect(url_for('usuarios.registro'))

            # Insertar el nuevo usuario
            cursor.execute("""
                INSERT INTO usuarios (nombre, email, password)
                VALUES (%s, %s, %s)
            """, (nombre, email, password))

            conn.commit()  # Confirmar los cambios en la base de datos

            cursor.close()
            conn.close()

            flash('Usuario registrado con éxito', 'success')
            return redirect(url_for('usuarios.registro'))  # Redirigir a la misma página o a otra

        except Exception as e:
            flash(f'Ocurrió un error al registrar el usuario: {e}', 'error')

            # En caso de error, redirige a la página de registro
            return redirect(url_for('usuarios.registro'))

    return render_template('registro.html')
