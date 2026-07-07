import os

# ── Configuración de Ollama (IA generativa local) ─────────────
# El profesor indicó usar Ollama. Se asume que corre localmente
# con: `ollama serve`  y que el modelo ya fue descargado con
# `ollama pull llama3` (o el modelo que elijan).
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3")

# ── CORS (para que el frontend en HTML/JS pueda llamar al backend) ─
CORS_ORIGINS = ["*"]  # en producción, restringir al dominio real