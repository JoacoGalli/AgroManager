"""
Script de ejecución y verificación de AgroManager
Verifica dependencias antes de ejecutar la aplicación
"""

import os
import sys


def check_dependencies():
    """Verificar que todas las dependencias estén instaladas"""
    dependencies = {
        'kivy': 'Kivy',
        'kivymd': 'KivyMD',
        'matplotlib': 'Matplotlib',
        'requests': 'Requests',
        'sqlite3': 'SQLite3'
    }
    
    missing = []
    
    print("Verificando dependencias...")
    print("-" * 50)
    
    for module, name in dependencies.items():
        try:
            __import__(module)
            print(f"✅ {name:<20} OK")
        except ImportError:
            print(f"❌ {name:<20} FALTA")
            missing.append(name)
    
    print("-" * 50)
    
    if missing:
        print(f"\n❌ Faltan dependencias: {', '.join(missing)}")
        print("\nPara instalarlas, ejecuta:")
        print("  pip install -r requirements.txt")
        print("  garden install matplotlib")
        return False
    
    print("\n✅ Todas las dependencias están instaladas\n")
    return True


def check_files():
    """Verificar que todos los archivos necesarios existan"""
    required_files = [
        'main.py',
        'database.py',
        'cheques.py',
        'proveedores.py',
        'gastos.py',
        'ingresos.py',
        'margenes.py',
        'superficie.py',
        'mercado.py',
        'tambo.py'
    ]
    
    print("Verificando archivos del proyecto...")
    print("-" * 50)
    
    missing = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file:<20} OK")
        else:
            print(f"❌ {file:<20} FALTA")
            missing.append(file)
    
    print("-" * 50)
    
    if missing:
        print(f"\n❌ Faltan archivos: {', '.join(missing)}")
        return False
    
    print("\n✅ Todos los archivos están presentes\n")
    return True


def show_info():
    """Mostrar información de la aplicación"""
    print("\n" + "=" * 50)
    print("  🌾 AgroManager - Sistema de Gestión Agropecuaria")
    print("=" * 50)
    print("\nVersión: 1.0")
    print("Desarrollado con: Kivy + KivyMD")
    print("Base de datos: SQLite")
    print("\nMódulos incluidos:")
    print("  • Vencimientos de Cheques")
    print("  • Proveedores y Facturas")
    print("  • Gastos y Ingresos")
    print("  • Márgenes de Producción")
    print("  • Superficie y Stock")
    print("  • Precios de Mercado")
    print("  • Gestión de Tambo")
    print("\n" + "=" * 50 + "\n")


def run_app():
    """Ejecutar la aplicación principal"""
    try:
        from main import AgroManagerApp
        print("🚀 Iniciando AgroManager...\n")
        AgroManagerApp().run()
    except Exception as e:
        print(f"\n❌ Error al ejecutar la aplicación: {e}")
        print("\nVerifica que todos los módulos estén correctamente instalados.")
        sys.exit(1)


def main():
    """Función principal"""
    show_info()
    
    # Verificar dependencias
    if not check_dependencies():
        sys.exit(1)
    
    # Verificar archivos
    if not check_files():
        sys.exit(1)
    
    # Ejecutar aplicación
    print("Todo listo para ejecutar AgroManager\n")
    
    try:
        run_app()
    except KeyboardInterrupt:
        print("\n\n👋 Aplicación cerrada por el usuario")
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()