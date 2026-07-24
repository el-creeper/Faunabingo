#!/bin/bash

# 1. On copie les photos initiales vers le disque dur de sauvegarde
cp -rn static/images/. /app/data/ 2>/dev/null || true

# 2. On supprime les dossiers locaux et on crée les ponts vers la sauvegarde
rm -rf database static/images
mkdir -p static
ln -s /app/data database
ln -s /app/data static/images

# 3. On initialise la base de données
python init_db.py

# 4. On lance l'application
uvicorn main:app --host 0.0.0.0 --port $PORT