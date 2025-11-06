#!/bin/bash

# Script de inicio rápido para AgroManager con uv
# Uso: bash quickstart.sh

set -e

echo "🌾 AgroManager - Inicio Rápido"
echo "======================================"
echo ""

# Función para verificar si un comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar si uv está instalado
echo "Verificando uv..."
if ! command_exists uv; then
    echo -e "${YELLOW}uv no está instalado. Instalando...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Agregar uv al PATH para esta sesión
    export PATH="$HOME/.cargo/bin:$PATH"
    
    if ! command_exists uv; then
        echo -e "${RED}Error: No se pudo instalar uv${NC}"
        echo "Por favor, visita: https://github.com/astral-sh/uv"
        exit 1
    fi
fi
echo -e "${GREEN}✅ uv está instalado${NC}"
echo ""

# Instalar dependencias del sistema
echo "Verificando dependencias del sistema..."
if ! dpkg -l | grep -q libsdl2-dev; then
    echo -e "${YELLOW}Instalando dependencias del sistema (requiere sudo)...${NC}"
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
    echo -e "${GREEN}✅ Dependencias del sistema instaladas${NC}"
else
    echo -e "${GREEN}✅ Dependencias del sistema ya están instaladas${NC}"
fi
echo ""

# Crear entorno virtual con uv si no existe
if [ ! -d ".venv" ]; then
    echo "Creando entorno virtual..."
    uv venv
    echo -e "${GREEN}✅ Entorno virtual creado${NC}"
else
    echo -e "${GREEN}✅ Entorno virtual ya existe${NC}"
fi
echo ""

# Instalar dependencias
echo "Instalando dependencias Python..."
uv pip install cython
uv pip install kivy[base]==2.3.0
uv pip install kivymd==1.1.1
uv pip install matplotlib==3.7.1
uv pip install requests==2.31.0
uv pip install kivy-garden==0.1.5
echo -e "${GREEN}✅ Dependencias principales instaladas${NC}"
echo ""

# Instalar matplotlib backend para Kivy
echo "Instalando matplotlib backend para Kivy..."
uv run garden install matplotlib
echo -e "${GREEN}✅ Backend de matplotlib instalado${NC}"
echo ""

# Verificar que todos los archivos necesarios existen
echo "Verificando archivos del proyecto..."
archivos_necesarios=(
    "main.py"
    "database.py"
    "cheques.py"
    "proveedores.py"
    "gastos.py"
    "ingresos.py"
    "margenes.py"
    "superficie.py"
    "mercado.py"
    "tambo.py"
)

faltantes=()
for archivo in "${archivos_necesarios[@]}"; do
    if [ ! -f "$archivo" ]; then
        faltantes+=("$archivo")
    fi
done

if [ ${#faltantes[@]} -ne 0 ]; then
    echo -e "${RED}⚠️  Faltan los siguientes archivos:${NC}"
    for archivo in "${faltantes[@]}"; do
        echo "  - $archivo"
    done
    echo ""
    echo "Por favor, copia todos los archivos del proyecto antes de continuar."
    exit 1
fi
echo -e "${GREEN}✅ Todos los archivos necesarios están presentes${NC}"
echo ""

# Ejecutar verificación de dependencias
echo "Verificando dependencias..."
uv run python -c "import kivy; print('✅ Kivy OK')"
uv run python -c "import kivymd; print('✅ KivyMD OK')"
uv run python -c "import matplotlib; print('✅ Matplotlib OK')"
uv run python -c "import requests; print('✅ Requests OK')"
echo -e "${GREEN}✅ Todas las dependencias verificadas${NC}"
echo ""

# Preguntar si desea ejecutar la aplicación
echo "======================================"
echo -e "${GREEN}🎉 Instalación completada!${NC}"
echo "======================================"
echo ""
echo "Para ejecutar AgroManager:"
echo "  1. Con Make: ${YELLOW}make run${NC}"
echo "  2. Con uv directamente: ${YELLOW}uv run python main.py${NC}"
echo "  3. Con el script: ${YELLOW}uv run python run.py${NC}"
echo ""

read -p "¿Deseas ejecutar AgroManager ahora? (s/N): " respuesta
if [[ "$respuesta" =~ ^([sS][iI]|[sS])$ ]]; then
    echo ""
    echo -e "${GREEN}🚀 Iniciando AgroManager...${NC}"
    echo ""
    uv run python main.py
else
    echo ""
    echo "Para ejecutar más tarde, usa: ${YELLOW}make run${NC} o ${YELLOW}uv run python main.py${NC}"
fi