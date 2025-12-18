# apps/backend/Dockerfile
FROM python:3.12-slim-bookworm AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app
# 1. Copier les fichiers de définition (pour le cache layer)
COPY pyproject.toml uv.lock ./
COPY libs/shared-models ./libs/shared-models/
COPY apps/backend/pyproject.toml ./apps/backend/

# 2. Installer les dépendances (sans le code)
# --package permet de cibler uniquement le backend
RUN uv sync --frozen --no-install-project --package gen-tests-backend

# 3. Copier le code source
COPY libs/shared-models ./libs/shared-models
COPY apps/backend ./apps/backend

# 4. Installer le projet (code)
RUN uv sync --frozen --no-install-project --package gen-tests-backend

# --- Runtime Stage ---
FROM python:3.12-slim-bookworm
WORKDIR /app
# Copier l'environnement virtuel créé par uv
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/apps/backend /app/apps/backend
COPY --from=builder /app/libs /app/libs

ENV PATH="/app/.venv/bin:$PATH"
# Ensure python path sees the app
ENV PYTHONPATH="/app"

CMD ["uvicorn", "apps.backend.src.interfaces.http.api:app", "--host", "0.0.0.0"]
