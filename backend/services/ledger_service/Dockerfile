# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY backend/services/shared/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/services/shared /app/shared
COPY backend/services/ledger_service /app/ledger_service

ENV PYTHONUNBUFFERED=1
ENV APP_MODULE="ledger_service.main:app"
ENV PYTHONPATH="/app"

EXPOSE 8002

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8002/health')"

CMD ["uvicorn", "ledger_service.main:app", "--host", "0.0.0.0", "--port", "8002"]
