vamos a aprender a:

- crear un agente ollama u openai (seleccionable según opciones) 

- crear varios agentes

- orquestar varios agentes 

- orquestarlos usando langchain

- ver los prompts y resultados con langsmith



todo eso mientras hacemos un juego de ui sencilla que ya hemos empezado con mi:

main:

from settings.settings import settings

from UI.console.console_base import ConsoleBase



console = ConsoleBase(settings.main_name)













def main():

    print("Hello from agentcluedo!")

    console.show_menu()



if __name__ == "__main__":

    main()



mi settings/settings.py

from pathlib import Path

from dotenv import load_dotenv

from typing import Any

import json, os



from .utils.read_config import load_config

from .utils.write_config import save_config

from .utils.api_limits import APILimitManager





class Settings:

    """Singleton para gestión de configuración"""

    _instance = None

    _initialized = False

    

    def __new__(cls, config_path=None):

        if cls._instance is None:

            cls._instance = super(Settings, cls).__new__(cls)

        return cls._instance

    

    def __init__(self, config_path=None):

        if self._initialized:

            return 

        if config_path:

            self.config_path = Path(config_path)

        else:

            base_dir = Path(__file__).parent

            self.config_path = base_dir / "config.json" 

        self.config = load_config(self.config_path) 

        self._load_config_sections(config_path) 

        env_path = self.config_path.parent / ".env"

        if env_path.exists():

            load_dotenv(env_path) 

        self._load_env_vars() 

        self.api_limits = APILimitManager(self.config) 

        self._initialized = True

    

    def _load_config_sections(self, path): 

        def load_config_internal(config_path, objective=None):

            if Path(config_path).exists() is not True: 

                print("⚠️No se encontró config.json, usando valores por defecto.")

                return {}

            with open(config_path, "r", encoding="utf-8") as f:

                return json.load(f).get(objective, {})

        

        # Carga de config de Json:

        config_main = load_config(self.config_path, "main")

        config_agentes = load_config_internal(self.config_path, "Agentes")

        

        ########################################## ##################################

        

        

        self.main_name  = config_main.get("name")

        self.agentes    = config_agentes.get("ia_agente_texto", "ollama")

        

        

        

        

        

    def _load_env_vars(self):

        """Carga variables de entorno como atributos"""

        env_vars = [

            "HUGGINGFACE_TOKEN",

            "OPEN_AI_API",

            "API_HOST",

            "API_PORT"

        ]

        

        for var_name in env_vars:

            value = os.getenv(var_name)

            if value:

                setattr(self, var_name, value) 

    

    def save(self):

        """Guarda la configuración usando save_config"""

        save_config(self.config, self.config_path)





# Instancia global singleton

settings = Settings()

mi settings/config.json:

{

  "main": {

    "name": "AgentCluedo",

    "version": "0.1.0",

    "description": "AgentCluedo es un juego de misterio interactivo donde un asesinato ha ocurrido en una mansión aislada. Hay un detective, varios sospechosos y un \"Director de Juego\" (que sabe la verdad). Todos son agentes de IA (LLMs) gestionados por LangChain, y el objetivo del jugador humano es observar o, si lo prefiere, tomar el rol del detective."

  },

  "Agentes": {

    "ia_agente_texto": "ollama",

    "ia_agente_imagen": "stable-diffusion"

    }

}

mi settings\utils\read_config.py

import json

from pathlib import Path



def load_config(path="config.json", objective=None): 

    path_obj = Path(path) if not isinstance(path, Path) else path

    if not path_obj.exists():

        print("⚠️ No se encontró config.json, usando valores por defecto.")

        return {}

    with open(path_obj, "r", encoding="utf-8") as f:

        config = json.load(f)

        return config.get(objective, {}) if objective else config

mi settings\utils\write_config.py

import json

from pathlib import Path



def save_config(config_data, path="config.json"):

    path_obj = Path(path) if not isinstance(path, Path) else path

    with open(path_obj, "w", encoding="utf-8") as f:

        json.dump(config_data, f, ensure_ascii=False, indent=2)

mi UI\console\console_base.py

from UI.console.menu_consola import MenuConsola

class ConsoleBase:

    def __init__(self, game_title: str):

        self.game_title = game_title

        self.menu = MenuConsola(self.game_title)

    

    def show_menu(self):

        self.menu.show_menu()

    

    def start_game(self):

        self.menu.start_game()

    

    def load_game(self):

        self.menu.load_game()

    pass

y mi UI\console\menu_consola.py

class MenuConsola:

    def __init__(self, game_title: str): 

        self.game_title = game_title

    

    def show_menu(self):

        print(f"========== {self.game_title} ==========")

        print("1. Iniciar juego")

        print("2. Cargar juego")

        print("3. Salir")

        print("4. Configurar juego")

        print("5. Salir")

        print("6. Salir")

        print("7. Salir")

        print("8. Salir")

        print("9. Salir")

        print("10. Salir")



te recuerdo el argumento:

🕵️ El Enigma de la Mansión Silenciosa

Este es un juego de misterio interactivo donde un asesinato ha ocurrido en una mansión aislada. Hay un detective, varios sospechosos y un "Director de Juego" (que sabe la verdad). Todos son agentes de IA (LLMs) gestionados por LangChain, y el objetivo del jugador humano es observar o, si lo prefiere, tomar el rol del detective.



Los Agentes (4 roles clave)

Necesitamos al menos cuatro agentes para que la dinámica funcione:



El Orquestador (Agente "Game Master"):



Rol: Este agente es el "cerebro" del juego. Sabe quién es el asesino, el arma, el motivo y la ubicación de las pistas clave.



Función en LangChain: Se inicializa con un prompt secreto que contiene la "verdad". Su trabajo es (1) describir la escena del crimen inicial, (2) responder a las acciones de búsqueda del detective ("Buscas en el escritorio y encuentras...") y (3) determinar si el juego termina cuando el detective hace una acusación.



El Detective (Agente "Investigador"):



Rol: El protagonista. Su objetivo es resolver el crimen.



Función en LangChain: Este sería el agente más complejo, probablemente un Agente ReAct (Reasoning and Acting). Se le darían "herramientas" (Tools) como: interrogar(sospechoso, pregunta) y buscar_pista(ubicacion). El agente debe razonar, decidir a quién interrogar, qué preguntar y dónde buscar, todo basado en las respuestas que recibe.



El Sospechoso 1 (Agente "Coartada A"):



Rol: Un personaje con una personalidad, una historia de fondo y una coartada (verdadera o falsa).



Función en LangChain: Este agente necesita Memoria (Memory). Se le da un prompt de sistema que define su identidad: "Eres el Mayordomo. Estabas en la cocina. Viste a la Heredera discutir con la víctima... [Si es el asesino: ...y estás mintiendo sobre la hora]". Debe usar la memoria conversacional para ser coherente en sus respuestas al Detective.



El Sospechoso 2 (Agente "Coartada B"):



Rol: Otro personaje con su propia coartada, motivos y secretos.



Función en LangChain: Igual que el Sospechoso 1, pero con una personalidad y un prompt de sistema completamente diferentes ("Eres la Heredera. Odiabas a la víctima porque te iba a desheredar, pero estabas en tu habitación..."). También necesita Memoria para no contradecirse.



Puedes añadir fácilmente más agentes (Sospechoso 3, Sospechoso 4) para hacerlo más complejo.



¿Cómo se implementaría con LangChain?

El flujo del juego sería una "cadena" (Chain) orquestada que maneja los turnos:



Inicio: El Orquestador describe la escena: "Están reunidos en la biblioteca. Lord Alistair ha sido asesinado con un abrecartas..."



Turno del Detective: El agente Detective (usando ReAct) piensa: "Necesito establecer líneas de tiempo. Preguntaré al Mayordomo dónde estaba". Ejecuta la herramienta interrogar(Mayordomo, "¿Dónde estaba a las 8 PM?").



Turno del Sospechoso: El agente Mayordomo recibe la pregunta. Consulta su prompt de sistema y su Memoria (para ver si ya dijo algo al respecto) y genera una respuesta: "Estaba en la cocina, señor, preparando el té".



Turno del Detective: El Detective recibe la respuesta. Piensa: "Coartada débil. Ahora interrogaré a la Heredera". Ejecuta interrogar(Heredera, "¿Vio al Mayordomo?").



Turno del Sospechoso 2: La agente Heredera responde: "¡No! ¡Ese mentiroso! Lo vi cerca de la biblioteca...".



Bucle: El juego continúa. El Detective puede decidir buscar_pista(cocina). El Orquestador respondería ("Encuentras un pañuelo manchado...").



Final: El Detective decide que tiene suficiente evidencia y ejecuta una herramienta final: acusar(Heredera). El Orquestador recibe esto, compara con su "verdad" secreta y anuncia el final del juego.



Este diseño utiliza los componentes centrales de LangChain: LLMs para la generación de texto, Prompts para definir los roles, Memory para la coherencia de los sospechosos y Agents/Tools para que el detective pueda tomar acciones e interactuar con el entorno.





y los agentes usaremos reglas del clean code, herencias y los patrones de diseño que sean necesarios para eficiencia y mantenimiento