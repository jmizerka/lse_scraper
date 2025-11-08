FROM python:3.12-slim

WORKDIR /app

COPY cron/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && playwright install chromium

COPY core/ ./core
COPY cron/ ./
COPY ./utils /app/utils
