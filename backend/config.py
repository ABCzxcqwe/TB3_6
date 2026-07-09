import os

# ── Configuración de Ollama ────────────────────────────────────
# Sigue el patrón indicado por el profesor: .env con OLLAMA_URL,
# OLLAMA_MODEL y OLLAMA_API_KEY (funciona tanto con Ollama local
# como con Ollama Cloud - https://ollama.com).
#
# Ejemplo .env para Ollama Cloud:
#   OLLAMA_URL=https://ollama.com/api
#   OLLAMA_MODEL=gpt-oss:20b
#   OLLAMA_API_KEY=TU_API_KEY
#
# Ejemplo .env para Ollama local:
#   OLLAMA_URL=http://localhost:11434/api
#   OLLAMA_MODEL=llama3
#   OLLAMA_API_KEY=          (vacío, no hace falta)
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3")
OLLAMA_API_KEY = os.environ.get("OLLAMA_API_KEY", "")

if OLLAMA_API_KEY:
    OLLAMA_HEADERS = {"Authorization": "Bearer " + OLLAMA_API_KEY}
else:
    OLLAMA_HEADERS = {}

# ── CORS (para que el frontend en HTML/JS pueda llamar al backend) ─
CORS_ORIGINS = ["*"]  # en producción, restringir al dominio real