# ======================
# 🐍 FastAPI Dockerfile
# ======================
FROM python:3.11-slim

WORKDIR /app

# Instala dependencias del sistema
RUN apt-get update && apt-get install -y libpq-dev gcc

# Copia los archivos del proyecto
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
