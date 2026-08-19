FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# `ask.py` sans argument ouvre le mode interactif.
# Monter les cours et la base : -v ./mes_cours:/app/mes_cours -v ./vector_db:/app/vector_db
ENTRYPOINT ["python", "ask.py"]
