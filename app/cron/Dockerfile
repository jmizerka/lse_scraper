FROM app-base:latest

WORKDIR /app

COPY app/cron/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/core ./core
COPY app/utils ./utils
COPY app/cron ./cron

CMD ["python", "-m", "cron.entrypoint"]
