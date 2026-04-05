# ── Base image ────────────────────────────────────────────────────────────────
FROM python:3.11-slim

# Labels
LABEL maintainer="Email Triage Meta Hackathon"
LABEL description="Email Triage OpenEnv — FastAPI evaluation server"

# ── System deps ───────────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
 && rm -rf /var/lib/apt/lists/*

# ── Working directory ─────────────────────────────────────────────────────────
WORKDIR /app

# ── Python deps (cached layer) ────────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# ── Application code ──────────────────────────────────────────────────────────
COPY . .

# ── Environment variables ─────────────────────────────────────────────────────
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# HuggingFace Spaces environment variables (set in Space settings)
ENV API_BASE_URL=""
ENV MODEL_NAME=""
ENV HF_TOKEN=""
ENV OPENAI_API_KEY=""

# ── Expose port 7860 (REQUIRED for Hugging Face Spaces) ─────────────────────
EXPOSE 7860

# ── Health check ──────────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:7860/healthz || exit 1

# ── Start server on 7860 ──────────────────────────────────────────────────────
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7860"]
