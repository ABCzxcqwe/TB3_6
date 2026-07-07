"""
Backend web del Centro de Eventos - TB4 (1ACC0271)

Ejecutar desde la RAIZ del proyecto (donde están servicios.py, repositorios.py, etc.):
    uvicorn backend.app:app --reload --port 8000

Luego abrir http://localhost:8000/docs para ver y probar todos los endpoints
(evidencia automática de funcionamiento para el informe).

Requiere: pip install fastapi uvicorn requests
Requiere Ollama corriendo localmente: `ollama serve`  y un modelo descargado,
ej: `ollama pull llama3`
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import CORS_ORIGINS
from backend.routers import ambientes, reservas, asistente

app = FastAPI(
    title="Centro de Eventos - API (Caso 6)",
    description="Backend web del sistema de gestión de reservas, "
                "con CRUD de ambientes y asistente de IA generativa (Ollama).",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ambientes.router)
app.include_router(reservas.router)
app.include_router(asistente.router)

# Sirve el frontend estático (frontend/index.html, app.js, style.css, etc.)
app.mount("/app", StaticFiles(directory="frontend", html=True), name="frontend")


@app.get("/", tags=["Salud"])
def salud():
    return {"status": "ok", "mensaje": "API del Centro de Eventos corriendo. Ver /docs"}