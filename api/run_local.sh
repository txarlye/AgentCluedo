#!/usr/bin/env bash
# Levanta el backend de AgentCluedo en local: DynamoDB Local (Docker) +
# venv (uv) + tablas + uvicorn. Todo gratis, sin tocar AWS.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VENV_DIR=".venv"

info()  { echo "ℹ️  $*"; }
warn()  { echo "⚠️  $*"; }
ok()    { echo "✅ $*"; }
fail()  { echo "❌ $*"; exit 1; }

echo "🕵️  AgentCluedo API - preparando el entorno local..."

command -v uv >/dev/null 2>&1 || fail "No se encontró 'uv'. Instálalo: https://docs.astral.sh/uv/"
command -v docker >/dev/null 2>&1 || fail "No se encontró 'docker'. Necesario para DynamoDB Local."

info "Arrancando DynamoDB Local (Docker)..."
docker compose up -d || fail "No se pudo arrancar DynamoDB Local."

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
    info "Instalando dependencias de api/..."
    uv pip install -r requirements.txt --python "$PYTHON_BIN" --no-cache || fail "Fallo instalando dependencias."
    info "Instalando el motor del juego (engine/) en modo editable..."
    uv pip install -e "$SCRIPT_DIR/../engine" --python "$PYTHON_BIN" --no-cache || fail "Fallo instalando engine/."
}

PYTHON_BIN="$(venv_python)"
if [ -z "${PYTHON_BIN:-}" ]; then
    create_venv
else
    if ! "$PYTHON_BIN" -c "import fastapi, boto3, itsdangerous, stripe, cluedo_engine" >/dev/null 2>&1; then
        warn "El venv existente parece incompleto. Se recreará."
        create_venv
    fi
fi
PYTHON_BIN="$(venv_python)"
ok "Entorno Python listo ($PYTHON_BIN)"

info "Esperando a que DynamoDB Local responda..."
for i in $(seq 1 20); do
    if "$PYTHON_BIN" -c "
import boto3
c = boto3.client('dynamodb', endpoint_url='http://localhost:8500', region_name='us-east-1', aws_access_key_id='local', aws_secret_access_key='local')
c.list_tables()
" >/dev/null 2>&1; then
        break
    fi
    sleep 1
done

info "Creando tablas (si no existen)..."
"$PYTHON_BIN" scripts/init_local_tables.py || fail "Fallo creando las tablas."

export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8
if [ "${OLLAMA_HOST:-}" = "0.0.0.0" ]; then
    export OLLAMA_HOST="http://localhost:11434"
fi

echo "---"
echo "🎮 Arrancando la API en http://localhost:8090 (demo en /static/demo.html)..."
echo "---"
exec "$PYTHON_BIN" -m uvicorn main:app --host 0.0.0.0 --port 8090
