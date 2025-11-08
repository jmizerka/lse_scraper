FROM app-base:latest

WORKDIR /app

COPY app/cli/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/core ./core
COPY app/utils ./utils
COPY app/cli ./cli

CMD ["python", "-m", "cli.entrypoint"]
