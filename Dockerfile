FROM python:3.12.3-slim

  WORKDIR /app

  COPY web/requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt

  COPY backend/ ./backend/
  COPY web/ ./web/
  COPY pyproject.toml .
  RUN pip install -e .

  ENV PYTHONUNBUFFERED=1
  ENV PYTHONDONTWRITEBYTECODE=1

  EXPOSE 8080

  CMD ["gunicorn", \
       "--bind", "0.0.0.0:8080", \
       "--workers", "2", \
       "--timeout", "300", \
       "--worker-class", "sync", \
       "--capture-output", \
       "web.app:app"]