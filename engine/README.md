# cluedo-engine

Motor de juego de AgentCluedo: `GameManager`, agentes sospechosos y el
detective. Sin I/O de consola ni dependencia de `settings/` — quien lo usa
(la consola en `console/`, la futura API en `api/`) construye el `llm` y se
lo pasa a `GameManager`.

Instalación editable desde otro proyecto del monorepo:

```
uv pip install -e ../engine
```
