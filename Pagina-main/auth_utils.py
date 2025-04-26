from flask import session, redirect, url_for, flash
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:  # <-- aquí el cambio
            flash('Debes iniciar sesión para acceder a esta página.', 'error')
            return redirect(url_for('usuarios.login'))
        return f(*args, **kwargs)
    return decorated_function