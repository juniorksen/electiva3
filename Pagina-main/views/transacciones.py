from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import psycopg2
from psycopg2 import sql
from datetime import datetime, date

transacciones_bp = Blueprint('transacciones', __name__)


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

@transacciones_bp.route('/dashboard')

def dashboard():
    # Verificar si el usuario está logueado
    if 'usuario_id' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('usuarios.login'))
    
    usuario_id = session['usuario_id']
    
    # Obtener datos de usuario y resumen financiero
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Obtener información del usuario
    cursor.execute("SELECT nombre, saldo_actual FROM usuarios WHERE id_usuario = %s", (usuario_id,))
    usuario = cursor.fetchone()
    nombre_usuario = usuario[0]
    saldo_actual = usuario[1]
    
    # Obtener total de ingresos del mes actual
    mes_actual = datetime.now().month
    año_actual = datetime.now().year
    cursor.execute("""
        SELECT COALESCE(SUM(monto), 0)
        FROM ingresos
        WHERE id_usuario = %s AND EXTRACT(MONTH FROM fecha) = %s AND EXTRACT(YEAR FROM fecha) = %s
    """, (usuario_id, mes_actual, año_actual))
    total_ingresos_mes = cursor.fetchone()[0]
    
    # Obtener total de gastos del mes actual
    cursor.execute("""
        SELECT COALESCE(SUM(monto), 0)
        FROM gastos
        WHERE id_usuario = %s AND EXTRACT(MONTH FROM fecha) = %s AND EXTRACT(YEAR FROM fecha) = %s
    """, (usuario_id, mes_actual, año_actual))
    total_gastos_mes = cursor.fetchone()[0]
    
    # Obtener gastos por categoría del mes actual
    cursor.execute("""
        SELECT c.nombre, COALESCE(SUM(g.monto), 0) as total
        FROM categorias c
        LEFT JOIN gastos g ON c.id_categoria = g.id_categoria 
            AND g.id_usuario = %s 
            AND EXTRACT(MONTH FROM g.fecha) = %s 
            AND EXTRACT(YEAR FROM g.fecha) = %s
        GROUP BY c.nombre
        ORDER BY total DESC
    """, (usuario_id, mes_actual, año_actual))
    gastos_por_categoria = cursor.fetchall()
    
    # Obtener gastos fijos activos
    cursor.execute("""
        SELECT gf.descripcion, gf.monto, c.nombre as categoria, gf.dia_mes_pago
        FROM gastos_fijos gf
        JOIN categorias c ON gf.id_categoria = c.id_categoria
        WHERE gf.id_usuario = %s AND gf.activo = TRUE
        ORDER BY gf.dia_mes_pago
    """, (usuario_id,))
    gastos_fijos = cursor.fetchall()
    
    # Obtener últimos movimientos (ingresos y gastos)
    cursor.execute("""
        (SELECT 'ingreso' as tipo, i.monto, i.descripcion, i.fecha, NULL as categoria
         FROM ingresos i 
         WHERE i.id_usuario = %s)
        UNION ALL
        (SELECT 'gasto' as tipo, g.monto, g.descripcion, g.fecha, c.nombre as categoria
         FROM gastos g
         JOIN categorias c ON g.id_categoria = c.id_categoria
         WHERE g.id_usuario = %s)
        ORDER BY fecha DESC
        LIMIT 10
    """, (usuario_id, usuario_id))
    ultimos_movimientos = cursor.fetchall()
    
    # Obtener todas las categorías para los formularios
    cursor.execute("SELECT id_categoria, nombre FROM categorias ORDER BY nombre")
    categorias = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template(
        'dashboard.html',
        nombre_usuario=nombre_usuario,
        saldo_actual=saldo_actual,
        total_ingresos_mes=total_ingresos_mes,
        total_gastos_mes=total_gastos_mes,
        gastos_por_categoria=gastos_por_categoria,
        gastos_fijos=gastos_fijos,
        ultimos_movimientos=ultimos_movimientos,
        categorias=categorias,
        fecha_actual=date.today().strftime('%Y-%m-%d')
    )

@transacciones_bp.route('/ingresos')
def listar_ingresos():
    # Verificar si el usuario está logueado
    if 'usuario_id' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('usuarios.login'))
    
    usuario_id = session['usuario_id']
    
    # Parámetros de filtro
    fecha_desde = request.args.get('fecha_desde', '')
    fecha_hasta = request.args.get('fecha_hasta', '')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Consulta base
    query = """
        SELECT id_ingreso, monto, descripcion, fecha, fecha_registro
        FROM ingresos
        WHERE id_usuario = %s
    """
    params = [usuario_id]
    
    # Agregar filtros
    if fecha_desde:
        query += " AND fecha >= %s"
        params.append(fecha_desde)
    
    if fecha_hasta:
        query += " AND fecha <= %s"
        params.append(fecha_hasta)
    
    query += " ORDER BY fecha DESC"
    
    cursor.execute(query, params)
    ingresos = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template(
        'ingresos.html',
        ingresos=ingresos,
        filtros={
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta
        }
    )

@transacciones_bp.route('/gastos')
def listar_gastos():
    # Verificar si el usuario está logueado
    if 'usuario_id' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('usuarios.login'))
    
    usuario_id = session['usuario_id']
    
    # Parámetros de filtro
    categoria_id = request.args.get('categoria_id', '')
    fecha_desde = request.args.get('fecha_desde', '')
    fecha_hasta = request.args.get('fecha_hasta', '')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Consulta base
    query = """
        SELECT g.id_gasto, g.monto, g.descripcion, g.fecha, c.nombre as categoria
        FROM gastos g
        JOIN categorias c ON g.id_categoria = c.id_categoria
        WHERE g.id_usuario = %s
    """
    params = [usuario_id]
    
    # Agregar filtros
    if categoria_id:
        query += " AND g.id_categoria = %s"
        params.append(categoria_id)
    
    if fecha_desde:
        query += " AND g.fecha >= %s"
        params.append(fecha_desde)
    
    if fecha_hasta:
        query += " AND g.fecha <= %s"
        params.append(fecha_hasta)
    
    query += " ORDER BY g.fecha DESC"
    
    cursor.execute(query, params)
    gastos = cursor.fetchall()
    
    # Obtener categorías para el filtro
    cursor.execute("SELECT id_categoria, nombre FROM categorias ORDER BY nombre")
    categorias = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template(
        'gastos.html',
        gastos=gastos,
        categorias=categorias,
        filtros={
            'categoria_id': categoria_id,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta
        }
    )

@transacciones_bp.route('/ingresos/agregar', methods=['POST'])
def agregar_ingreso():
    # Verificar si el usuario está logueado
    if 'usuario_id' not in session:
        flash('Debes iniciar sesión para realizar esta acción', 'error')
        return redirect(url_for('usuarios.login'))
    
    try:
        usuario_id = session['usuario_id']
        monto = float(request.form['monto'])
        descripcion = request.form['descripcion']
        fecha = request.form.get('fecha', date.today().strftime('%Y-%m-%d'))
        
        # Validaciones básicas
        if monto <= 0:
            flash('El monto debe ser mayor a cero', 'error')
            return redirect(url_for('transacciones.dashboard'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO ingresos (id_usuario, monto, descripcion, fecha)
            VALUES (%s, %s, %s, %s)
        """, (usuario_id, monto, descripcion, fecha))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Ingreso registrado correctamente', 'success')
    except Exception as e:
        flash(f'Error al registrar el ingreso: {e}', 'error')
    
    return redirect(url_for('transacciones.dashboard'))

@transacciones_bp.route('/gastos/agregar', methods=['POST'])
def agregar_gasto():
    # Verificar si el usuario está logueado
    if 'usuario_id' not in session:
        flash('Debes iniciar sesión para realizar esta acción', 'error')
        return redirect(url_for('usuarios.login'))
    
    try:
        usuario_id = session['usuario_id']
        monto = float(request.form['monto'])
        descripcion = request.form['descripcion']
        categoria_id = int(request.form['categoria_id'])
        fecha = request.form.get('fecha', date.today().strftime('%Y-%m-%d'))
        
        # Validaciones básicas
        if monto <= 0:
            flash('El monto debe ser mayor a cero', 'error')
            return redirect(url_for('transacciones.dashboard'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO gastos (id_usuario, id_categoria, monto, descripcion, fecha)
            VALUES (%s, %s, %s, %s, %s)
        """, (usuario_id, categoria_id, monto, descripcion, fecha))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Gasto registrado correctamente', 'success')
    except Exception as e:
        flash(f'Error al registrar el gasto: {e}', 'error')
    
    return redirect(url_for('transacciones.dashboard'))

@transacciones_bp.route('/ingresos/editar/<int:id>', methods=['GET', 'POST'])
def editar_ingreso(id):
    # Verificar si el usuario está logueado
    if 'usuario_id' not in session:
        flash('Debes iniciar sesión para realizar esta acción', 'error')
        return redirect(url_for('usuarios.login'))
    
    usuario_id = session['usuario_id']
    
    if request.method == 'POST':
        try:
            monto = float(request.form['monto'])
            descripcion = request.form['descripcion']
            fecha = request.form['fecha']
            
            # Validaciones básicas
            if monto <= 0:
                flash('El monto debe ser mayor a cero', 'error')
                return redirect(url_for('finanzas.editar_ingreso', id=id))
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Verificar que el ingreso pertenezca al usuario antes de actualizar
            cursor.execute("SELECT id_usuario FROM ingresos WHERE id_ingreso = %s", (id,))
            ingreso = cursor.fetchone()
            
            if not ingreso or ingreso[0] != usuario_id:
                flash('No tienes permiso para editar este ingreso', 'error')
                return redirect(url_for('finanzas.listar_ingresos'))
            
            # Obtener el monto anterior para ajustar el saldo
            cursor.execute("SELECT monto FROM ingresos WHERE id_ingreso = %s", (id,))
            monto_anterior = cursor.fetchone()[0]
            
            # Actualizar el ingreso
            cursor.execute("""
                UPDATE ingresos
                SET monto = %s, descripcion = %s, fecha = %s
                WHERE id_ingreso = %s AND id_usuario = %s
            """, (monto, descripcion, fecha, id, usuario_id))
            
            # Ajustar el saldo del usuario
            cursor.execute("""
                UPDATE usuarios
                SET saldo_actual = saldo_actual - %s + %s
                WHERE id_usuario = %s
            """, (monto_anterior, monto, usuario_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Ingreso actualizado correctamente', 'success')
            return redirect(url_for('finanzas.listar_ingresos'))
        
        except Exception as e:
            flash(f'Error al actualizar el ingreso: {e}', 'error')
            return redirect(url_for('finanzas.editar_ingreso', id=id))
    
    else:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id_ingreso, monto, descripcion, fecha
            FROM ingresos
            WHERE id_ingreso = %s AND id_usuario = %s
        """, (id, usuario_id))
        
        ingreso = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not ingreso:
            flash('Ingreso no encontrado', 'error')
            return redirect(url_for('finanzas.listar_ingresos'))
        
        return render_template('editar_ingreso.html', ingreso=ingreso)

@transacciones_bp.route('/gastos/editar/<int:id>', methods=['GET', 'POST'])
def editar_gasto(id):
    if 'usuario_id' not in session:
        flash('Debes iniciar sesión para realizar esta acción', 'error')
        return redirect(url_for('usuarios.login'))

    usuario_id = session['usuario_id']

    if request.method == 'POST':
        try:
            monto = float(request.form['monto'])
            descripcion = request.form['descripcion']
            categoria_id = int(request.form['categoria_id'])
            fecha = request.form['fecha']

            if monto <= 0:
                flash('El monto debe ser mayor a cero', 'error')
                return redirect(url_for('finanzas.editar_gasto', id=id))

            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT id_usuario FROM gastos WHERE id_gasto = %s", (id,))
            gasto = cursor.fetchone()

            if not gasto or gasto[0] != usuario_id:
                flash('No tienes permiso para editar este gasto', 'error')
                return redirect(url_for('finanzas.listar_gastos'))

            cursor.execute("SELECT monto FROM gastos WHERE id_gasto = %s", (id,))
            monto_anterior = cursor.fetchone()[0]

            cursor.execute("""
                UPDATE gastos
                SET monto = %s, id_categoria = %s, descripcion = %s, fecha = %s
                WHERE id_gasto = %s AND id_usuario = %s
            """, (monto, categoria_id, descripcion, fecha, id, usuario_id))

            cursor.execute("""
                UPDATE usuarios
                SET saldo_actual = saldo_actual + %s - %s
                WHERE id_usuario = %s
            """, (monto_anterior, monto, usuario_id))

            conn.commit()
            cursor.close()
            conn.close()

            flash('Gasto actualizado correctamente', 'success')
            return redirect(url_for('finanzas.listar_gastos'))

        except Exception as e:
            flash(f'Error al actualizar el gasto: {e}', 'error')
            return redirect(url_for('finanzas.editar_gasto', id=id))

    else:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id_gasto, monto, descripcion, id_categoria, fecha
            FROM gastos
            WHERE id_gasto = %s AND id_usuario = %s
        """, (id, usuario_id))
        gasto = cursor.fetchone()

        cursor.execute("SELECT id_categoria, nombre FROM categorias ORDER BY nombre")
        categorias = cursor.fetchall()

        cursor.close()
        conn.close()

        if not gasto:
            flash('Gasto no encontrado', 'error')
            return redirect(url_for('finanzas.listar_gastos'))

        return render_template('editar_gasto.html', gasto=gasto, categorias=categorias)
