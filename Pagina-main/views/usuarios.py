from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import psycopg2
from psycopg2 import sql

usuarios_bp = Blueprint('usuarios', __name__)

# Conexión a la base de datos
def get_db_connection():
    conn = psycopg2.connect(
        host='localhost',
        database='finanzas_personales',
        user='postgres',
        password='12345678'
    )
    conn.set_client_encoding('UTF8')
    return conn

@usuarios_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
            user_exists = cursor.fetchone()
            if user_exists:
                flash('El correo electrónico ya está registrado.', 'error')
                return redirect(url_for('usuarios.registro'))

            cursor.execute("""
                INSERT INTO usuarios (nombre, email, password)
                VALUES (%s, %s, %s)
            """, (nombre, email, password))

            conn.commit()
            cursor.close()
            conn.close()

            flash('Usuario registrado con éxito', 'success')
            return redirect(url_for('usuarios.login'))  # Redirigir al login después del registro

        except Exception as e:
            flash(f'Ocurrió un error al registrar el usuario: {e}', 'error')
            return redirect(url_for('usuarios.registro'))

    return render_template('registro.html')  # Asegúrate de tener un archivo 'registro.html' para la vista de registro



@usuarios_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM usuarios WHERE email = %s AND password = %s", (email, password))
            usuario = cursor.fetchone()

            cursor.close()
            conn.close()

            if usuario:
                session['usuario_id'] = usuario[0]  # ID del usuario
                session['usuario_nombre'] = usuario[1]  # Nombre del usuario
                flash('Inicio de sesión exitoso', 'success')
                return redirect(url_for('home'))  # Redirigir a la ruta 'home', no 'index'
            else:
                flash('Correo o contraseña incorrectos', 'error')
                return redirect(url_for('usuarios.login'))  # Redirigir a la página de login en caso de error

        except Exception as e:
            flash(f'Error al iniciar sesión: {e}', 'error')
            return redirect(url_for('usuarios.login'))  # En caso de error, redirigir a login

    return render_template('login.html')  # Si la solicitud es GET, mostrar el formulario de login




@usuarios_bp.route('/logout')
def logout():
    session.clear()  # Limpiar la sesión
    flash('Sesión cerrada exitosamente', 'info')
    return redirect(url_for('usuarios.login'))  # Redirigir al login después de cerrar sesión
