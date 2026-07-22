import sqlite3
import uuid
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import admin, jeu

app = FastAPI(title="FaunaBingo")
app.mount("/static", StaticFiles(directory="static"), name="static")
DB_NAME = "database/bingo_faune.db"

def inserer_donnees_test():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM Espece")
            if cursor.fetchone()[0] == 0:
                # Ajout des deux scores à la fin : (..., points_vu, points_photo)
                especes_test = [
                    (str(uuid.uuid4()), "Quetzal resplendissant", "Pharomachrus mocinno", "Oiseau", "Trogonidae", 5, 18, 40, "Vert, Rouge", 50, 100),
                    (str(uuid.uuid4()), "Singe capucin", "Cebus capucinus", "Mammifère", "Cebidae", 30, 160, 45, "Noir, Blanc", 20, 40),
                    (str(uuid.uuid4()), "Iguane vert", "Iguana iguana", "Reptile", "Iguanidae", 20, 90, 150, "Vert, Gris", 10, 25)
                ]
                cursor.executemany("""
                    INSERT INTO Espece (id_espece, nom_courant, nom_scientifique, classe, famille, 
                                        longevite_annees, reproduction_jours, taille_cm, couleurs_principales, points_vu, points_photo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, especes_test)
                conn.commit()
        except sqlite3.OperationalError:
            pass

@app.on_event("startup")
def startup_event():
    inserer_donnees_test()

# --- BRANCHEMENT DES ROUTEURS ---
app.include_router(admin.router)
app.include_router(jeu.router)