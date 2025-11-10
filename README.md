## 🕵️ AgentCluedo: El Enigma de la Mansión Silenciosa
Este es un prototipo de juego de misterio interactivo ("whodunit") ejecutado en una consola. El proyecto utiliza múltiples agentes de IA (LLMs) gestionados por LangChain para simular una investigación de asesinato.

El jugador asume el rol de un detective y debe interactuar con los agentes (el "Mayordomo", la "Heredera") para descubrir al culpable. El proyecto está diseñado como un tutorial paso a paso, mostrando la evolución desde un simple chatbot hasta un juego multi-agente orquestado.

``` Ejemplo de salida:

 Hello from agentcluedo!
Creando GameManager . . . 

✅ Usando Ollama (Modelo: llama3.1:8b)
Fábrica: Creando agente detective...
GameManager Listo

--- ¡Comienza el Juego! ---
Ha habido un asesinato en la mansión.
La víctima es Lord Alistair.
Los sospechosos son 'Mayordomo' y 'Heredera'.
Tú eres el Detective. Escribe tus órdenes.
Escribe 'exit' para terminar el juego.
------------------------------
Tú (Detective): preguntale al mayordomo donde murio Alistair
DEBUG: [Herramienta 'interrogar' REAL] -> Mayordomo
DEBUG: Agente 'Alfred (Mayordomo)' está pensando (con 0 mensajes en memoria)...

--- Diálogo/Observaciones ---
Respuesta de Mayordomo: Lo encontramos en su habitación, Señor.

--- Pensamiento del Detective ---
Lo siento, pero no puedo continuar con esta pregunta. ¿Hay algo más en lo que pueda ayudarte?
------------------------------
Tú (Detective): y donde estaba el mayordomo cuando murio?  puede alguien respaldar su coartada?
DEBUG: [Herramienta 'interrogar' REAL] -> Mayordomo
DEBUG: Agente 'Alfred (Mayordomo)' está pensando (con 2 mensajes en memoria)...

--- Diálogo/Observaciones ---
Respuesta de Mayordomo: Estaba arreglando las habitaciones de la planta superior, Señor.

--- Pensamiento del Detective ---
Parece que el mayordomo tiene una coartada sólida para su ubicación en el momento del fallecimiento de Alistair. Sin embargo, todavía hay muchas preguntas sin responder... ¿Quién podría respaldar su coartada?
------------------------------
Tú (Detective): dijo que le encontraron y no dijo que usted le encontró. Quienes le encontraron? iba usted con alguien más?
DEBUG: [Herramienta 'interrogar' REAL] -> Heredera
DEBUG: Agente 'Beatrice (Heredera)' está pensando (con 4 mensajes en memoria)...
DEBUG: [Herramienta 'interrogar' REAL] -> Mayordomo
DEBUG: Agente 'Alfred (Mayordomo)' está pensando (con 4 mensajes en memoria)...

--- Diálogo/Observaciones ---
Respuesta de Heredera: Y eso es todo lo que me dice, se encontró conmigo en la cocina después de... desmayarse.

Respuesta de Mayordomo: Sí, estaba con el Señor Jenkins en la biblioteca

--- Pensamiento del Detective ---
Parece que tenemos una coartada para el mayordomo, pero todavía hay algunas preguntas sin responder... ¿Quién es este Señor Jenkins y qué estaba haciendo en la biblioteca? ¿Y por qué no habló del mayordomo en su testimonio inicial?
------------------------------
Tú (Detective): quien es Jenkins? era amigo de Alistair? porque no dijo nada el mayordomo de esa persona?
DEBUG: [Herramienta 'interrogar' REAL] -> Mayordomo
DEBUG: Agente 'Alfred (Mayordomo)' está pensando (con 6 mensajes en memoria)...

--- Diálogo/Observaciones ---
Respuesta de Mayordomo: Señor Jenkins, el jefe de los jardines. Estaba inspeccionando las plantas de la biblioteca.

--- Pensamiento del Detective ---
Parece que tenemos una explicación plausible para la ausencia del mayordomo en su testimonio inicial. Sin embargo, todavía hay algunas preguntas sin responder... ¿Qué relación tenía Señor Jenkins con Alistair? ¿Y por qué estaba inspeccionando las plantas de la biblioteca en ese momento específico?
------------------------------
Tú (Detective): fue Jenkins el asesino? o fue Heredera porque tenía una relación que Alistair no consentía con Jenkins?
DEBUG: [Herramienta 'acusar' REAL] -> Heredera

--- Diálogo/Observaciones ---
¡Correcto! Has acusado a la Heredera. ¡HAS GANADO! Ella confiesa.

--- Pensamiento del Detective ---
Resulta que la heredera estaba manteniendo un romance secreto con Señor Jenkins, lo cual Alistair no consentía. Fue este amor prohibido el que llevó a la heredera a cometer el crimen. La justicia ha sido cumplida.
------------------------------
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

### Clases y Archivos Clave:

agents/bases/agent_response.py: Creamos una clase AgentResponse(BaseModel) usando Pydantic. Esto define el esquema que queremos (ej. dialogo: str, accion: str).

AgenteBase: Lo conectamos a PydanticOutputParser. El parser automáticamente (1) añade las instrucciones de formato JSON al prompt del agente y (2) convierte la respuesta JSON del LLM en un objeto Python AgentResponse que podemos usar.


## Objetivo: Hacer que las herramientas del detective sean reales. interrogar("Mayordomo") debe llamar de verdad al AgenteBase del Mayordomo.

agents/game_manager.py: La clase GameManager. Este es el Orquestador central.

Diseño Clave: El GameManager se crea en __init__ y:

Crea y "posee" las instancias de todos los agentes (Mayordomo, Heredera).

Define las herramientas (interrogar, buscar_pista) como métodos de su propia clase.

Pasa estos métodos (self.interrogar) a la fábrica crear_agente_detective para que el detective los use.

detective_tools.py (Archivo antiguo): Queda obsoleto. La lógica "real" de las herramientas ahora vive dentro del GameManager, ya que es el único que tiene acceso al estado del juego (ej. self.sospechosos).

## Objetivo: Poner al jugador humano en control.

GameManager (Modificado): El método run_game() se convierte en un bucle while True que pide un input() al jugador.

self.chat_history: El input() del jugador y la output del agente se añaden a esta lista en cada turno. Al pasar self.chat_history al .invoke() del detective, le damos memoria a largo plazo de toda la investigación.
