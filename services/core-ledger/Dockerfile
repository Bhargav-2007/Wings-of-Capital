FROM python:3.12-slim
WORKDIR /app
ENV PYTHONPATH=/app

RUN groupadd -g 1000 app && useradd -m -u 1000 -g 1000 app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=app:app . .

USER app
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
