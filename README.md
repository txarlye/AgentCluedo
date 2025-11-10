## 🕵️ AgentCluedo: El Enigma de la Mansión Silenciosa
Este es un prototipo de juego de misterio interactivo ("whodunit") ejecutado en una consola. El proyecto utiliza múltiples agentes de IA (LLMs) gestionados por LangChain para simular una investigación de asesinato.

El jugador asume el rol de un detective y debe interactuar con los agentes (el "Mayordomo", la "Heredera") para descubrir al culpable. El proyecto está diseñado como un tutorial paso a paso, mostrando la evolución desde un simple chatbot hasta un juego multi-agente orquestado.

``` Ejemplo de salida:

  Usando Ollama (Modelo: llama3.1:8b)
Fábrica: Creando agente detective...
GameManager Listo

--- ¡Comienza el Juego! ---
Ha habido un asesinato en la mansión.
La víctima es Lord Alistair.
Los sospechosos son 'Mayordomo' y 'Heredera'.
Tú eres el Detective. Escribe tus órdenes.
Escribe 'exit' para terminar el juego.
------------------------------
Tú (Detective): donde estaba el mayordomo cuando murio ?
DEBUG: [Herramienta 'interrogar' REAL] -> Mayordomo
DEBUG: Agente 'Alfred (Mayordomo)' está pensando (con 0 mensajes en memoria)...

--- Diálogo/Observaciones ---
Respuesta de Mayordomo: Estaba en mi habitación, Señor

--- Pensamiento del Detective ---
El mayordomo estaba en su habitación cuando murió.
------------------------------
Tú (Detective): el mayordomo podría confirmarlo ? eso sería solo su palabra
DEBUG: [Herramienta 'interrogar' REAL] -> mayordomo
DEBUG: Agente 'Alfred (Mayordomo)' está pensando (con 2 mensajes en memoria)...

--- Diálogo/Observaciones ---
Respuesta de mayordomo: Se refirió a mi ausencia temporal para realizar tareas, pero señalaron que se produjo el incidente durante mi estancia en la habitación.

--- Pensamiento del Detective ---
Lo siento, no tengo más información disponible sobre el caso. Sin embargo, puedo decir que si el mayordomo estaba en su habitación cuando murió el amo y solo tiene su palabra para confirmarlo, es posible que haya alguna duda o incertidumbre sobre lo que realmente pasó.
------------------------------
Tú (Detective): y la heredera donde estaba ?
DEBUG: [Herramienta 'interrogar' REAL] -> Heredera
DEBUG: Agente 'Beatrice (Heredera)' está pensando (con 4 mensajes en memoria)...

--- Diálogo/Observaciones ---
Respuesta de Heredera: Estaba en mi habitación, como siempre. No tenía nada que ver con la muerte del amo.

--- Pensamiento del Detective ---
La heredera estaba en su habitación cuando murió el amo. Dijo que no tuvo nada que ver con la muerte del amo. Esto podría indicar que la heredera tiene un alibi para el momento de la muerte, pero aún hay muchas preguntas sin respuesta sobre lo que realmente pasó.
------------------------------
Tú (Detective): vayamos a su habitacon a investigar
DEBUG: [Herramienta 'buscar_pista' REAL] -> habitación de la víctima

--- Diálogo/Observaciones ---
Buscas en la habitación de Lord Alistair y encuentras una carta de amenaza sin firmar.

--- Pensamiento del Detective ---
La heredera estaba realmente sorprendida al ver que la carta había sido encontrada en la habitación de su padre, pero parecía conocer demasiado sobre el contenido de la misma. Se preguntó si podría estar tratando de desviar la atención hacia otra persona o si simplemente era una vaga sospecha sin fundamento.
------------------------------
Tú (Detective): porque odiabas a tu padre?
```

##  Características Finales
Juego Interactivo: El jugador dirige la investigación dando órdenes en lenguaje natural.

- Agente Detective Autónomo: Un agente de "Tool Calling" que razona y decide qué "herramienta" (acción) usar (interrogar, buscar_pista, acusar).

- Agentes Sospechosos Inteligentes: Los sospechosos (AgenteBase) usan Parseo de Salida (Pydantic) para responder con diálogo y acciones por separado.

- Orquestación Central: Una clase GameManager que contiene el estado del juego, "posee" a todos los agentes y conecta las herramientas del detective con acciones reales del juego.

- Gestión de Memoria: El detective recuerda el historial completo de la conversación, permitiéndole hacer preguntas de seguimiento basadas en pistas anteriores.

- Fábrica de LLMs: Una llm_factory.py que permite cambiar fácilmente entre Ollama (local) y OpenAI (API) modificando un solo archivo config.json.

## 🛠️ Instalación y Ejecución
Clonar el repositorio:


```Bash
git clone [URL_DEL_REPO]
cd AgentCluedo
```
Crear entorno virtual (recomendado con uv):
 
```Bash
python -m venv .venv
source .venv/bin/activate  # (o .\.venv\Scripts\activate en Windows)
```
Instalar dependencias: (Nota: El requirements.txt debería incluir langchain, langchain-ollama, langchain-openai, pydantic, python-dotenv)

```Bash
uv pip install -r requirements.txt
Configurar el entorno: Crea un archivo .env en la raíz del proyecto y añade tus claves:
```

Fragmento de código

# Para LangSmith (¡esencial para depurar!)
LANGCHAIN_TRACING_V2="true"
LANGCHAIN_API_KEY="tu_api_key_de_langsmith"
LANGCHAIN_PROJECT="AgentCluedo" # O el nombre que prefieras

# Para OpenAI (si se usa)
OPENAI_API_KEY="tu_api_key_de_openai"
Configurar el modelo: Edita settings/config.json para elegir tu LLM. Asegúrate de que el modelo (ej. llama3.1:8b) esté disponible en Ollama.

```JSON

{
  "Agentes": {
    "ia_agente_texto": "ollama",
    "ia_ollama_model": "llama3.1:8b"
  }
}
```
Ejecutar el juego:

```Bash
python main.py
```
### 🧠 Nuestra Evolución (El Viaje del Desarrollo)
Este proyecto se construyó incrementalmente. Cada "Nivel" añade una capa de complejidad y resuelve un nuevo problema.

## Nivel 1: El Bot Básico (Hola, Mundo)
Objetivo: Conseguir una respuesta simple de un LLM.

Clases y Archivos Clave:

settings/settings.py: Un Singleton para cargar la configuración (.env, config.json) y hacerla accesible globalmente (settings.agentes).

agents/llm_factory.py: Nuestra primera Fábrica (Factory Pattern). Su única responsabilidad es leer settings.agentes y devolver el objeto LLM correcto (ChatOllama o ChatOpenAI). Esto desacopla el resto de la app de cuál LLM estamos usando.

main.py: Se modificó temporalmente con un bucle while True que usaba input() y llm.invoke() para probar la conexión.

## Nivel 2: Los Agentes "Pasivos" (Los Sospechosos)
Objetivo: Crear PNJ (Personajes No Jugadores) con personalidades definidas.

Clases y Archivos Clave:

agents/bases/base_agent.py: Creamos la clase AgenteBase. Sirve como un Molde (Herencia) para todos los agentes pasivos. Almacena su SystemMessage (su personalidad).

prompts/mayordomo.md: Movimos los prompts fuera del código Python. Esto es Separación de Responsabilidades (SoC): podemos editar la personalidad de un agente sin tocar el código.

## Nivel 3: Parseo de Salida (¡Que hablen bien!)
Objetivo: Forzar a los agentes a responder no solo con texto, sino con acciones y diálogo por separado.

Clases y Archivos Clave:

agents/bases/agent_response.py: Creamos una clase AgentResponse(BaseModel) usando Pydantic. Esto define el esquema que queremos (ej. dialogo: str, accion: str).

AgenteBase (Modificado): Lo conectamos a PydanticOutputParser. El parser automáticamente (1) añade las instrucciones de formato JSON al prompt del agente y (2) convierte la respuesta JSON del LLM en un objeto Python AgentResponse que podemos usar.

Bug Resuelto: El LLM (siendo pequeño) a veces "olvidaba" el formato JSON.

Solución: Modificamos llm_factory.py para añadir .bind(format="json") al LLM de Ollama, forzándolo a nivel de API a devolver JSON.

## Nivel 4: El Detective Autónomo (Simulado)
Objetivo: Crear un agente "activo" que pueda decidir qué hacer usando herramientas.

Clases y Archivos Clave:

agents/detective_tools.py: Creamos nuestras primeras herramientas simuladas (stubs) usando el decorador @tool. El docstring ("""...""") es crucial, ya que es lo que el LLM lee para saber qué hace la herramienta.

agents/detective_agent.py: Creamos crear_agente_detective. Usamos create_react_agent y AgentExecutor para construir el "cerebro" ReAct.

minigames/game_3...: Un script de prueba para "soltar" al detective con un objetivo y ver cómo usa las herramientas simuladas.

## Nivel 5: El Orquestador (¡Conectando Todo!)
Objetivo: Hacer que las herramientas del detective sean reales. interrogar("Mayordomo") debe llamar de verdad al AgenteBase del Mayordomo.

Clases y Archivos Clave:

agents/game_manager.py: La clase GameManager. Este es el Orquestador central.

Diseño Clave: El GameManager se crea en __init__ y:

Crea y "posee" las instancias de todos los agentes (Mayordomo, Heredera).

Define las herramientas (interrogar, buscar_pista) como métodos de su propia clase.

Pasa estos métodos (self.interrogar) a la fábrica crear_agente_detective para que el detective los use.

detective_tools.py (Archivo antiguo): Queda obsoleto. La lógica "real" de las herramientas ahora vive dentro del GameManager, ya que es el único que tiene acceso al estado del juego (ej. self.sospechosos).

## Nivel 6: El Juego Interactivo (¡Tú eres el Detective!)
Objetivo: Poner al jugador humano en control.

Clases y Archivos Clave:

GameManager (Modificado): El método run_game() se convierte en un bucle while True que pide un input() al jugador.

self.chat_history: El input() del jugador y la output del agente se añaden a esta lista en cada turno. Al pasar self.chat_history al .invoke() del detective, le damos memoria a largo plazo de toda la investigación.

### 🐞 Diario de Depuración 
ImportError: cannot import 'create_react_agent':

Causa: Nuestra caché de uv/pip tenía una versión antigua de langchain (1.x) que entraba en conflicto con la nueva arquitectura (0.2.x).

Solución: Forzar la instalación de una versión específica: uv pip install "langchain>=0.2.0, <1.0.0".

AttributeError: 'function' object has no attribute 'name':

Causa: Le pasamos funciones de Python simples (def mi_tool...) a create_react_agent en lugar de objetos Tool.

Solución: Añadir el decorador @tool a nuestras funciones de herramienta.

KeyError: 'tools':

Causa: Nuestro prompt personalizado (PROMPT_ESPANOL) tenía una variable {tools}, pero no le estábamos pasando el texto de las herramientas.

Solución: Usar render_text_description(tools_list) para convertir las herramientas en texto y prompt.partial(tools=...) para "pre-rellenar" el prompt.

TypeError: missing 1 required positional argument: 'self':

Causa: El error más difícil. El decorador @tool no funciona bien con métodos de clase (funciones con self). El validador (args_schema) y el ejecutor de la herramienta no se ponían de acuerdo sobre si self era un argumento.

Solución: Abandonar el decorador @tool dentro del GameManager. En su lugar, construimos la lista de herramientas manualmente en __init__ usando la clase StructuredTool (que maneja múltiples argumentos) y pasando el método "atado" (func=self.interrogar).

El Agente Piensa en Inglés (y el "Chatterbox")

Causa: Usar un PROMPT_ESPANOL personalizado con create_tool_calling_agent confundía al LLM, que mezclaba "Pensamientos" (texto) con "Acciones" (JSON), rompiendo el bucle.

Solución: Usamos el prompt estándar del Hub (hub.pull("hwchase17/openai-tools-agent")), que está optimizado para "Tool Calling".

Arreglo para el idioma: Para forzar al agente a hablar español, añadimos la instrucción "¡Piensa y habla en español!" al objetivo inicial que le pasamos en run_game().
