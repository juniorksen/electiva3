import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_finance_database():
    # Conexión a PostgreSQL con el usuario por defecto
    conn = psycopg2.connect(
        host="localhost",
        user="postgres",  # Usuario por defecto de pgAdmin
        password="12345678"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    conn.set_client_encoding('UTF8')  # Configuramos UTF-8 para esta conexión
    
    # Crear la base de datos
    cursor = conn.cursor()
    
    # Primero verificamos si la base de datos ya existe
    cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'finanzas_personales'")
    exists = cursor.fetchone()
    
    if not exists:
        cursor.execute("CREATE DATABASE finanzas_personales WITH ENCODING 'UTF8'")  # Especificamos UTF-8 para la BD
        print("Base de datos 'finanzas_personales' creada con éxito")
    else:
        print("La base de datos 'finanzas_personales' ya existe")
    
    cursor.close()
    conn.close()
    
    # Ahora nos conectamos a la base de datos creada para crear las tablas
    conn = psycopg2.connect(
        host="localhost",
        user="postgres",
        password="12345678",
        database="finanzas_personales"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    conn.set_client_encoding('UTF8')  # Configuramos UTF-8 para esta conexión también
    cursor = conn.cursor()
    
    # Crear tablas
    
    # Tabla usuarios
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id_usuario SERIAL PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        saldo_actual DECIMAL(12,2) DEFAULT 0,
        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    print("Tabla 'usuarios' creada con éxito")
    
    # Tabla categorias
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categorias (
        id_categoria SERIAL PRIMARY KEY,
        nombre VARCHAR(50) NOT NULL,
        descripcion TEXT,
        icono VARCHAR(50)
    )
    """)
    print("Tabla 'categorias' creada con éxito")
    
    # Insertar categorías predefinidas
    cursor.execute("SELECT COUNT(*) FROM categorias")
    if cursor.fetchone()[0] == 0:
        categorias = [
            ('Alimentación', 'Gastos relacionados con comida', 'food'),
            ('Transporte', 'Gastos de transporte público, gasolina, etc.', 'car'),
            ('Vivienda', 'Alquiler, hipoteca, servicios', 'home'),
            ('Entretenimiento', 'Cine, salidas, streaming', 'entertainment'),
            ('Salud', 'Medicamentos, consultas médicas', 'health'),
            ('Educación', 'Cursos, libros, material educativo', 'education'),
            ('Ropa', 'Vestimenta y accesorios', 'clothing'),
            ('Tecnología', 'Dispositivos electrónicos, software', 'tech'),
            ('Otros', 'Gastos sin categoría específica', 'misc')
        ]
        
        insert_query = "INSERT INTO categorias (nombre, descripcion, icono) VALUES (%s, %s, %s)"
        cursor.executemany(insert_query, categorias)
        print("Categorías predefinidas insertadas con éxito")
    
    # Tabla ingresos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ingresos (
        id_ingreso SERIAL PRIMARY KEY,
        id_usuario INTEGER REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
        monto DECIMAL(12,2) NOT NULL,
        descripcion VARCHAR(255),
        fecha DATE NOT NULL,
        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    print("Tabla 'ingresos' creada con éxito")
    
    # Tabla gastos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gastos (
        id_gasto SERIAL PRIMARY KEY,
        id_usuario INTEGER REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
        id_categoria INTEGER REFERENCES categorias(id_categoria),
        monto DECIMAL(12,2) NOT NULL,
        descripcion VARCHAR(255),
        fecha DATE NOT NULL,
        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    print("Tabla 'gastos' creada con éxito")
    
    # Tabla presupuestos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS presupuestos (
        id_presupuesto SERIAL PRIMARY KEY,
        id_usuario INTEGER REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
        id_categoria INTEGER REFERENCES categorias(id_categoria),
        monto_limite DECIMAL(12,2) NOT NULL,
        mes INTEGER NOT NULL CHECK (mes BETWEEN 1 AND 12),
        año INTEGER NOT NULL,
        UNIQUE (id_usuario, id_categoria, mes, año)
    )
    """)
    print("Tabla 'presupuestos' creada con éxito")
    
    # Tabla gastos_fijos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gastos_fijos (
        id_gasto_fijo SERIAL PRIMARY KEY,
        id_usuario INTEGER REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
        descripcion VARCHAR(255) NOT NULL,
        monto DECIMAL(12,2) NOT NULL,
        id_categoria INTEGER REFERENCES categorias(id_categoria),
        dia_mes_pago INTEGER CHECK (dia_mes_pago BETWEEN 1 AND 31),
        activo BOOLEAN DEFAULT TRUE
    )
    """)
    print("Tabla 'gastos_fijos' creada con éxito")
    
    # Tabla consultas_compras
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS consultas_compras (
        id_consulta SERIAL PRIMARY KEY,
        id_usuario INTEGER REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
        descripcion VARCHAR(255) NOT NULL,
        monto DECIMAL(12,2) NOT NULL,
        id_categoria INTEGER REFERENCES categorias(id_categoria),
        fecha_consulta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        recomendacion TEXT,
        razon TEXT,
        decision_usuario BOOLEAN,
        fecha_decision TIMESTAMP
    )
    """)
    print("Tabla 'consultas_compras' creada con éxito")
    
    # Tabla analisis_ia
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analisis_ia (
        id_analisis SERIAL PRIMARY KEY,
        id_usuario INTEGER REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
        fecha_analisis TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        mes INTEGER NOT NULL CHECK (mes BETWEEN 1 AND 12),
        año INTEGER NOT NULL,
        categoria_mayor_gasto INTEGER REFERENCES categorias(id_categoria),
        porcentaje_ahorro DECIMAL(5,2),
        recomendaciones TEXT,
        datos_analisis JSONB
    )
    """)
    print("Tabla 'analisis_ia' creada con éxito")
    
    # Tabla parametros_recomendacion
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS parametros_recomendacion (
        id_parametro SERIAL PRIMARY KEY,
        id_usuario INTEGER REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
        porcentaje_minimo_saldo DECIMAL(5,2) DEFAULT 10.00,
        prioridad_categorias JSONB,
        nivel_restrictivo INTEGER DEFAULT 5 CHECK (nivel_restrictivo BETWEEN 1 AND 10)
    )
    """)
    print("Tabla 'parametros_recomendacion' creada con éxito")
    
    # Crear índices
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_gastos_usuario_fecha ON gastos(id_usuario, fecha)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ingresos_usuario_fecha ON ingresos(id_usuario, fecha)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_gastos_categoria ON gastos(id_categoria)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_consultas_usuario ON consultas_compras(id_usuario)")
    print("Índices creados con éxito")
    
    # Crear vista saldo_usuario
    cursor.execute("""
    CREATE OR REPLACE VIEW vista_saldo_usuario AS
    SELECT 
        u.id_usuario,
        u.nombre,
        u.saldo_actual,
        COALESCE(SUM(gf.monto), 0) AS gastos_fijos_pendientes,
        u.saldo_actual - COALESCE(SUM(gf.monto), 0) AS saldo_proyectado
    FROM usuarios u
    LEFT JOIN gastos_fijos gf ON u.id_usuario = gf.id_usuario AND gf.activo = TRUE
    GROUP BY u.id_usuario, u.nombre, u.saldo_actual
    """)
    print("Vista 'vista_saldo_usuario' creada con éxito")
    
    # Crear función evaluar_compra
    cursor.execute("""
    CREATE OR REPLACE FUNCTION evaluar_compra(usuario_id INTEGER, monto DECIMAL, categoria_id INTEGER)
    RETURNS TABLE (
        recomendacion VARCHAR(50),
        razon TEXT,
        impacto_saldo DECIMAL(12,2)
    ) AS $$
    DECLARE
        saldo_disponible DECIMAL(12,2);
        gastos_pendientes DECIMAL(12,2);
        porcentaje_minimo DECIMAL(5,2);
        nivel_restriccion INTEGER;
    BEGIN
        -- Obtener saldo actual
        SELECT saldo_actual INTO saldo_disponible FROM usuarios WHERE id_usuario = usuario_id;
        
        -- Obtener gastos fijos pendientes
        SELECT COALESCE(SUM(monto), 0) INTO gastos_pendientes FROM gastos_fijos 
        WHERE id_usuario = usuario_id AND activo = TRUE;
        
        -- Obtener parámetros de recomendación
        SELECT porcentaje_minimo_saldo, nivel_restrictivo 
        INTO porcentaje_minimo, nivel_restriccion
        FROM parametros_recomendacion 
        WHERE id_usuario = usuario_id;
        
        -- Si no hay parámetros configurados, usar valores predeterminados
        IF porcentaje_minimo IS NULL THEN
            porcentaje_minimo := 10.0;
            nivel_restriccion := 5;
        END IF;
        
        -- Calcular impacto de la compra
        saldo_disponible := saldo_disponible - gastos_pendientes;
        
        -- Evaluar compra
        IF monto > saldo_disponible THEN
            RETURN QUERY SELECT 
                'No recomendado'::VARCHAR(50),
                'El costo excede tu saldo disponible después de gastos fijos.'::TEXT,
                saldo_disponible - monto;
        ELSIF (saldo_disponible - monto) < (saldo_disponible * porcentaje_minimo / 100) THEN
            RETURN QUERY SELECT 
                'No recomendado'::VARCHAR(50),
                'La compra te dejaría con menos del ' || porcentaje_minimo || '% de tu saldo disponible.'::TEXT,
                saldo_disponible - monto;
        ELSIF nivel_restriccion > 7 AND monto > (saldo_disponible * 0.2) THEN
            RETURN QUERY SELECT 
                'Reconsiderar'::VARCHAR(50),
                'La compra representa más del 20% de tu saldo disponible y tu nivel de restricción es alto.'::TEXT,
                saldo_disponible - monto;
        ELSE
            RETURN QUERY SELECT 
                'Recomendado'::VARCHAR(50),
                'La compra parece razonable considerando tu saldo actual y gastos pendientes.'::TEXT,
                saldo_disponible - monto;
        END IF;
    END;
    $$ LANGUAGE plpgsql;
    """)
    print("Función 'evaluar_compra' creada con éxito")
    
    # Crear trigger para actualizar saldo con ingresos
    cursor.execute("""
    CREATE OR REPLACE FUNCTION actualizar_saldo_ingreso()
    RETURNS TRIGGER AS $$

    BEGIN
        UPDATE usuarios
        SET saldo_actual = saldo_actual + NEW.monto
        WHERE id_usuario = NEW.id_usuario;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS trigger_actualizar_saldo_ingreso ON ingresos;

    CREATE TRIGGER trigger_actualizar_saldo_ingreso
    AFTER INSERT ON ingresos
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_saldo_ingreso();
    """)
    print("Trigger 'trigger_actualizar_saldo_ingreso' creado con éxito")
    
    # Crear trigger para actualizar saldo con gastos
    cursor.execute("""
    CREATE OR REPLACE FUNCTION actualizar_saldo_gasto()
    RETURNS TRIGGER AS $$

    BEGIN
        UPDATE usuarios
        SET saldo_actual = saldo_actual - NEW.monto
        WHERE id_usuario = NEW.id_usuario;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS trigger_actualizar_saldo_gasto ON gastos;

    CREATE TRIGGER trigger_actualizar_saldo_gasto
    AFTER INSERT ON gastos
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_saldo_gasto();
    """)
    print("Trigger 'trigger_actualizar_saldo_gasto' creado con éxito")
    
    cursor.close()
    conn.close()
    
    print("\nBase de datos financiera creada completamente con éxito!")

if __name__ == "__main__":
    try:
        create_finance_database()
    except Exception as e:
        print(f"Error al crear la base de datos: {e}")