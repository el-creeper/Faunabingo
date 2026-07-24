#!/bin/bash

# 1. On prépare les vrais dossiers dans le disque dur de sauvegarde
mkdir -p /app/data/database
mkdir -p /app/data/static

# 2. On copie toutes les images et fichiers de style vers la sauvegarde
cp -rn static/* /app/data/static/ 2>/dev/null || true

# 3. On supprime les dossiers d'origine
rm -rf database
rm -rf static

# 4. On crée des raccourcis globaux
ln -s /app/data/database database
ln -s /app/data/static static

# 5. On initialise la base de données et on lance le serveur
python init_db.py
uvicorn main:app --host 0.0.0.0 --port $PORT