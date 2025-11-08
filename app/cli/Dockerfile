FROM python:3.12-slim

WORKDIR /app

COPY cli/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && playwright install chromium

COPY core/ ./core
COPY cli/ ./
COPY ./utils /app/utils
