import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def envoyer_email_bienvenue(email_destinataire: str, prenom: str):
    """Envoie un email HTML de confirmation d'inscription en tâche de fond."""
    
    # Configuration SMTP (Par défaut, paramétré pour Gmail)
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

    # Sécurité de développement : si pas de mot de passe configuré, on simule l'envoi
    if not SMTP_PASSWORD:
        print(f"📩 [SIMULATION] Email de confirmation envoyé à : {email_destinataire}")
        return

    sujet = "Bienvenue sur FaunaBingo ! 🌿"
    
    # Le corps de l'email en HTML
    html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333; background-color: #f5f5f4; padding: 20px;">
            <div style="max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; border: 1px solid #e7e5e4;">
                <h2 style="color: #4d7c0f; margin-top: 0;">Bienvenue dans l'aventure, {prenom} ! 🐒</h2>
                <p>Ton compte FaunaBingo a été créé avec succès.</p>
                <p>Nous sommes ravis de t'avoir parmi nous. Prépare-toi à explorer et à capturer les plus belles espèces (en photo, bien sûr !).</p>
                <p><i>Pura Vida,</i><br><b>L'équipe FaunaBingo</b></p>
            </div>
        </body>
    </html>
    """

    # Préparation du message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = sujet
    msg["From"] = f"FaunaBingo <{SMTP_USER}>"
    msg["To"] = email_destinataire
    msg.attach(MIMEText(html, "html"))

    # Envoi via le serveur
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls() # Sécurise la connexion
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
    
    html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333; background-color: #f5f5f4; padding: 20px;">
            <div style="max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; border: 1px solid #e7e5e4;">
                <h2 style="color: #ca8a04; margin-top: 0;">Coucou ! 🐒</h2>
                <p>Tu (ou quelqu'un d'autre) as essayé de créer un compte sur FaunaBingo avec cette adresse e-mail.</p>
                <p><b>Il s'avère qu'un compte existe déjà chez nous !</b></p>
                <p>Si tu as oublié ton mot de passe, retourne sur l'application et utilise la fonction "Mot de passe oublié" sur la page de connexion.</p>
                <p><i>Pura Vida,</i><br><b>L'équipe FaunaBingo</b></p>
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