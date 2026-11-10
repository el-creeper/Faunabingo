import sqlite3
import uuid
import hashlib
# Importe la fonction de ton code FastAPI qui gère le chiffrement des mots de passe (ex: bcrypt/passlib)
# from auth import get_password_hash (à adapter selon le nom de ton fichier)

email_clair = "google@faunabingo.fr"
# Exemple de chiffrement si ton email est géré en SHA-256 :
email_hash = hashlib.sha256(email_clair.lower().encode()).hexdigest()

# Utilise ta fonction de chiffrement pour générer le hash du mot de passe :
# mdp_hash = get_password_hash("GoogleTest2026!")
mdp_hash = "COLLE_ICI_LE_HASH_GENERE"

with sqlite3.connect("database/bingo_faune.db") as conn:
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Participant (id_participant, prenom, email_hash, mot_de_passe_hash, score_total)
        VALUES (?, ?, ?, ?, ?)
    """, (str(uuid.uuid4()), 'Google', email_hash, mdp_hash, 0))
    conn.commit()
    print("Compte de test inséré avec succès !")