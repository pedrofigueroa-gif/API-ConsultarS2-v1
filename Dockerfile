FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production \
    HOST=0.0.0.0 \
    PORT=8080 \
    APP_RELOAD=false

WORKDIR /app

COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt \
    && useradd --system --uid 10001 --create-home appuser

COPY app ./app
COPY main.py ./main.py

USER appuser
EXPOSE 8080
CMD ["python", "main.py"]
