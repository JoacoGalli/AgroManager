"""
Utilidades adicionales para AgroManager
Funciones de exportación, backup, etc.
"""

import csv
import sqlite3
from datetime import datetime
import os


class ExportUtils:
    """Utilidades para exportar datos"""
    
    @staticmethod
    def export_to_csv(db_path='agromanager.db', output_dir='exports'):
        """Exportar todas las tablas a archivos CSV"""
        
        # Crear directorio de exports si no existe
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Obtener lista de tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tablas = [row[0] for row in cursor.fetchall()]
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        archivos_creados = []
        
        for tabla in tablas:
            cursor.execute(f"SELECT * FROM {tabla}")
            rows = cursor.fetchall()
            
            if rows:
                # Obtener nombres de columnas
                columnas = rows[0].keys()
                
                # Crear archivo CSV
                filename = f"{output_dir}/{tabla}_{timestamp}.csv"
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=columnas)
                    writer.writeheader()
                    
                    for row in rows:
                        writer.writerow(dict(row))
                
                archivos_creados.append(filename)
                print(f"✅ Exportado: {filename}")
        
        conn.close()
        return archivos_creados
    
    @staticmethod
    def backup_database(db_path='agromanager.db', backup_dir='backups'):
        """Crear backup de la base de datos"""
        
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"{backup_dir}/agromanager_backup_{timestamp}.db"
        
        try:
            import shutil
            shutil.copy2(db_path, backup_file)
            print(f"✅ Backup creado: {backup_file}")
            return backup_file
        except Exception as e:
            print(f"❌ Error al crear backup: {e}")
            return None
    
    @staticmethod
    def generate_financial_report(db_path='agromanager.db'):
        """Generar reporte financiero resumido"""
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Resumen de ingresos
        cursor.execute('''
            SELECT 
                categoria,
                COUNT(*) as cantidad,
                SUM(monto) as total,
                AVG(monto) as promedio
            FROM ingresos
            GROUP BY categoria
        ''')
        ingresos = cursor.fetchall()
        
        # Resumen de gastos
        cursor.execute('''
            SELECT 
                categoria,
                COUNT(*) as cantidad,
                SUM(monto) as total,
                AVG(monto) as promedio
            FROM gastos
            GROUP BY categoria
        ''')
        gastos = cursor.fetchall()
        
        # Totales
        cursor.execute('SELECT SUM(monto) FROM ingresos')
        total_ingresos = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT SUM(monto) FROM gastos')
        total_gastos = cursor.fetchone()[0] or 0
        
        balance = total_ingresos - total_gastos
        
        # Generar reporte
        report = []
        report.append("=" * 60)
        report.append("REPORTE FINANCIERO - AgroManager")
        report.append(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        report.append("=" * 60)
        report.append("")
        
        report.append("INGRESOS POR CATEGORÍA:")
        report.append("-" * 60)
        for ing in ingresos:
            report.append(f"  {ing['categoria'].title():<15} | Cant: {ing['cantidad']:>3} | "
                         f"Total: ${ing['total']:>12,.2f} | Prom: ${ing['promedio']:>10,.2f}")
        report.append("")
        
        report.append("GASTOS POR CATEGORÍA:")
        report.append("-" * 60)
        for gasto in gastos:
            report.append(f"  {gasto['categoria'].title():<15} | Cant: {gasto['cantidad']:>3} | "
                         f"Total: ${gasto['total']:>12,.2f} | Prom: ${gasto['promedio']:>10,.2f}")
        report.append("")
        
        report.append("RESUMEN GENERAL:")
        report.append("-" * 60)
        report.append(f"  Total Ingresos:  ${total_ingresos:>15,.2f}")
        report.append(f"  Total Gastos:    ${total_gastos:>15,.2f}")
        report.append(f"  Balance:         ${balance:>15,.2f}")
        report.append("")
        
        rentabilidad = (balance / total_ingresos * 100) if total_ingresos > 0 else 0
        report.append(f"  Rentabilidad:    {rentabilidad:>15.2f}%")
        report.append("=" * 60)
        
        conn.close()
        
        # Guardar reporte
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"reportes/reporte_financiero_{timestamp}.txt"
        
        if not os.path.exists('reportes'):
            os.makedirs('reportes')
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
        
        print(f"✅ Reporte generado: {report_file}")
        print('\n'.join(report))
        
        return report_file


class DataCleaner:
    """Utilidades para limpiar datos antiguos"""
    
    @staticmethod
    def delete_old_records(db_path='agromanager.db', days=365):
        """Eliminar registros antiguos (más de X días)"""
        from datetime import timedelta
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        fecha_limite = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        # Eliminar gastos antiguos
        cursor.execute('DELETE FROM gastos WHERE fecha < ?', (fecha_limite,))
        gastos_deleted = cursor.rowcount
        
        # Eliminar ingresos antiguos
        cursor.execute('DELETE FROM ingresos WHERE fecha < ?', (fecha_limite,))
        ingresos_deleted = cursor.rowcount
        
        # Eliminar registros de tambo antiguos
        cursor.execute('DELETE FROM tambo WHERE fecha < ?', (fecha_limite,))
        tambo_deleted = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        print(f"✅ Eliminados:")
        print(f"   - Gastos: {gastos_deleted}")
        print(f"   - Ingresos: {ingresos_deleted}")
        print(f"   - Registros tambo: {tambo_deleted}")
        
        return gastos_deleted + ingresos_deleted + tambo_deleted


# Función de prueba
if __name__ == '__main__':
    print("=== Utilidades AgroManager ===\n")
    
    print("1. Exportar a CSV")
    print("2. Crear backup")
    print("3. Generar reporte financiero")
    print("4. Limpiar registros antiguos")
    print("5. Salir")
    
    opcion = input("\nSelecciona una opción: ")
    
    if opcion == '1':
        archivos = ExportUtils.export_to_csv()
        print(f"\n✅ Se exportaron {len(archivos)} tablas")
    
    elif opcion == '2':
        backup = ExportUtils.backup_database()
        if backup:
            print(f"\n✅ Backup creado exitosamente")
    
    elif opcion == '3':
        ExportUtils.generate_financial_report()
    
    elif opcion == '4':
        dias = input("¿Eliminar registros más antiguos que cuántos días? (default: 365): ")
        dias = int(dias) if dias else 365
        
        confirmar = input(f"⚠️  ¿Confirmas eliminar registros de hace más de {dias} días? (s/N): ")
        if confirmar.lower() == 's':
            DataCleaner.delete_old_records(days=dias)
        else:
            print("Operación cancelada")
    
    else:
        print("Saliendo...")