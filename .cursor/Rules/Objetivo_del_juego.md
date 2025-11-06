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