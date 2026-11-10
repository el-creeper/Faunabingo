import sqlite3
import uuid
import bcrypt
import hashlib
import os

# Si tu utilises un fichier .env pour ta clé EMAIL_PEPPER, on le charge ici
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def hacher_mot_de_passe(mot_de_passe: str) -> str:
    """Transforme 'mon_mot_de_passe' en une chaîne illisible unique"""
    mot_de_passe_bytes = mot_de_passe.encode('utf-8')
    sel = bcrypt.gensalt()
    hachage_bytes = bcrypt.hashpw(mot_de_passe_bytes, sel)
    return hachage_bytes.decode('utf-8')

def hacher_email(email: str) -> str:
    """
    Transforme l'email en hachage SHA-256 en y ajoutant une clé secrète (Pepper).
    """
    pepper = os.getenv("EMAIL_PEPPER", "cle_secrete_par_defaut_a_changer")
    email_propre = email.strip().lower()
    texte_a_hacher = email_propre + pepper
    return hashlib.sha256(texte_a_hacher.encode()).hexdigest()


# --- CRÉATION DU COMPTE ---
email_clair = "test_google@faunabingo.fr"
mdp_clair = "Google!Test2026"

print(f"Création du compte pour : {email_clair}")

email_hash = hacher_email(email_clair)
mdp_hash = hacher_mot_de_passe(mdp_clair)
id_participant = str(uuid.uuid4())

DB_NAME = "database/bingo_faune.db"

try:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Participant (id_participant, prenom, email_hash, mot_de_passe_hash, score_total)
            VALUES (?, ?, ?, ?, ?)
        """, (id_participant, 'Google', email_hash, mdp_hash, 0))
        conn.commit()
        print("✅ Compte de test inséré avec succès dans la base de données !")
        print(f"👉 Tu peux donner ces infos à la Play Console :")
        print(f"Email : {email_clair}")
        print(f"Mot de passe : {mdp_clair}")
        
except sqlite3.IntegrityError:
    print("ℹ️ Le compte existe déjà dans la base de données (email_hash en doublon).")
except Exception as e:
    print(f"❌ Une erreur est survenue : {e}")