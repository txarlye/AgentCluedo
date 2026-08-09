# AgentCluedo → SaaS de pago: hoja de ruta por fases, Fase 1 detallada

## Contexto

AgentCluedo es hoy un juego de consola (Python + LangChain + Ollama/OpenAI) ya
funcional (`console/` tras esta reestructuración). El usuario quiere
evolucionarlo a un SaaS monetizable: paquetes de créditos vía Stripe,
partidas ejecutadas con Claude en Amazon Bedrock, y en fases posteriores
retratos de personajes generados por IA y NFTs coleccionables en OpenSea.

Decisión ya tomada con el usuario: **no se crea un repo nuevo**. El repo
`txarlye/AgentCluedo` (pequeño, aislado, 1.2 MB sin `.venv`) se reestructura
como monorepo, manteniendo el juego de consola funcionando de forma
independiente.

Este documento traza la **hoja de ruta completa a alto nivel** y detalla en
profundidad únicamente la **Fase 1** (SaaS de pago: Stripe + AWS + Bedrock),
que es lo que el usuario pidió planificar ahora. Las fases 2 y 3 se dejan
como esbozo para no perder el hilo, pero se planificarán en detalle cuando
llegue su turno.

**Importante:** este plan es un documento para guiar la implementación. No
incluye aprovisionar infraestructura AWS real ni crear cuentas/objetos en
Stripe — eso requiere credenciales que Claude Code no tiene en este entorno.

## Regla: cada fase termina en una demo jugable

Ninguna fase se da por cerrada solo con backend/infra funcionando "por
API". Cada fase debe terminar en algo que se pueda abrir en un navegador y
jugar de principio a fin, aunque sea tosco:
- La **consola** sigue jugable durante todo el proceso (no se toca su
  experiencia en ningún punto).
- La **Fase 1** incluye una página HTML estática mínima (ver §7) con los
  `fetch()` justos para pagar (Checkout de Stripe) y jugar una partida
  completa contra la API — no queda solo en curl/Postman.
- Cada fase siguiente (1.5, 2, 3) mejora esa misma demo, nunca empieza una
  nueva desde cero.

## Hoja de ruta completa (alto nivel)

1. **Fase 1 — SaaS de pago** (detallada abajo): reestructura a monorepo,
   motor de juego desacoplado de la consola, Bedrock como proveedor,
   backend FastAPI, créditos vía Stripe Checkout + webhook, auth ligera, y
   una demo HTML mínima pero jugable de principio a fin (pagar → jugar →
   ganar/perder). El frontend "de verdad" (React) llega en la Fase 1.5.
2. **Fase 1.5 — Frontend real**: **React + Vite** (decidido, no un
   framework "más moderno" tipo SvelteKit/Solid) + S3 + CloudFront, una
   vez el contrato de la API esté estable. Se prefiere React sobre
   alternativas más ligeras porque encaja con el patrón de despliegue
   estático S3+CloudFront ya decidido y porque el proyecto también es
   pieza de portfolio, donde React es lo más reconocible — el coste de
   esa elección es solo bundles algo más grandes/más boilerplate, sin
   requisitos de rendimiento en esta UI que lo penalicen.
3. **Fase 2 — Reparto dinámico + retratos de personajes generados por
   IA**: dos bloques, en este orden (el segundo depende del primero):
   1. **Generación procedural del caso** (nuevo, no estaba antes en el
      roadmap): hoy el motor tiene hardcodeados 2 sospechosos
      (Mayordomo/Heredera, personalidad fija en `.md`), víctima fija y
      culpable fijo en código (`acusar()` compara literal `"heredera"`).
      Este bloque hace que el LLM genere en cada partida: época/escenario,
      víctima, 4-6 sospechosos con relaciones, la verdad secreta
      (culpable/móvil/arma/cronología), pistas/mentiras/coartadas, y una
      descripción visual de cada personaje — sustituyendo los prompts
      `.md` fijos por fichas generadas dinámicamente. Sin esto, no hay
      reparto variable que retratar.
   2. **Retratos** (lo ya discutido): abstracción `ImageProvider`, lámina
      de reparto conjunta → retratos individuales, coste variable por
      imagen.
   - **Proveedor en local (decidido):** ComfyUI en modo API (`--listen`,
     sin UI manual), con un workflow fijo (checkpoint SDXL/Flux + LoRA de
     estilo para coherencia visual entre personajes de la misma partida).
     `ImageProvider` local lo llama por HTTP (`POST /prompt` +
     `GET /history/{id}`).
   - **Proveedor en AWS (decidido): Amazon Bedrock**, con los modelos de
     Stability AI disponibles en Bedrock (Stable Diffusion 3 / Stable
     Image Core-Ultra) — explícitamente **no** Titan Image Generator ni
     Nova Canvas, que AWS retira durante 2026. Gestionado, pago por
     imagen, sin GPU propia que operar — encaja con ECS Fargate igual que
     el resto del backend. Queda descartada por ahora la opción de
     autoalojar ComfyUI en una instancia GPU de AWS (EC2 g5/g6 o
     SageMaker): daría más control de estilo pero convierte el proyecto en
     operador de GPU (coste en reposo, escalado, cold starts) sin
     justificación todavía — se revisita solo si el estilo de
     Bedrock/Stability resulta insuficiente.
4. **Fase 3 — NFTs coleccionables (OpenSea)**: contrato ERC-721A en
   Base/Polygon, mint por lote al terminar cada partida (todo el reparto,
   ganes o pierdas), metadatos + imágenes en IPFS. Requiere revisión legal
   previa de la combinación pago+azar+premio (DGOJ) — en la primera versión
   el NFT debe presentarse como recuerdo digital no transferible, sin
   mercado interno ni promesa de valor económico, hasta tener esa revisión.
5. **Fase 4 — Optimización de coste**: modelo barato para diálogo
   rutinario + Sonnet reservado para generación de caso/contradicciones/
   acusación/desenlace, prompt caching de Bedrock para la descripción del
   caso (se repite cada turno).

## Fase 1 — SaaS de pago: plan detallado

### 1. Reestructuración de carpetas

Layout objetivo en la raíz del repo:

```
AgentCluedo/
  console/                # el juego actual, autocontenido
    main.py                # entrypoint recortado (wiring + game_loop.run_game)
    game_loop.py            # NUEVO: el bucle while/input/print, movido fuera de GameManager
    run.sh, run.bat
    requirements.txt, pyproject.toml, uv.lock
    settings/               # sin cambios internos
    test/                   # movido tal cual (hoy vacío)
  engine/                  # NUEVO paquete compartido de nivel superior
    pyproject.toml          # paquete instalable "cluedo-engine"
    cluedo_engine/
      game_manager.py        # de agents/game_manager.py, sin I/O ni settings
      llm_factory.py          # + rama "bedrock"
      detective_agent.py
      bases/ (base_agent.py, agent_response.py)
      utils/prompt_loader.py  # resuelve prompts relativos al propio paquete
      prompts/ (mayordomo.md, heredera.md)
      models/turn_result.py   # NUEVO: AgentTurnResult
  api/                     # NUEVO backend FastAPI (ver §4)
  web/                     # placeholder; build real en Fase 1.5
  infra/                   # notas de recursos/IAM, sin código IaC ejecutado aquí
```

Decisiones sobre las piezas ambiguas:
- **`UI/console/*.py` y `minigames/*.py`: se eliminan, no se mueven.** Están
  importados en `main.py` pero cada llamada real está comentada
  (`main.py:11-18`); `MenuConsola` está roto/incompleto. Hay que quitar
  también los 4 imports muertos al recortar `console/main.py`.
- **`settings/utils/api_limits.py`**: se queda tal cual en
  `console/settings/utils/` (stub muerto, nunca invocado, sin clave
  `api_limits` en `config.json`) — no se toca en la Fase 1; el límite real
  por usuario/sesión se construye desde cero en `api/services/` (§4), no
  resucitando este stub.

**Cambios necesarios en `run.sh` / `run.bat` por el movimiento:** ambos ya
usan rutas relativas al propio script, así que moverlos dentro de
`console/` no rompe nada; solo hace falta añadir, en el mismo punto donde
hoy instalan `requirements.txt`, una instalación editable del paquete
compartido (`uv pip install -e "$SCRIPT_DIR/../engine" --python "$PYTHON_BIN" --no-cache`
en bash, equivalente en batch) y extender el chequeo de venv-corrupto para
que también haga `import cluedo_engine`. El resto (chequeo de Ollama,
bootstrap de `.env`, `PYTHONUTF8`/`OLLAMA_HOST`) no cambia.

### 2. Desacoplar el motor de la I/O de consola

**Decisión clave: `engine/` es un paquete de nivel superior, hermano de
`console/` y `api/`, no anidado dentro de `console/`.** Si viviera en
`console/engine/`, `api/` tendría que importar del árbol de otra app
(violación de capas) y su build de Docker tendría que arrastrar el
`settings/`/`.env` local de consola sin necesidad. Con `engine/` como
paquete instalable propio (`pip install -e ../engine`), tanto `console/`
como `api/` lo instalan de forma independiente en sus propios venvs/imágenes.

Cambios en `game_manager.py` (movido a `engine/cluedo_engine/game_manager.py`):
- El constructor recibe el `llm` ya construido como parámetro, en vez de
  llamar a `get_llm()` internamente (que hoy lee el singleton `settings`
  directamente — el motor no debe importar `settings/` en absoluto).
- El bloque de `run_game()` que hoy hace `self.detective.invoke(...)` +
  imprime + actualiza `chat_history` (`agents/game_manager.py:166-189`) se
  convierte en un método nuevo `step(human_input: str) -> AgentTurnResult`
  que hace lo mismo pero devuelve el resultado en vez de imprimirlo.
- **Bug real a corregir de paso, no solo mover:** hoy `acusar()`
  (`agents/game_manager.py:114-120`) devuelve un string de victoria/derrota
  pero nada detiene el bucle — sigue pidiendo turnos después de una
  acusación correcta. Se añade `self.game_over` / `self.game_result` que
  `step()` traduce a `AgentTurnResult.is_game_over` / `.result`. La API
  necesita esta señal real para cerrar la sesión en DynamoDB y dejar de
  aceptar turnos/créditos.
- Nuevo `start_case() -> str` con el texto de briefing (hoy hardcodeado al
  principio de `run_game()`), reutilizable por consola y API sin duplicar
  el copy.

Nuevo `engine/cluedo_engine/models/turn_result.py`:
```python
class AgentTurnResult(BaseModel):
    final_response: str
    observations: list[str] = []
    is_game_over: bool = False
    result: Literal["won", "lost"] | None = None
```

`console/game_loop.py` (nuevo) contiene el bucle `while True` de hoy casi
igual, pero llamando a `gm.step(human_input)` y pintando los campos del
`AgentTurnResult` con `print()`, comprobando `result.is_game_over` para
salir. `console/main.py` solo hace el wiring settings→engine y llama a
`game_loop.run_game(gm)`.

`prompt_loader.py` deja de depender de `settings.prompt_path` (una ruta
relativa que solo funciona si el CWD es la raíz del repo) y resuelve los
prompts relativos a la ubicación del propio paquete instalado.

### 3. Bedrock como nuevo proveedor

`llm_factory.py` pasa a recibir parámetros en vez de leer `settings`
directamente:
```python
def get_llm(provider: str, *, ollama_model=None, openai_api_key=None,
            bedrock_model_id=None, aws_region=None, aws_profile=None) -> BaseChatModel
```
- Ramas `ollama`/`openai`: igual que hoy, parametrizadas.
- Rama `bedrock` nueva: `from langchain_aws import ChatBedrock` importado
  **dentro** de la rama (no a nivel de módulo), para que `console/` no
  necesite `langchain-aws`/`boto3` instalados. `aws_profile` solo se pasa
  si está definido (dev local vía `~/.aws/credentials`); en producción el
  rol IAM de la tarea ECS da las credenciales automáticamente.
- Paquete: **`langchain-aws`**, no `boto3` directo — mantiene
  `llm.with_structured_output(AgentResponse)` (`base_agent.py:21`)
  funcionando sin cambios, al ser parte de la interfaz `BaseChatModel`.
- `engine/pyproject.toml`: `langchain-aws` como **extra opcional**
  (`cluedo-engine[bedrock]`), no dependencia dura — `console/` sigue ligero.
- IAM: el rol de la tarea ECS necesita `bedrock:InvokeModel` acotado al/los
  ARN de modelo/inference-profile concretos (detalle de `infra/`).
- Split de modelo barato/Sonnet de la visión original: **se difiere**. Se
  deja preparado el hueco (`GameManager(llm, reasoning_llm=None)`,
  `reasoning_llm` por defecto = `llm`) pero no se activa hasta tener datos
  reales de uso/coste que justifiquen qué llamadas necesitan el modelo caro.
- Prompt caching de Bedrock: verificar la superficie exacta de la API en
  `langchain-aws` en el momento de implementar; no bloquea la Fase 1.

### 4. Backend FastAPI mínimo (`api/`)

Layout: `api/main.py`, `api/routers/{games,billing}.py`,
`api/services/{session_store,credit_ledger,stripe_client}.py`,
`api/deps.py` (dependencia de auth), `api/config.py`, `api/Dockerfile`.

Endpoints mínimos:
- `POST /v1/games` — inicia caso: descuenta 1 crédito de forma atómica en
  DynamoDB (`UpdateItem` con `ConditionExpression="credits_balance > :zero"`
  para evitar doble gasto por condición de carrera), crea `GameManager`
  con el LLM de Bedrock, llama a `start_case()`, guarda la sesión, devuelve
  `{game_id, briefing}`.
- `POST /v1/games/{game_id}/turns` — body `{"input": str}`. Carga la sesión
  de DynamoDB, **reconstruye** un `GameManager` fresco (el `AgentExecutor`
  de LangChain no es serializable, solo `chat_history` se persiste),
  restaura el historial, llama a `step()`, persiste el resultado, devuelve
  el `AgentTurnResult`. Si `is_game_over`, marca el estado `won`/`lost` (sin
  devolver el crédito en ningún caso).
- `GET /v1/games/{game_id}` — estado actual (para reanudar/recargar).
- `POST /v1/billing/checkout-session`, `POST /v1/billing/webhook`,
  `GET /v1/billing/credits` — ver §5.
- `GET /healthz` — 200 trivial para el target group del ALB.

**Persistencia — DynamoDB obligatorio ya en la Fase 1, no aplazable.** Un
diccionario en memoria no vale: las tareas ECS Fargate reinician y pueden
escalar a N instancias detrás de un ALB, así que el segundo turno de un
usuario puede caer en una instancia distinta sin memoria compartida. Tres
tablas pequeñas (no single-table, no se justifica todavía):
- **`games`**: PK `game_id`; `user_id`, `status` (`active|won|lost`),
  `chat_history` (JSON), `created_at`, `updated_at`, `model_provider`, TTL
  para expirar sesiones abandonadas.
- **`users`**: PK `user_id`; `credits_balance` (Number), `email`,
  `created_at`.
- **`processed_stripe_events`**: PK `event_id` (solo para idempotencia,
  ver §5).

### 5. Integración con Stripe

- **Creación de Checkout Session**: `stripe.checkout.Session.create(mode="payment", line_items=[...], success_url=..., cancel_url=..., client_reference_id=user_id, metadata={"user_id":..., "credit_pack":...})`.
  Apple Pay/Google Pay aparecen solos en Stripe Checkout una vez activados
  y verificado el dominio en el Dashboard — configuración, no código.
- **Webhook** (`POST /v1/billing/webhook`) — trampa clásica de FastAPI: hay
  que leer el body **crudo** (`await request.body()`) antes de que
  cualquier parseo pydantic lo toque, y pasar esos bytes + la cabecera
  `Stripe-Signature` a `stripe.Webhook.construct_event(...)`. La ruta no
  debe declarar un modelo de body pydantic (rompería la verificación de
  firma).
- **Idempotencia:** Stripe puede reenviar el mismo evento. Antes de
  acreditar, `PutItem` condicional en `processed_stripe_events` con
  `ConditionExpression="attribute_not_exists(event_id)"`; si falla, el
  evento ya se procesó — no se acredita de nuevo, se responde 200 igual.
- **Ledger de créditos:** en `checkout.session.completed`, se lee
  `client_reference_id` (user_id) y se busca los créditos comprados en un
  mapeo `price_id → créditos` mantenido en el servidor (no fiarse solo de
  metadata del cliente) — luego `UpdateItem` en `users`:
  `ADD credits_balance :n`.

### 6. Autenticación

Recomendación: **magic-link por email**, no Cognito, para la Fase 1.
Cognito exige UI alojada o SDK propio, verificación de email, middleware
de validación JWT vía JWKS e IaC de user pool antes de poder demostrar un
solo pago — nada de eso hace falta para probar el bucle pago→crédito→juego.
- `POST /v1/auth/request-link {email}` — firma un token de corta duración
  con el email, envía el enlace.
- `GET /v1/auth/verify?token=...` — valida, crea/actualiza el usuario en
  `users`, emite un token de sesión (JWT/cookie firmada).
- `api/deps.py::get_current_user` valida ese token en rutas protegidas.
- **Atajo de desarrollo:** con `AUTH_DEV_MODE=true`, `request-link` devuelve
  el token directamente en la respuesta (sin enviar email), para poder
  probar todo el flujo por curl antes de tener proveedor de email.
- Decisión abierta: proveedor de email — SES encaja mejor a largo plazo
  pero tiene sandbox/verificación de dominio; un tercero (Postmark/Resend/
  SendGrid) puede desbloquear pruebas locales antes.

### 7. Alcance del frontend en la Fase 1

**Recomendación: sin React todavía en la Fase 1 — el framework completo
(S3+CloudFront) se deja para la Fase 1.5 — pero SÍ una página HTML estática
mínima, obligatoria, no opcional.** Construir el React completo antes de
que el contrato de la API se estabilice arriesga rehacer la integración
cuando cambien los endpoints durante la iteración del backend; pero cerrar
la Fase 1 sin nada clicable rompe la regla de "cada fase termina en una
demo jugable" (ver arriba). La solución intermedia: un único fichero
`api/static/demo.html` (sin build step, JS plano) servido por el propio
FastAPI, con:
- Un formulario de email → `POST /v1/auth/request-link` (en `AUTH_DEV_MODE`
  muestra el token directamente, sin esperar correo).
- Un botón "Comprar créditos" → `POST /v1/billing/checkout-session` →
  redirige al Checkout alojado por Stripe (modo test).
- Tras el pago, un botón "Nuevo caso" → `POST /v1/games` → muestra el
  briefing.
- Un cuadro de texto + botón "Enviar" → `POST /v1/games/{id}/turns` →
  pinta `final_response`/`observations`, y si `is_game_over`, el resultado.

Esto es la demo de la Fase 1: tosca, sin estilos, pero jugable de extremo a
extremo en un navegador por cualquiera, no solo por quien sepa usar curl.
La Fase 1.5 sustituye este HTML suelto por el React real sin cambiar nada
del backend.

### 8. Secretos y configuración

**A AWS Secrets Manager** (rotables, sensibles): clave secreta de Stripe +
secreto de firma del webhook; secreto de firma de los tokens de
magic-link; clave del proveedor de email si aplica.

**Se quedan como variables de entorno / parámetros de la task definition**
(no sensibles): `AWS_REGION`, `BEDROCK_MODEL_ID`, nombres de tablas,
mapeo `STRIPE_PRICE_ID_* → créditos`, `LOG_LEVEL`.

**El patrón de `settings/settings.py` se bifurca a propósito, no se
unifica.** `console/settings/settings.py` mantiene su forma actual
(singleton, `config.json` + `.env` local) porque es correcta para
desarrollo interactivo. `api/` tiene su propio `api/config.py` (env vars
puras / pydantic-settings) porque ECS inyecta las variables (incluidas las
resueltas desde Secrets Manager) directamente en el proceso — no hay
`.env` en ese entorno, y forzar uno sería una violación artificial de
12-factor. Es una divergencia deliberada, no algo por unificar.

**Aviso aparte (no se toca en esta fase, pero se marca):**
`settings/.env_example` contiene un valor de `LANGCHAIN_API_KEY` con pinta
de clave real, no de placeholder — conviene rotarla y limpiar el fichero
de ejemplo independientemente de esta reestructuración.

### 9. Orden de construcción sugerido

**Revisado (2026-08-09):** el usuario quiere posponer crear/tocar la cuenta
AWS todo lo posible, desarrollando y depurando en local con herramientas
gratuitas hasta tener la demo lo más completa posible antes de "subirlo".
Como `get_llm()` ya es un factory intercambiable, no hay ninguna razón
técnica para que Bedrock vaya antes que el resto — se mueve al final,
justo antes de la primera necesidad real de AWS. Todo lo demás (FastAPI,
DynamoDB Local, Stripe test mode, magic-link) es gratis y no requiere
cuenta AWS:

1. ✅ Reestructura mecánica (§1).
2. ✅ Extracción del motor (§2).
3. Construir `api/` en local (uvicorn) contra **DynamoDB Local** (Docker,
   sin cuenta AWS — es solo una imagen Docker) usando **Ollama** (no
   Bedrock todavía) como LLM vía `cluedo_engine.llm_factory.get_llm`;
   implementar `/v1/games` + `/v1/games/{id}/turns` de extremo a extremo
   con un usuario de auth-dev-mode.
4. Añadir magic-link en modo dev (§6) — sigue todo en local y gratis.
5. Añadir Stripe en modo TEST (§5, gratis — no requiere tarjeta real ni
   cuenta de pago, solo una cuenta Stripe gratuita), usando `stripe listen
   --forward-to localhost:.../v1/billing/webhook` para firmar webhooks en
   local. Mientras el usuario no tenga aún sus claves de prueba de Stripe,
   la demo usa un endpoint de "conceder créditos" solo-dev (gateado por
   `AUTH_DEV_MODE`) para no bloquear el resto.
6. **Checkpoint de demo jugable de la Fase 1:** `api/static/demo.html`
   (§7) servido desde FastAPI. Recorrido completo desde el navegador:
   email → créditos (Stripe test o el atajo dev) → nuevo caso → varios
   turnos vía Ollama → acusación → resultado. Esto es "Fase 1 terminada"
   en local, cero coste, cero cuenta AWS.
7. Solo ahora, con todo lo demás ya probado: añadir la rama Bedrock (§3)
   y probarla a mano contra una cuenta AWS real vía perfil personal — sin
   ECS todavía. Primer punto que toca AWS real, pero solo un perfil CLI
   acotado a `bedrock:InvokeModel`, y deliberadamente el último paso antes
   de necesitar AWS de verdad.
8. Primer aprovisionamiento AWS real: crear las tablas DynamoDB y las
   entradas de Secrets Manager de verdad; apuntar el `api/` local (aún en
   local) a esos recursos reales — valida permisos IAM/esquemas antes de
   containerizar.
9. Containerizar `api/` (`Dockerfile`), probar con `docker run` contra
   esos mismos recursos AWS reales — valida la imagen antes de tocar ECS.
10. Desplegar en ECS (Fargate o "Express Mode" — decidir aquí, no afecta al
    código de la app) detrás de un ALB con la task definition real (env
    vars + referencias a Secrets Manager + rol IAM de la tarea). El
    `demo.html` del paso 6 queda servido también en producción.
11. Pasar Stripe a modo live (nuevo secreto de webhook, price IDs reales)
    solo una vez validado el paso 10 en modo test contra el servicio ya
    desplegado.
12. Solo con 1–11 sólidos: empezar Fase 1.5 (frontend React que sustituye
    a `demo.html`) / Fase 2 (imágenes) / Fase 3 (NFTs).

Resultado: los pasos 3-6 (backend, auth, pagos de prueba, demo jugable)
son enteramente locales y gratuitos — AWS no aparece hasta el paso 7, y
solo como un perfil personal de prueba, no como aprovisionamiento real
(eso queda en el paso 8). 10 de los 12 pasos no tocan AWS en absoluto.

### Decisiones abiertas (no se asumen, se preguntan cuando toque implementar)

- ID(s) exactos de modelo Bedrock para Claude, y si la región objetivo
  necesita un inference profile cross-region (`us.anthropic.claude-*`) en
  vez de un model id simple.
- Precios/tamaños de los paquetes de créditos (define los `Price` de
  Stripe y el mapeo `price_id → créditos`).
- Proveedor de email para magic-link: SES vs Postmark/Resend/SendGrid.
- Fargate vs ECS "Express Mode" — solo afecta a `infra/`, se puede decidir
  tan tarde como el paso 10 del orden de construcción.

## Archivos críticos

- `agents/game_manager.py` → base para `engine/cluedo_engine/game_manager.py`
- `agents/llm_factory.py` → base para `engine/cluedo_engine/llm_factory.py`
- `agents/detective_agent.py`, `agents/bases/base_agent.py`,
  `agents/bases/agent_response.py`, `agents/utils/prompt_loader.py` →
  se mueven a `engine/cluedo_engine/` casi sin cambios de lógica
- `settings/settings.py` → se queda en `console/`, patrón NO se reutiliza
  en `api/` (config propia, ver §8)
- `main.py` → se recorta a `console/main.py` + nuevo `console/game_loop.py`
- `run.sh`, `run.bat` → se mueven a `console/`, +1 línea de instalación
  editable del engine cada uno
- `UI/console/*.py`, `minigames/*.py` → se eliminan (código muerto)

## Verificación

- **Fase 1, paso 1-2**: tras la reestructura y la extracción del motor,
  jugar una partida completa por consola (`console/run.bat` o `run.sh`)
  con Ollama, incluyendo una acusación correcta e incorrecta, y confirmar
  que el comportamiento (texto, flujo, fin de partida) es idéntico al
  actual — más el fix de que el juego ahora sí termina tras acusar.
- **Fase 1, paso 3**: con `uvicorn` local + DynamoDB Local (Docker) +
  Ollama, recorrer por curl/Postman: crear usuario dev → `POST /v1/games`
  → varios `POST /v1/games/{id}/turns` → acusación → `is_game_over=true`
  con el resultado correcto.
- **Fase 1, paso 4-5**: añadido magic-link (modo dev) y Stripe test mode
  (o el atajo de conceder créditos en dev mientras no haya claves de
  Stripe todavía): pedir enlace → conseguir créditos → jugar, todo por
  curl/Postman.
- **Fase 1, paso 6 (checkpoint de demo)**: repetir ese mismo recorrido
  pero desde `api/static/demo.html` en el navegador, sin curl — email,
  créditos, caso, turnos, acusación y resultado, todo clicable. Esto es
  lo que se prueba "ahora" en local, sin AWS.
- **Fase 1, paso 7**: probar la rama Bedrock de `llm_factory.get_llm()` con
  un script suelto o test manual contra una cuenta AWS real (perfil
  personal), confirmando respuesta válida de `ChatBedrock`, y luego el
  mismo recorrido del paso 6 pero con Bedrock en vez de Ollama.
- **Fase 1, paso 8-10**: repetir el recorrido completo otra vez contra
  recursos AWS reales (tablas/Secrets Manager reales), luego contenedor
  local, luego el servicio ya desplegado en ECS tras el paso 10 —
  incluyendo abrir `demo.html` contra la URL pública del ALB.
