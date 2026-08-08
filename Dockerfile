# ---- Base build stage ----
FROM python:3.12-slim AS base

WORKDIR /app

# Install system deps needed to build some python packages (kept minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# ---- Final runtime stage ----
FROM python:3.12-slim

WORKDIR /app

# Create a non-root user for security
RUN useradd -m appuser
COPY --from=base /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=base /usr/local/bin /usr/local/bin
COPY . .

USER appuser

EXPOSE 5000

ENV APP_VERSION=1.0.0

HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
