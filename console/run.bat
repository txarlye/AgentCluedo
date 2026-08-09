@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul

cd /d "%~dp0"

set "VENV_DIR=.venv"
set "REQ_FILE=requirements.txt"
set "PYTHON_BIN=%VENV_DIR%\Scripts\python.exe"

echo.
echo AgentCluedo - preparando el entorno...
echo.

where uv >nul 2>nul
if errorlevel 1 goto :no_uv

set "NEED_INSTALL=0"
if not exist "%PYTHON_BIN%" set "NEED_INSTALL=1"
if "%NEED_INSTALL%"=="1" goto :do_install

"%PYTHON_BIN%" -c "import langchain, langchain_core, langchain_ollama, langchain_openai, cluedo_engine" >nul 2>nul
if errorlevel 1 (
    echo [AVISO] El entorno virtual existente parece corrupto o incompleto. Se recreara.
    set "NEED_INSTALL=1"
)
if "!NEED_INSTALL!"=="1" goto :do_install
goto :venv_ready

:do_install
echo Creando entorno virtual con Python 3.12 en %VENV_DIR% ...
if exist "%VENV_DIR%" rmdir /s /q "%VENV_DIR%"
uv venv --python 3.12 "%VENV_DIR%"
if errorlevel 1 goto :venv_fail

echo Instalando dependencias desde %REQ_FILE% ^(puede tardar un poco^)...
rem --no-deps: requirements.txt es un "pip freeze" con versiones fijadas que
rem            se contradicen si uv intenta resolverlas en modo estricto.
rem --no-cache: evita wheels corruptos que puedan haber quedado en la cache.
uv pip install -r "%REQ_FILE%" --python "%PYTHON_BIN%" --no-deps --no-cache
if errorlevel 1 goto :install_fail

echo Instalando el motor del juego ^(engine/^) en modo editable...
uv pip install -e "%~dp0..\engine" --python "%PYTHON_BIN%" --no-cache
if errorlevel 1 goto :install_fail

:venv_ready
echo [OK] Entorno Python listo ^(%PYTHON_BIN%^)

if exist "settings\.env" goto :env_ready
if not exist "settings\.env_example" goto :no_env_example
copy /y "settings\.env_example" "settings\.env" >nul
echo [AVISO] No existia settings\.env, se creo a partir de .env_example.
echo [AVISO] Edita settings\.env y anade tu OPEN_AI_API si vas a usar OpenAI.
goto :env_ready

:no_env_example
echo [AVISO] No existe settings\.env ni settings\.env_example.

:env_ready
if not exist "settings\config.json" goto :ollama_done

rem Leemos el motor/modelo configurados en config.json con un pequeno script
rem Python auxiliar, redirigiendo su salida a un fichero temporal (capturar
rem la salida de un comando directamente con "for /f ('...')" es fragil en
rem cmd.exe cuando el comando lleva varios argumentos entre comillas).
set "TMP_PY=%TEMP%\agentcluedo_read_config_%RANDOM%.py"
set "TMP_OUT=%TEMP%\agentcluedo_config_out_%RANDOM%.txt"
> "%TMP_PY%" echo import json, sys
>> "%TMP_PY%" echo cfg = json.load(open(sys.argv[1], encoding="utf-8")).get("Agentes", {})
>> "%TMP_PY%" echo print(cfg.get(sys.argv[2], ""))

"%PYTHON_BIN%" "%TMP_PY%" "settings\config.json" "ia_agente_texto" > "%TMP_OUT%" 2>nul
for /f "usebackq delims=" %%E in ("%TMP_OUT%") do set "ENGINE=%%E"

if /i not "!ENGINE!"=="ollama" goto :cleanup_config_tmp

"%PYTHON_BIN%" "%TMP_PY%" "settings\config.json" "ia_ollama_model" > "%TMP_OUT%" 2>nul
for /f "usebackq delims=" %%M in ("%TMP_OUT%") do set "MODEL=%%M"

where ollama >nul 2>nul
if errorlevel 1 (
    echo [AVISO] config.json usa Ollama pero no se encontro el comando 'ollama'. Instalalo desde https://ollama.com
    goto :cleanup_config_tmp
)

ollama list >nul 2>nul
if errorlevel 1 (
    echo [AVISO] Ollama esta instalado pero no responde. Arrancalo primero.
    goto :cleanup_config_tmp
)

ollama list | findstr /i /b "!MODEL!" >nul
if errorlevel 1 (
    echo [AVISO] El modelo '!MODEL!' no esta descargado. Ejecuta: ollama pull !MODEL!
) else (
    echo [OK] Ollama disponible con el modelo '!MODEL!'.
)

:cleanup_config_tmp
del "%TMP_PY%" >nul 2>nul
del "%TMP_OUT%" >nul 2>nul

:ollama_done
rem PYTHONUTF8 evita UnicodeEncodeError: la consola usa cp1252 por defecto y
rem el juego imprime emojis directamente con print().
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"

rem Si OLLAMA_HOST esta puesto a nivel de sistema como "0.0.0.0" (tipico para
rem que el SERVIDOR de Ollama escuche en todas las interfaces), el cliente
rem Python intenta CONECTAR a esa direccion y falla con WinError 10049.
rem Lo forzamos aqui solo para este proceso, sin tocar la variable global.
if /i "%OLLAMA_HOST%"=="0.0.0.0" set "OLLAMA_HOST=http://localhost:11434"

echo.
echo Arrancando AgentCluedo...
echo.
"%PYTHON_BIN%" main.py

echo.
pause
exit /b 0

:no_uv
echo [ERROR] No se encontro 'uv'. Instalalo desde https://docs.astral.sh/uv/
goto :fail

:venv_fail
echo [ERROR] No se pudo crear el entorno virtual.
goto :fail

:install_fail
echo [ERROR] Fallo instalando dependencias.
goto :fail

:fail
echo.
pause
exit /b 1
