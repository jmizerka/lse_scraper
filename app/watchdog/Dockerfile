FROM app-base:latest

WORKDIR /app

COPY app/watchdog/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/core ./core
COPY app/utils ./utils
COPY app/watchdog ./watchdog

CMD ["python", "-m", "watchdog.entrypoint"]
