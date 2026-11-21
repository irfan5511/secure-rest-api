FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt ./
RUN python -m pip install \
    --no-cache-dir \
    --index-url https://pypi.org/simple \
    --timeout 60 \
    --retries 3 \
    -r requirements.txt

COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini ./alembic.ini

RUN useradd --create-home --uid 10001 appuser
USER appuser

EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
