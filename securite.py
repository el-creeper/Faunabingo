import hashlib
import os
from passlib.context import CryptContext

# Configuration de Bcrypt pour les mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 1. GESTION DES MOTS DE PASSE
def hacher_mot_de_passe(mot_de_passe: str) -> str:
    """Transforme 'mon_mot_de_passe' en une chaîne illisible unique"""
    return pwd_context.hash(mot_de_passe)

def verifier_mot_de_passe(mot_de_passe_clair: str, mot_de_passe_hache: str) -> bool:
    """Vérifie si le mot de passe tapé correspond au hachage de la BDD"""
    return pwd_context.verify(mot_de_passe_clair, mot_de_passe_hache)

# 2. GESTION DES EMAILS
def hacher_email(email: str) -> str:
    """
    Transforme l'email en hachage SHA-256 en y ajoutant une clé secrète (Pepper).
    Ainsi, même si un hacker connaît la méthode, il ne peut pas deviner l'email sans le Pepper du serveur.
    """
    # On récupère le "pepper" caché dans les variables d'environnement (comme on a fait pour l'export)
    pepper = os.getenv("EMAIL_PEPPER", "cle_secrete_par_defaut_a_changer")
    
    # On nettoie l'email (minuscules, pas d'espaces) pour éviter les bugs de connexion
    email_propre = email.strip().lower()
    
    # On mélange l'email avec le pepper, et on hache le tout
    texte_a_hacher = email_propre + pepper
    return hashlib.sha256(texte_a_hacher.encode()).hexdigest()