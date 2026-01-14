FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY compose/requirements.txt compose/requirements.txt
COPY compose/local/requirements.txt compose/local/requirements.txt

RUN pip install --no-cache-dir --upgrade
RUN pip install --no-cache-dir -r compose/local/requirements.txt


COPY . .

# EXPOSE 80

# CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]
