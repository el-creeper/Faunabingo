import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def envoyer_email_bienvenue(email_destinataire: str, prenom: str, lien_verification: str):
    """Envoie un email HTML de confirmation d'inscription avec un lien de validation."""
    
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

    if not SMTP_PASSWORD:
        print(f"📩 [SIMULATION] Email avec lien envoyé à : {email_destinataire}")
        print(f"🔗 LIEN DE VALIDATION : {lien_verification}")
        return

    sujet = "Action requise : Active ton compte FaunaBingo 🌿"
    
    # Le corps de l'email en HTML AVEC le bouton de validation
    html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333; background-color: #f5f5f4; padding: 20px;">
            <div style="max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; border: 1px solid #e7e5e4; text-align: center;">
                <h2 style="color: #4d7c0f; margin-top: 0;">Bienvenue, {prenom} ! 🌿</h2>
                <p>Ton compte FaunaBingo a été créé. Il ne te reste plus qu'une étape pour activer ton accès.</p>
                
                <!-- LE FAMEUX BOUTON DE VALIDATION -->
                <a href="{lien_verification}" style="display: inline-block; background-color: #4d7c0f; color: white; padding: 12px 25px; text-decoration: none; border-radius: 10px; font-weight: bold; margin: 20px 0;">
                    Confirmer mon e-mail
                </a>
                
                <p style="font-size: 12px; color: #78716c;">Ce lien expirera dans 24 heures.</p>
                <p><i>Bonnes observations,</i><br><b>L'équipe FaunaBingo</b></p>
            </div>
        </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = sujet
    msg["From"] = f"FaunaBingo <{SMTP_USER}>"
    msg["To"] = email_destinataire
    msg.attach(MIMEText(html, "html"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, email_destinataire, msg.as_string())
        server.quit()
        print(f"✅ Email de bienvenue envoyé à {email_destinataire}")
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi de l'email : {e}")
        
def envoyer_email_compte_existant(email_destinataire: str):
    """Envoie un email avertissant qu'une tentative d'inscription a eu lieu sur un compte existant."""
    
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

    if not SMTP_PASSWORD:
        print(f"📩 [SIMULATION] Email de 'compte existant' envoyé à : {email_destinataire}")
        return

    sujet = "FaunaBingo - Tentative d'inscription 🌿"
    
    # Le corps de l'email en HTML
    html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333; background-color: #f5f5f4; padding: 20px;">
            <div style="max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; border: 1px solid #e7e5e4;">
                <h2 style="color: #ca8a04; margin-top: 0;">Bonjour ! 🐾</h2>
                <p>Tu (ou quelqu'un d'autre) as essayé de créer un compte sur FaunaBingo avec cette adresse e-mail.</p>
                <p><b>Il s'avère qu'un compte existe déjà chez nous !</b></p>
                <p>Si tu as oublié ton mot de passe, retourne sur l'application et utilise la fonction "Mot de passe oublié" sur la page de connexion.</p>
                <p><i>À très vite,</i><br><b>L'équipe FaunaBingo</b></p>
            </div>
        </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = sujet
    msg["From"] = f"FaunaBingo <{SMTP_USER}>"
    msg["To"] = email_destinataire
    msg.attach(MIMEText(html, "html"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, email_destinataire, msg.as_string())
        server.quit()
        print(f"✅ Email 'compte existant' envoyé à {email_destinataire}")
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi de l'email : {e}")
        
def envoyer_email_reinitialisation(email_destinataire: str, lien_reset: str):
    """Envoie un email avec le lien de réinitialisation du mot de passe."""
    
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

    if not SMTP_PASSWORD:
        print(f"📩 [SIMULATION] Email de reset envoyé à : {email_destinataire}")
        print(f"🔗 LIEN DE RESET : {lien_reset}")
        return

    sujet = "Réinitialisation de ton mot de passe 🌿"
    
    html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333; background-color: #f5f5f4; padding: 20px;">
            <div style="max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; border: 1px solid #e7e5e4; text-align: center;">
                <h2 style="color: #4d7c0f; margin-top: 0;">Mot de passe oublié ? 🐾</h2>
                <p>Nous avons reçu une demande de réinitialisation de mot de passe pour ton compte.</p>
                <a href="{lien_reset}" style="display: inline-block; background-color: #ca8a04; color: white; padding: 12px 25px; text-decoration: none; border-radius: 10px; font-weight: bold; margin: 20px 0;">
                    Choisir un nouveau mot de passe
                </a>
                <p style="font-size: 12px; color: #78716c;">Ce lien expirera dans 1 heure. Si tu n'as rien demandé, tu peux ignorer cet e-mail.</p>
            </div>
        </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = sujet
    msg["From"] = f"FaunaBingo <{SMTP_USER}>"
    msg["To"] = email_destinataire
    msg.attach(MIMEText(html, "html"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, email_destinataire, msg.as_string())
        server.quit()
        print(f"✅ Email de reset envoyé à {email_destinataire}")
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi de l'email : {e}")
        
        
def envoyer_email_demande_ami(email_destinataire: str, prenom_demandeur: str, lien_amis: str):
    """Envoie un e-mail quand on reçoit une demande d'ami d'un autre joueur."""
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

    if not SMTP_PASSWORD:
        print(f"📩 [SIMULATION] Demande d'ami de {prenom_demandeur} envoyée à : {email_destinataire}")
        return

    sujet = f"🤝 {prenom_demandeur} veut t'ajouter sur FaunaBingo !"
    html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333; background-color: #f5f5f4; padding: 20px;">
            <div style="max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; border: 1px solid #e7e5e4; text-align: center;">
                <h2 style="color: #4d7c0f; margin-top: 0;">Nouvelle demande d'ami ! 🐾</h2>
                <p><strong>{prenom_demandeur}</strong> t'a envoyé une demande d'ami sur FaunaBingo.</p>
                <p>Accepte sa demande pour pouvoir comparer vos scores et voir les animaux que vous avez photographiés.</p>
                <a href="{lien_amis}" style="display: inline-block; background-color: #4d7c0f; color: white; padding: 12px 25px; text-decoration: none; border-radius: 10px; font-weight: bold; margin: 20px 0;">
                    Voir mes demandes
                </a>
            </div>
        </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = sujet
    msg["From"] = f"FaunaBingo <{SMTP_USER}>"
    msg["To"] = email_destinataire
    msg.attach(MIMEText(html, "html"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, email_destinataire, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"❌ Erreur email : {e}")

def envoyer_email_invitation(email_destinataire: str, prenom_demandeur: str, lien_accueil: str):
    """Envoie un e-mail à quelqu'un qui n'a pas encore de compte FaunaBingo."""
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

    if not SMTP_PASSWORD:
        print(f"📩 [SIMULATION] Invitation de {prenom_demandeur} envoyée à : {email_destinataire}")
        return

    sujet = f"🌿 {prenom_demandeur} t'invite à jouer à FaunaBingo !"
    html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333; background-color: #f5f5f4; padding: 20px;">
            <div style="max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; border: 1px solid #e7e5e4; text-align: center;">
                <h2 style="color: #4d7c0f; margin-top: 0;">Rejoins FaunaBingo ! 📸</h2>
                <p><strong>{prenom_demandeur}</strong> aimerait t'ajouter en ami sur FaunaBingo, un jeu de collection d'animaux sauvages.</p>
                <p>Crée ton compte dès maintenant pour commencer ton carnet de bord et voir son score !</p>
                <a href="{lien_accueil}" style="display: inline-block; background-color: #ca8a04; color: white; padding: 12px 25px; text-decoration: none; border-radius: 10px; font-weight: bold; margin: 20px 0;">
                    Découvrir le jeu
                </a>
            </div>
        </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = sujet
    msg["From"] = f"FaunaBingo <{SMTP_USER}>"
    msg["To"] = email_destinataire
    msg.attach(MIMEText(html, "html"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, email_destinataire, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"❌ Erreur email : {e}")