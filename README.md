# 🌾 AgroManager - Sistema de Gestión Agropecuaria

AgroManager es una aplicación móvil y de escritorio desarrollada con Kivy/KivyMD para centralizar la información económica y productiva de establecimientos agropecuarios.

## 📋 Características

### Módulos Implementados

1. **Vencimientos de Cheques** 
   - Registro de cheques con fecha, monto y banco
   - Alertas visuales según proximidad de vencimiento
   - Gestión de estado (pendiente/cobrado)

2. **Proveedores y Facturas**
   - Base de datos de proveedores con información completa
   - Asociación de facturas con proveedores

3. **Gastos**
   - Registro por categoría (agro, ganadería, otros)
   - Gráficos de distribución tipo torta
   - Historial completo de gastos

4. **Ingresos**
   - Registro categorizado de ingresos
   - Comparación visual con gastos
   - Análisis de balance financiero

5. **Márgenes de Producción**
   - Cálculo de márgenes por hectárea
   - Análisis de rentabilidad por categoría
   - Dashboard de indicadores clave

6. **Superficie y Stock**
   - Gestión de hectáreas por cultivo
   - Gráficos de distribución de superficie
   - Registro de stock ganadero

7. **Mercado**
   - Consulta de dólar blue en tiempo real (API)
   - Precios estimados de commodities
   - Actualización manual de valores

8. **Tambo**
   - Registro de producción diaria de leche
   - Métricas de preñez, parición y destete
   - Gráficos de evolución temporal

## 🚀 Instalación Local

### Requisitos Previos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar o descargar los archivos**
   ```bash
   mkdir AgroManager
   cd AgroManager
   ```

2. **Copiar todos los archivos Python** al directorio:
   - `main.py`
   - `database.py`
   - `cheques.py`
   - `proveedores.py`
   - `gastos.py`
   - `ingresos.py`
   - `margenes.py`
   - `superficie.py`
   - `mercado.py`
   - `tambo.py`

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Instalar matplotlib backend para Kivy**
   ```bash
   garden install matplotlib
   ```

5. **Ejecutar la aplicación**
   ```bash
   python main.py
   ```

## 📱 Compilar APK para Android

### Requisitos
- Linux (Ubuntu recomendado) o WSL2 en Windows
- Python 3.8+
- Buildozer instalado

### Pasos para Compilar

1. **Instalar Buildozer**
   ```bash
   pip install buildozer
   pip install cython
   ```

2. **Instalar dependencias del sistema (Ubuntu/Debian)**
   ```bash
   sudo apt update
   sudo apt install -y git zip unzip openjdk-11-jdk wget
   sudo apt install -y python3-pip autoconf libtool pkg-config zlib1g-dev
   sudo apt install -y libncurses5-dev libncursesw5-dev libtinfo5 cmake
   sudo apt install -y libffi-dev libssl-dev
   ```

3. **Preparar el proyecto**
   - Asegúrate de que todos los archivos .py estén en el mismo directorio
   - El archivo `buildozer.spec` debe estar en el directorio raíz

4. **Compilar el APK**
   ```bash
   buildozer android debug
   ```

5. **El APK estará en**
   ```
   ./bin/agromanager-1.0-arm64-v8a-debug.apk
   ```

6. **Transferir e instalar en Android**
   ```bash
   # Conectar dispositivo por USB y habilitar depuración USB
   adb install bin/agromanager-1.0-arm64-v8a-debug.apk
   ```

### Problemas Comunes al Compilar

**Error: "Command failed: ./gradlew..."**
- Solución: Limpiar y volver a compilar
  ```bash
  buildozer android clean
  buildozer android debug
  ```

**Error de permisos**
- Solución: No ejecutar como root, usar usuario normal

**Timeout en descargas**
- Solución: Verificar conexión a internet, intentar nuevamente

## 🎨 Estructura del Proyecto

```
AgroManager/
├── main.py                 # Aplicación principal y dashboard
├── database.py             # Gestión de base de datos SQLite
├── cheques.py             # Módulo de cheques
├── proveedores.py         # Módulo de proveedores
├── gastos.py              # Módulo de gastos
├── ingresos.py            # Módulo de ingresos
├── margenes.py            # Módulo de márgenes
├── superficie.py          # Módulo de superficie
├── mercado.py             # Módulo de precios
├── tambo.py               # Módulo de tambo
├── requirements.txt       # Dependencias Python
├── buildozer.spec         # Configuración para APK
├── agromanager.db         # Base de datos (se crea automáticamente)
└── README.md              # Este archivo
```

## 💾 Base de Datos

La aplicación utiliza SQLite para almacenar todos los datos localmente. La base de datos se crea automáticamente al ejecutar la aplicación por primera vez con datos de ejemplo para facilitar las pruebas.

### Tablas
- `cheques`: Vencimientos de cheques
- `proveedores`: Información de proveedores
- `facturas`: Facturas asociadas a proveedores
- `gastos`: Registro de gastos
- `ingresos`: Registro de ingresos
- `superficie`: Hectáreas por cultivo
- `ganado`: Stock ganadero
- `tambo`: Métricas de producción tambera
- `margenes`: Cálculos de márgenes

## 🌐 APIs Utilizadas

- **Dólar Blue**: https://dolarapi.com/v1/dolares/blue
  - API gratuita, sin autenticación
  - Actualización en tiempo real

- **Commodities**: Los precios de soja, maíz, trigo y ganado son valores estimados. Para producción, integrar con:
  - Bolsa de Cereales de Buenos Aires
  - Mercado de Liniers
  - ONCCA

## 🔧 Personalización

### Cambiar Colores del Tema
En `main.py`, modificar:
```python
self.theme_cls.primary_palette = "Blue"  # Cambiar a: "Green", "Red", etc.
self.theme_cls.theme_style = "Light"     # Cambiar a: "Dark"
```

### Agregar Nuevas Categorías
En los módulos de gastos/ingresos, modificar el método `show_categoria_menu()` para agregar categorías personalizadas.

### Modificar Datos de Ejemplo
En `database.py`, editar el método `load_sample_data()` para cambiar los datos iniciales.

## 📊 Funcionalidades Destacadas

✅ Interfaz moderna con KivyMD  
✅ Base de datos local persistente  
✅ Gráficos interactivos con Matplotlib  
✅ Consulta de precios en tiempo real  
✅ Datos de ejemplo precargados  
✅ Responsive design para móvil y desktop  
✅ Alertas visuales de vencimientos  
✅ Análisis financiero completo  

## 🔜 Mejoras Futuras (Opcionales)

- [ ] Exportar datos a CSV/Excel
- [ ] Filtros por rango de fechas
- [ ] Modo oscuro/claro configurable
- [ ] Backup automático de base de datos
- [ ] Notificaciones push para vencimientos
- [ ] Sincronización en la nube
- [ ] Reportes PDF generados
- [ ] Multi-usuario con login

## 📝 Licencia

Proyecto de código abierto para uso educativo y personal.

## 👨‍💻 Autor

Sistema AgroManager - Versión 1.0

## 🐛 Reporte de Bugs

Para reportar problemas o sugerir mejoras, documentar:
1. Sistema operativo
2. Versión de Python
3. Descripción del error
4. Pasos para reproducir

---

**¡Listo para gestionar tu establecimiento agropecuario! 🚜🌾**