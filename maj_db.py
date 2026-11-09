import sqlite3

DB_NAME = "database/bingo_faune.db"

# Dictionnaire des remplacements : {"Ancien nom": "Nouveau nom"}
remplacements = {
    "Mygale à genoux rouges": "Mygale zebree",
    "Gecko casque": "Gecko des maisons",
    "Serpent liane": "Serpent liane vert"
}

# Dictionnaire pour les ID (au cas où tes id_espece sont basés sur le nom de l'image)
# Ex: Mygale_a_genoux_rouges -> Mygale_zebree
remplacements_ids = {
    "Mygale_a_genoux_rouges": "Mygale_zebree",
    "Gecko_casque": "Gecko_des_maisons",
    "Serpent_liane": "Serpent_liane_vert"
}


def mettre_a_jour_db():
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            
            # 1. Mise à jour des noms courants dans la table Espece
            for ancien, nouveau in remplacements.items():
                cursor.execute("""
                    UPDATE Espece 
                    SET nom_courant = ? 
                    WHERE nom_courant = ?
                """, (nouveau, ancien))
                
                modifs = cursor.rowcount
                print(f"Espèce : '{ancien}' renommée en '{nouveau}' ({modifs} modifiée).")

            # 2. Mise à jour des IDs (id_espece) dans Espece et Observation
            for ancien_id, nouveau_id in remplacements_ids.items():
                
                # Mise à jour dans Espece (id_espece et image_reference au cas où)
                cursor.execute("""
                    UPDATE Espece 
                    SET id_espece = ?, image_reference = ? 
                    WHERE id_espece = ?
                """, (nouveau_id, nouveau_id, ancien_id))
                
                # Mise à jour dans Observation (pour que les joueurs gardent la découverte)
                cursor.execute("""
                    UPDATE Observation 
                    SET id_espece = ? 
                    WHERE id_espece = ?
                """, (nouveau_id, ancien_id))
                
                modifs_obs = cursor.rowcount
                print(f"ID Espèce : '{ancien_id}' -> '{nouveau_id}' ({modifs_obs} observation(s) joueur(s) transférée(s)).")
            
            conn.commit()
            print("\n✅ Base de données mise à jour avec succès !")
            
    except Exception as e:
        print(f"❌ Une erreur est survenue : {e}")

if __name__ == "__main__":
    mettre_a_jour_db()