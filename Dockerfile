# =====================================================================
# Dockerfile para Django + SQLite + xhtml2pdf (e-cadempresas)
# Projeto: settings (raiz)  |  Django 6.0  |  Python 3.13
# Settings: settings  |  WSGI: wsgi:application
# Banco: SQLite em volume persistente (/app/data via SQLITE_PATH)
# =====================================================================

# ---------------------- Estágio de BUILD ----------------------------
FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

# Compiladores/deps para pacotes sem wheel (pycairo, reportlab, lxml, freetype)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    libcairo2-dev \
    libfreetype1-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

# ---------------------- Estágio FINAL (leve) ------------------------
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SQLITE_PATH=/app/data/db.sqlite3

WORKDIR /app

# Runtime: cairo/freetype (PDF) + libxml (lxml)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcairo2 \
    libfreetype6 \
    libfontconfig1 \
    libxml2 \
    libxslt1.1 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local

COPY . .

# Volume do banco SQLite + static_root + logs
RUN mkdir -p /app/data static_root logs

EXPOSE 8000

# Entry: mkdir do volume + migrações + collectstatic + gunicorn
CMD ["sh", "-c", "\
    mkdir -p /app/data && \
    python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput && \
    gunicorn wsgi:application \
      --bind 0.0.0.0:8000 \
      --workers ${GUNICORN_WORKERS:-2} \
      --timeout ${GUNICORN_TIMEOUT:-120} \
      --access-logfile - \
      --error-logfile -"]
