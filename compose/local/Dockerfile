FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements /app/requirements

RUN apk update && apk add libmagic

RUN python -m pip install --no-cache-dir --upgrade pip && \
  python -m pip install --no-cache-dir -r /app/requirements/local/requirements.txt

COPY . /app

# Copy and prepare the startup scripts
RUN cp /app/compose/local/commands/start-celery /start-celery && \
  sed -i 's/\r$//g' /start-celery && \
  chmod +x /start-celery

WORKDIR /app
