import hashlib
import os
import bcrypt
from itsdangerous import URLSafeTimedSerializer


# 1. GESTION DES MOTS DE PASSE (Bcrypt natif)
def hacher_mot_de_passe(mot_de_passe: str) -> str:
    """Transforme 'mon_mot_de_passe' en une chaîne illisible unique"""
    # Bcrypt exige que le texte soit converti en "bytes" (utf-8)
    mot_de_passe_bytes = mot_de_passe.encode('utf-8')
    
    # On génère un "sel" (salt) aléatoire et on hache
    sel = bcrypt.gensalt()
    hachage_bytes = bcrypt.hashpw(mot_de_passe_bytes, sel)
    
    # On convertit le résultat en texte normal pour le stocker en BDD
    return hachage_bytes.decode('utf-8')

def verifier_mot_de_passe(mot_de_passe_clair: str, mot_de_passe_hache: str) -> bool:
    """Vérifie si le mot de passe tapé correspond au hachage de la BDD"""
    try:
        mot_de_passe_bytes = mot_de_passe_clair.encode('utf-8')
        hachage_bytes = mot_de_passe_hache.encode('utf-8')
        
        return bcrypt.checkpw(mot_de_passe_bytes, hachage_bytes)
    except ValueError:
        # Si le hachage est mal formaté (ex: base de données corrompue)
        return False

# 2. GESTION DES EMAILS
def hacher_email(email: str) -> str:
    """
    Transforme l'email en hachage SHA-256 en y ajoutant une clé secrète (Pepper).
    """
    pepper = os.getenv("EMAIL_PEPPER", "cle_secrete_par_defaut_a_changer")
    
    email_propre = email.strip().lower()
    texte_a_hacher = email_propre + pepper
    
    return hashlib.sha256(texte_a_hacher.encode()).hexdigest()



# 3. GESTION DES JETONS D'INSCRIPTION (Stateless)
def generer_token_inscription(prenom: str, email: str, mdp_hash: str) -> str:
    """Emballe toutes les infos dans un jeton chiffré et signé."""
    secret = os.getenv("EMAIL_PEPPER", "cle_secrete_par_defaut")
    serializer = URLSafeTimedSerializer(secret)
    
    donnees = {
        "prenom": prenom,
        "email": email,
        "mdp_hash": mdp_hash
    }
    return serializer.dumps(donnees, salt="inscription-faunabingo")

def lire_token_inscription(token: str, max_age_secondes: int = 86400) -> dict:
    """Déchiffre le jeton s'il a moins de 24h. Renvoie None sinon."""
    secret = os.getenv("EMAIL_PEPPER", "cle_secrete_par_defaut")
    serializer = URLSafeTimedSerializer(secret)
    try:
        return serializer.loads(token, salt="inscription-faunabingo", max_age=max_age_secondes)
    except:
        return None
    
    
# 4. GESTION DES JETONS DE RÉINITIALISATION DE MOT DE PASSE
def generer_token_mdp(email: str) -> str:
    """Crée un jeton sécurisé contenant l'email pour réinitialiser le mot de passe."""
    secret = os.getenv("EMAIL_PEPPER", "cle_secrete_par_defaut")
    serializer = URLSafeTimedSerializer(secret)
    return serializer.dumps(email, salt="reset-mdp-faunabingo")

def lire_token_mdp(token: str, max_age_secondes: int = 3600) -> str:
    """Déchiffre le jeton s'il a moins de 1 heure. Renvoie None sinon."""
    secret = os.getenv("EMAIL_PEPPER", "cle_secrete_par_defaut")
    serializer = URLSafeTimedSerializer(secret)
    try:
        return serializer.loads(token, salt="reset-mdp-faunabingo", max_age=max_age_secondes)
    except:
        return None