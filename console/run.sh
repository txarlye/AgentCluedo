#!/usr/bin/env bash
# Arranca AgentCluedo automáticamente: crea/repara el venv con uv,
# instala dependencias, prepara el .env y lanza main.py.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VENV_DIR=".venv"
REQ_FILE="requirements.txt"

info()  { echo "ℹ️  $*"; }
warn()  { echo "⚠️  $*"; }
ok()    { echo "✅ $*"; }
fail()  { echo "❌ $*"; exit 1; }

echo "🕵️  AgentCluedo - preparando el entorno..."

# 1. uv es obligatorio (gestiona python + venv + dependencias)
command -v uv >/dev/null 2>&1 || fail "No se encontró 'uv'. Instálalo con: pipx install uv  (o ver https://docs.astral.sh/uv/)"

# 2. Localizar el python del venv según plataforma
venv_python() {
    if [ -f "$VENV_DIR/Scripts/python.exe" ]; then
        echo "$VENV_DIR/Scripts/python.exe"
    elif [ -f "$VENV_DIR/bin/python" ]; then
        echo "$VENV_DIR/bin/python"
    fi
}

create_venv() {
    info "Creando entorno virtual con Python 3.12 en $VENV_DIR ..."
    rm -rf "$VENV_DIR"
    uv venv --python 3.12 "$VENV_DIR" || fail "No se pudo crear el venv."
    PYTHON_BIN="$(venv_python)"
    info "Instalando dependencias desde $REQ_FILE (puede tardar un poco)..."
    # --no-deps: requirements.txt es un "pip freeze" con versiones fijadas que se
    #            contradicen si uv intenta resolverlas en modo estricto.
    # --no-cache: evita wheels corruptos que puedan haber quedado en la caché de uv.
    uv pip install -r "$REQ_FILE" --python "$PYTHON_BIN" --no-deps --no-cache \
        || fail "Fallo instalando dependencias."
}

PYTHON_BIN="$(venv_python)"

if [ -z "${PYTHON_BIN:-}" ]; then
    create_venv
else
    # Comprobamos que el venv no esté roto (p.ej. por sincronización con Synology Drive)
    if ! "$PYTHON_BIN" -c "import langchain, langchain_core, langchain_ollama, langchain_openai" >/dev/null 2>&1; then
        warn "El venv existente parece corrupto o incompleto. Se recreará."
        create_venv
    fi
fi

PYTHON_BIN="$(venv_python)"
[ -n "${PYTHON_BIN:-}" ] || fail "No se pudo localizar el intérprete del venv tras crearlo."
ok "Entorno Python listo ($PYTHON_BIN)"

# 3. Preparar .env si no existe
if [ ! -f "settings/.env" ]; then
    if [ -f "settings/.env_example" ]; then
        cp "settings/.env_example" "settings/.env"
        warn "No existía settings/.env, se creó a partir de .env_example."
        warn "Edita settings/.env y añade tu OPEN_AI_API si vas a usar OpenAI."
    else
        warn "No existe settings/.env ni settings/.env_example. Créalo manualmente si el juego lo necesita."
    fi
fi

# 4. Si el motor configurado es Ollama, comprobar que esté disponible
CONFIG_FILE="settings/config.json"
if [ -f "$CONFIG_FILE" ] && grep -q '"ia_agente_texto"[[:space:]]*:[[:space:]]*"ollama"' "$CONFIG_FILE"; then
    MODEL=$(grep -o '"ia_ollama_model"[[:space:]]*:[[:space:]]*"[^"]*"' "$CONFIG_FILE" | sed -E 's/.*:\s*"([^"]*)"/\1/')
    if ! command -v ollama >/dev/null 2>&1; then
        warn "config.json usa Ollama pero no se encontró el comando 'ollama'. Instálalo desde https://ollama.com"
    elif ! ollama list >/dev/null 2>&1; then
        warn "Ollama está instalado pero no responde. Arráncalo (ej: abre la app de Ollama o ejecuta 'ollama serve')."
    elif [ -n "$MODEL" ] && ! ollama list | grep -qi "^${MODEL}"; then
        warn "El modelo '$MODEL' no está descargado. Ejecuta: ollama pull $MODEL"
    else
        ok "Ollama disponible con el modelo '$MODEL'."
    fi
fi

# 5. Arrancar el juego
# PYTHONUTF8 evita UnicodeEncodeError en Windows: la consola usa cp1252 por
# defecto y el juego imprime emojis (✅⚠️) directamente con print().
export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8

# Si OLLAMA_HOST está puesto a nivel de sistema como "0.0.0.0" (típico para
# que el SERVIDOR de Ollama escuche en todas las interfaces), el cliente
# Python intenta CONECTAR a esa dirección y falla (WinError 10049).
# Lo forzamos aquí solo para este proceso, sin tocar la variable global.
if [ "${OLLAMA_HOST:-}" = "0.0.0.0" ]; then
    export OLLAMA_HOST="http://localhost:11434"
fi

echo "---"
echo "🎮 Arrancando AgentCluedo..."
echo "---"
exec "$PYTHON_BIN" main.py
