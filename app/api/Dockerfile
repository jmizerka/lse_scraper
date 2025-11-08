FROM app-base:latest

WORKDIR /app

COPY app/api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/core ./core
COPY app/utils ./utils

COPY app/api ./api

CMD ["uvicorn", "api.entrypoint:app", "--host", "0.0.0.0", "--port", "8000"]
