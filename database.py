"""
Módulo de gestión de base de datos SQLite
Maneja todas las operaciones CRUD de la aplicación
"""

import sqlite3
from datetime import datetime, timedelta
import os


class DatabaseManager:
    """Gestor centralizado de la base de datos"""
    
    def __init__(self, db_name='agromanager.db'):
        self.db_name = db_name
        self.conn = None
    
    def get_connection(self):
        """Obtener conexión a la base de datos"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_name)
            self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def close(self):
        """Cerrar conexión"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def init_db(self):
        """Inicializar todas las tablas"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabla de cheques
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cheques (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero TEXT NOT NULL,
                banco TEXT NOT NULL,
                monto REAL NOT NULL,
                fecha_vencimiento TEXT NOT NULL,
                estado TEXT DEFAULT 'pendiente',
                fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de proveedores
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS proveedores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                rubro TEXT,
                cuit TEXT,
                telefono TEXT,
                email TEXT,
                direccion TEXT,
                fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de facturas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS facturas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proveedor_id INTEGER,
                numero TEXT NOT NULL,
                monto REAL NOT NULL,
                fecha TEXT NOT NULL,
                descripcion TEXT,
                FOREIGN KEY (proveedor_id) REFERENCES proveedores(id)
            )
        ''')
        
        # Tabla de gastos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gastos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                categoria TEXT NOT NULL,
                concepto TEXT NOT NULL,
                monto REAL NOT NULL,
                fecha TEXT NOT NULL,
                descripcion TEXT
            )
        ''')
        
        # Tabla de ingresos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ingresos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                categoria TEXT NOT NULL,
                concepto TEXT NOT NULL,
                monto REAL NOT NULL,
                fecha TEXT NOT NULL,
                descripcion TEXT
            )
        ''')
        
        # Tabla de superficie
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS superficie (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cultivo TEXT NOT NULL,
                hectareas REAL NOT NULL,
                fecha_siembra TEXT,
                fecha_cosecha TEXT
            )
        ''')
        
        # Tabla de ganado
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ganado (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL,
                cantidad INTEGER NOT NULL,
                categoria TEXT,
                fecha_registro TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de tambo
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tambo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                litros_producidos REAL,
                porcentaje_prenez REAL,
                porcentaje_paricion REAL,
                porcentaje_destete REAL,
                vacas_lactancia INTEGER,
                observaciones TEXT
            )
        ''')
        
        # Tabla de márgenes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS margenes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL,
                cultivo_producto TEXT NOT NULL,
                hectareas_cantidad REAL,
                costo_total REAL,
                ingreso_total REAL,
                margen REAL,
                fecha TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        
        # Cargar datos de ejemplo si es la primera vez
        self.load_sample_data()
    
    def load_sample_data(self):
        """Cargar datos de ejemplo para testing"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Verificar si ya hay datos
        cursor.execute("SELECT COUNT(*) FROM cheques")
        if cursor.fetchone()[0] == 0:
            # Insertar cheques de ejemplo
            hoy = datetime.now()
            cheques_ejemplo = [
                ('001234', 'Banco Nación', 500000, (hoy + timedelta(days=5)).strftime('%Y-%m-%d')),
                ('002345', 'Banco Provincia', 750000, (hoy + timedelta(days=15)).strftime('%Y-%m-%d')),
                ('003456', 'Banco Galicia', 300000, (hoy + timedelta(days=30)).strftime('%Y-%m-%d')),
            ]
            cursor.executemany(
                'INSERT INTO cheques (numero, banco, monto, fecha_vencimiento) VALUES (?, ?, ?, ?)',
                cheques_ejemplo
            )
            
            # Insertar proveedores de ejemplo
            proveedores_ejemplo = [
                ('Semillas del Campo S.A.', 'Insumos Agrícolas', '20-12345678-9', '11-4444-5555', 'ventas@semillas.com', 'Av. Rural 123'),
                ('Agroquímicos del Sur', 'Agroquímicos', '30-87654321-2', '11-5555-6666', 'info@agrosur.com', 'Ruta 9 Km 45'),
                ('Ferretería Rural', 'Herramientas', '27-11223344-5', '11-6666-7777', 'ferreteria@rural.com', 'Calle Principal 567'),
            ]
            cursor.executemany(
                'INSERT INTO proveedores (nombre, rubro, cuit, telefono, email, direccion) VALUES (?, ?, ?, ?, ?, ?)',
                proveedores_ejemplo
            )
            
            # Insertar gastos de ejemplo
            gastos_ejemplo = [
                ('agro', 'Semillas de soja', 800000, (hoy - timedelta(days=10)).strftime('%Y-%m-%d'), 'Compra de semillas'),
                ('ganadería', 'Alimento balanceado', 450000, (hoy - timedelta(days=5)).strftime('%Y-%m-%d'), 'Para ganado'),
                ('otros', 'Combustible', 120000, (hoy - timedelta(days=2)).strftime('%Y-%m-%d'), 'Gasoil para maquinaria'),
            ]
            cursor.executemany(
                'INSERT INTO gastos (categoria, concepto, monto, fecha, descripcion) VALUES (?, ?, ?, ?, ?)',
                gastos_ejemplo
            )
            
            # Insertar ingresos de ejemplo
            ingresos_ejemplo = [
                ('agro', 'Venta de trigo', 2500000, (hoy - timedelta(days=20)).strftime('%Y-%m-%d'), 'Cosecha 2024'),
                ('ganadería', 'Venta de novillos', 1800000, (hoy - timedelta(days=15)).strftime('%Y-%m-%d'), '50 cabezas'),
                ('otros', 'Arriendo', 300000, (hoy - timedelta(days=30)).strftime('%Y-%m-%d'), 'Lote 5'),
            ]
            cursor.executemany(
                'INSERT INTO ingresos (categoria, concepto, monto, fecha, descripcion) VALUES (?, ?, ?, ?, ?)',
                ingresos_ejemplo
            )
            
            # Insertar superficie de ejemplo
            superficie_ejemplo = [
                ('Soja', 150, '2024-10-15', '2025-04-15'),
                ('Trigo', 100, '2024-06-01', '2024-12-01'),
                ('Maíz', 80, '2024-09-01', '2025-03-01'),
            ]
            cursor.executemany(
                'INSERT INTO superficie (cultivo, hectareas, fecha_siembra, fecha_cosecha) VALUES (?, ?, ?, ?)',
                superficie_ejemplo
            )
            
            # Insertar datos de tambo
            tambo_ejemplo = [
                (hoy.strftime('%Y-%m-%d'), 5000, 85, 90, 88, 250, 'Producción normal'),
            ]
            cursor.executemany(
                'INSERT INTO tambo (fecha, litros_producidos, porcentaje_prenez, porcentaje_paricion, porcentaje_destete, vacas_lactancia, observaciones) VALUES (?, ?, ?, ?, ?, ?, ?)',
                tambo_ejemplo
            )
            
            conn.commit()
    
    # Métodos para el Dashboard
    def get_cheques_proximos(self, dias=7):
        """Obtener cheques que vencen en los próximos X días"""
        conn = self.get_connection()
        cursor = conn.cursor()
        fecha_limite = (datetime.now() + timedelta(days=dias)).strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT * FROM cheques 
            WHERE fecha_vencimiento <= ? AND estado = 'pendiente'
            ORDER BY fecha_vencimiento
        ''', (fecha_limite,))
        return cursor.fetchall()
    
    def get_total_gastos_mes(self):
        """Obtener total de gastos del mes actual"""
        conn = self.get_connection()
        cursor = conn.cursor()
        mes_actual = datetime.now().strftime('%Y-%m')
        cursor.execute('''
            SELECT COALESCE(SUM(monto), 0) FROM gastos 
            WHERE fecha LIKE ?
        ''', (mes_actual + '%',))
        return cursor.fetchone()[0]
    
    def get_total_ingresos_mes(self):
        """Obtener total de ingresos del mes actual"""
        conn = self.get_connection()
        cursor = conn.cursor()
        mes_actual = datetime.now().strftime('%Y-%m')
        cursor.execute('''
            SELECT COALESCE(SUM(monto), 0) FROM ingresos 
            WHERE fecha LIKE ?
        ''', (mes_actual + '%',))
        return cursor.fetchone()[0]
    
    def get_total_proveedores(self):
        """Obtener número total de proveedores"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM proveedores')
        return cursor.fetchone()[0]
    
    def get_superficie_total(self):
        """Obtener superficie total en hectáreas"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COALESCE(SUM(hectareas), 0) FROM superficie')
        return cursor.fetchone()[0]