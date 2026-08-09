from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from routers import auth, billing, games

app = FastAPI(title="AgentCluedo API")

app.include_router(auth.router)
app.include_router(games.router)
app.include_router(billing.router)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/")
def root():
    return RedirectResponse(url="/static/demo.html")
