.PHONY: help install run clean test backup export build-apk setup-uv

# Variables
PYTHON := python
UV := uv
UV_RUN := uv run --no-project python
APP_NAME := AgroManager
MAIN_FILE := main.py
DB_FILE := agromanager.db

# Colores para output
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Mostrar esta ayuda
	@echo "$(GREEN)🌾 AgroManager - Makefile$(NC)"
	@echo ""
	@echo "$(YELLOW)Comandos disponibles:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

setup-uv: ## Instalar uv (si no está instalado)
	@echo "$(GREEN)📦 Verificando uv...$(NC)"
	@which uv > /dev/null || (echo "$(YELLOW)Instalando uv...$(NC)" && curl -LsSf https://astral.sh/uv/install.sh | sh)
	@echo "$(GREEN)✅ uv está listo$(NC)"

install-system-deps: ## Instalar dependencias del sistema (requiere sudo)
	@echo "$(GREEN)📦 Instalando dependencias del sistema...$(NC)"
	@echo "$(YELLOW)Esto requiere permisos de sudo$(NC)"
	sudo apt-get update
	sudo apt-get install -y \
		python3-dev \
		libsdl2-dev \
		libsdl2-image-dev \
		libsdl2-mixer-dev \
		libsdl2-ttf-dev \
		libportmidi-dev \
		libswscale-dev \
		libavformat-dev \
		libavcodec-dev \
		zlib1g-dev \
		libgstreamer1.0-dev \
		gstreamer1.0-plugins-base \
		gstreamer1.0-plugins-good
	@echo "$(GREEN)✅ Dependencias del sistema instaladas$(NC)"

install: setup-uv install-system-deps ## Instalar todas las dependencias con uv
	@echo "$(GREEN)📦 Instalando dependencias con uv...$(NC)"
	@echo "$(YELLOW)Usando Python 3.12 (Kivy no es compatible con 3.13)$(NC)"
	$(UV) venv --python 3.12
	$(UV) pip install cython
	$(UV) pip install kivy[base]==2.3.0
	@echo "$(GREEN)📱 Instalando KivyMD desde GitHub (incluye archivos .kv)...$(NC)"
	$(UV) pip install https://github.com/kivymd/KivyMD/archive/refs/tags/1.1.1.zip
	$(UV) pip install matplotlib==3.7.1
	$(UV) pip install requests==2.31.0
	$(UV) pip install kivy-garden==0.1.5
	@echo "$(GREEN)📊 Instalando matplotlib backend para Kivy...$(NC)"
	$(UV) pip install kivy_garden.matplotlib || $(UV) pip install kivy-garden.matplotlib || \
	($(UV) run garden install matplotlib 2>/dev/null || echo "$(YELLOW)⚠️  Continuando sin garden.matplotlib (se instalará en runtime)$(NC)")
	@echo "$(GREEN)✅ Dependencias instaladas correctamente$(NC)"

run: ## Ejecutar la aplicación
	@echo "$(GREEN)🚀 Iniciando $(APP_NAME)...$(NC)"
	$(UV_RUN) $(MAIN_FILE)

run-check: ## Ejecutar con verificación previa
	@echo "$(GREEN)🔍 Verificando instalación...$(NC)"
	$(UV_RUN) run.py

dev: install run ## Instalar dependencias y ejecutar (desarrollo rápido)

clean: ## Limpiar archivos temporales y cache
	@echo "$(YELLOW)🧹 Limpiando archivos temporales...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✅ Limpieza completada$(NC)"

clean-all: clean ## Limpieza profunda (incluye .venv y .buildozer)
	@echo "$(RED)⚠️  Limpieza profunda...$(NC)"
	@rm -rf .venv
	@rm -rf .buildozer
	@rm -rf bin
	@echo "$(GREEN)✅ Limpieza profunda completada$(NC)"

backup: ## Crear backup de la base de datos
	@echo "$(GREEN)💾 Creando backup...$(NC)"
	$(UV_RUN) -c "from utils import ExportUtils; ExportUtils.backup_database()"
	@echo "$(GREEN)✅ Backup creado en backups/$(NC)"

export: ## Exportar datos a CSV
	@echo "$(GREEN)📤 Exportando datos a CSV...$(NC)"
	$(UV_RUN) -c "from utils import ExportUtils; ExportUtils.export_to_csv()"
	@echo "$(GREEN)✅ Datos exportados a exports/$(NC)"

report: ## Generar reporte financiero
	@echo "$(GREEN)📊 Generando reporte financiero...$(NC)"
	$(UV_RUN) -c "from utils import ExportUtils; ExportUtils.generate_financial_report()"
	@echo "$(GREEN)✅ Reporte generado en reportes/$(NC)"

db-reset: ## Resetear base de datos (¡CUIDADO! Borra todos los datos)
	@echo "$(RED)⚠️  ADVERTENCIA: Esto borrará todos los datos$(NC)"
	@read -p "¿Estás seguro? (escribe 'SI' para confirmar): " confirm; \
	if [ "$$confirm" = "SI" ]; then \
		rm -f $(DB_FILE); \
		echo "$(GREEN)✅ Base de datos reseteada$(NC)"; \
	else \
		echo "$(YELLOW)Operación cancelada$(NC)"; \
	fi

db-check: ## Verificar integridad de la base de datos
	@echo "$(GREEN)🔍 Verificando base de datos...$(NC)"
	@sqlite3 $(DB_FILE) "PRAGMA integrity_check;" 2>/dev/null || echo "$(RED)❌ Base de datos no existe o está corrupta$(NC)"

test: ## Ejecutar verificaciones básicas
	@echo "$(GREEN)🧪 Ejecutando tests...$(NC)"
	@$(UV_RUN) -c "import kivy; print('✅ Kivy OK')"
	@$(UV_RUN) -c "import kivymd; print('✅ KivyMD OK')"
	@$(UV_RUN) -c "import matplotlib; print('✅ Matplotlib OK')"
	@$(UV_RUN) -c "import requests; print('✅ Requests OK')"
	@$(UV_RUN) -c "import sqlite3; print('✅ SQLite3 OK')"
	@echo "$(GREEN)✅ Todas las dependencias están instaladas correctamente$(NC)"

info: ## Mostrar información del proyecto
	@echo "$(GREEN)📋 Información del Proyecto$(NC)"
	@echo "Nombre: $(APP_NAME)"
	@echo "Archivo principal: $(MAIN_FILE)"
	@echo "Base de datos: $(DB_FILE)"
	@echo ""
	@echo "$(YELLOW)Estado de archivos:$(NC)"
	@ls -lh *.py 2>/dev/null | awk '{print "  " $$9 " (" $$5 ")"}'
	@echo ""
	@echo "$(YELLOW)Base de datos:$(NC)"
	@if [ -f $(DB_FILE) ]; then \
		echo "  ✅ Existe ($(shell ls -lh $(DB_FILE) | awk '{print $$5}'))"; \
	else \
		echo "  ❌ No existe"; \
	fi

# Comandos para Android (requiere Linux/WSL)
setup-buildozer: ## Instalar Buildozer y dependencias para Android
	@echo "$(GREEN)📱 Instalando Buildozer...$(NC)"
	$(UV) pip install buildozer
	$(UV) pip install cython
	@echo "$(YELLOW)Instalando dependencias del sistema...$(NC)"
	@echo "$(RED)Nota: Requiere sudo$(NC)"
	sudo apt-get update
	sudo apt-get install -y git zip unzip openjdk-11-jdk wget
	sudo apt-get install -y python3-pip autoconf libtool pkg-config
	sudo apt-get install -y zlib1g-dev libncurses5-dev libncursesw5-dev
	sudo apt-get install -y libtinfo5 cmake libffi-dev libssl-dev
	@echo "$(GREEN)✅ Buildozer instalado$(NC)"

build-apk: ## Compilar APK para Android (solo Linux/WSL)
	@echo "$(GREEN)📱 Compilando APK...$(NC)"
	@echo "$(YELLOW)Esto puede tomar varios minutos...$(NC)"
	$(UV) run buildozer android debug
	@echo "$(GREEN)✅ APK generado en bin/$(NC)"

build-apk-release: ## Compilar APK release (firmado)
	@echo "$(GREEN)📱 Compilando APK release...$(NC)"
	$(UV) run buildozer android release
	@echo "$(GREEN)✅ APK release generado$(NC)"

clean-build: ## Limpiar archivos de compilación Android
	@echo "$(YELLOW)🧹 Limpiando archivos de compilación...$(NC)"
	$(UV) run buildozer android clean
	@echo "$(GREEN)✅ Limpieza de build completada$(NC)"

# Comandos de utilidades
lint: ## Verificar código con flake8 (opcional)
	@echo "$(GREEN)🔍 Verificando código...$(NC)"
	@$(UV) pip install flake8 2>/dev/null || true
	@$(UV) run flake8 *.py --max-line-length=120 --ignore=E402,W503 || echo "$(YELLOW)Instala flake8 para análisis de código$(NC)"

format: ## Formatear código con black (opcional)
	@echo "$(GREEN)✨ Formateando código...$(NC)"
	@$(UV) pip install black 2>/dev/null || true
	@$(UV) run black *.py || echo "$(YELLOW)Instala black para formateo automático$(NC)"

deps-update: ## Actualizar dependencias
	@echo "$(GREEN)🔄 Actualizando dependencias...$(NC)"
	$(UV) pip install --upgrade kivy kivymd matplotlib requests
	@echo "$(GREEN)✅ Dependencias actualizadas$(NC)"

deps-list: ## Listar dependencias instaladas
	@echo "$(GREEN)📦 Dependencias instaladas:$(NC)"
	$(UV) pip list

# Comandos rápidos
start: run ## Alias para ejecutar la aplicación

stop: ## Detener la aplicación (si está corriendo)
	@pkill -f "python.*main.py" 2>/dev/null || echo "$(YELLOW)No hay procesos corriendo$(NC)"

restart: stop start ## Reiniciar la aplicación

# Desarrollo
watch: ## Ejecutar y reiniciar automáticamente al cambiar archivos (requiere entr)
	@echo "$(GREEN)👀 Modo watch activado (Ctrl+C para detener)$(NC)"
	@ls *.py | entr -r make run

logs: ## Ver logs de la aplicación
	@echo "$(GREEN)📜 Logs recientes:$(NC)"
	@tail -f *.log 2>/dev/null || echo "$(YELLOW)No hay archivos de log$(NC)"

# Por defecto, mostrar ayuda
.DEFAULT_GOAL := help