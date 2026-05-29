# backend/main.py — BeninScope / TERROIR
# Lancement : uvicorn backend.main:app --reload --port 8000
# (depuis la racine du projet : benin_insights_challenge/)

import sys
import logging
from pathlib import Path
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

log = logging.getLogger("terroir.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Démarre le poller GDELT live au lancement, l'arrête à la fermeture."""
    try:
        from backend.services.gdelt_live_poller import start_background_poller
        start_background_poller()
        log.info("Poller GDELT live démarré.")
    except Exception as exc:
        log.warning(f"Poller GDELT non démarré (offline ?) : {exc}")
    yield

# ── Résolution des chemins ──────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR  = Path(__file__).resolve().parent
STATIC_DIR   = BACKEND_DIR / "static"

# Rendre le package backend importable depuis n'importe où
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ── Application ────────────────────────────────────────────────────────────
app = FastAPI(
    title="BeninScope — TERROIR API",
    description="Veille territoriale et signalement citoyen — Bénin 2025",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# ── CORS ────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ─────────────────────────────────────────────────────────────────
from backend.routers.health    import router as health_router
from backend.routers.stats     import router as stats_router
from backend.routers.events    import router as events_router
from backend.routers.stt       import router as stt_router
from backend.routers.incidents import router as incidents_router
from backend.routers.gdelt     import router as gdelt_router

app.include_router(health_router)
app.include_router(stats_router)
app.include_router(events_router)
app.include_router(stt_router)
app.include_router(incidents_router)
app.include_router(gdelt_router)

# ── Fichiers statiques (frontend) ───────────────────────────────────────────
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.get("/", include_in_schema=False)
    def root():
        index = STATIC_DIR / "index.html"
        if index.exists():
            return FileResponse(str(index))
        return {"message": "BeninScope TERROIR — frontend en construction"}
else:
    @app.get("/", include_in_schema=False)
    def root():
        return {"message": "BeninScope TERROIR API", "docs": "/api/docs"}


# ── Lancement direct ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
