FROM python:3.11-slim

WORKDIR /app

# Copier requirements et installer toutes les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier l'application
COPY . .

# Exposer le port
EXPOSE 10300

# Lancer FastAPI
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "10300"]

