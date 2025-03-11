# Étape 1 : Utiliser une image Python comme base
FROM python:3.9-slim

# Étape 2 : Définir le répertoire de travail
WORKDIR /app

# Étape 3 : Copier le fichier requirements.txt dans le conteneur
COPY requirements.txt .

# Étape 4 : Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Étape 5 : Copier le code source dans le conteneur
COPY . .

# Étape 6 : Exposer le port sur lequel l'application tourne
EXPOSE 8000

# Étape 7 : Lancer l'application FastAPI avec Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
