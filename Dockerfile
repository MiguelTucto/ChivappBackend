# ==========================================
# Dockerfile Multi-Stage - ChivApp Backend
# ==========================================

FROM python:3.12-slim AS builder

WORKDIR /app

# Instalar dependencias del sistema requeridas para compilar paquetes y soporte de PDFs
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ==========================================
# Etapa Final (Runner)
# ==========================================
FROM python:3.12-slim AS runner

WORKDIR /app

# Dependencias de tiempo de ejecución para postgres, imágenes y PDFs
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libjpeg62-turbo \
    zlib1g \
    libfreetype6 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario de seguridad no-root
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --gid 1001 appuser

# Copiar paquetes instalados desde el builder
COPY --from=builder /root/.local /home/appuser/.local

# Asegurar PATH para scripts instalados con pip --user
ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

# Copiar código fuente
COPY --chown=appuser:appgroup . /app

# Crear directorio para subidas locales y dar permisos a appuser
RUN mkdir -p /app/uploads && chown -R appuser:appgroup /app/uploads

USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8080}/health || exit 1

CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080} --workers 2"]
