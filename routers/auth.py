import sqlite3
import uuid
from fastapi import APIRouter, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from securite import hacher_email, hacher_mot_de_passe
from emails import envoyer_email_bienvenue, envoyer_email_compte_existant



router = APIRouter(tags=["Authentification"])
DB_NAME = "database/bingo_faune.db"

def layout_auth(titre: str, contenu: str) -> str:
    """Un layout épuré spécialement pour les pages de connexion/inscription"""
    return f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{titre} - FaunaBingo</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-stone-100 text-stone-800 font-sans min-h-screen flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-8">
        <div class="sm:mx-auto sm:w-full sm:max-w-md text-center">
            <h1 class="text-4xl font-black text-lime-700 tracking-tight mb-2">🌿 FaunaBingo</h1>
            <h2 class="text-xl font-bold text-stone-800">{titre}</h2>
        </div>
        <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
            <div class="bg-white py-8 px-6 shadow-md rounded-2xl border border-stone-200">
                {contenu}
            </div>
        </div>
    </body>
    </html>
    """

@router.get("/inscription", response_class=HTMLResponse)
def page_inscription():
    contenu = """
    <form action="/inscription" method="POST" class="space-y-5">
        <div>
            <label for="prenom" class="block text-sm font-bold text-stone-700 mb-1">Prénom (Pseudo)</label>
            <input id="prenom" name="prenom" type="text" required class="w-full px-4 py-3 rounded-xl border border-stone-300 focus:outline-none focus:ring-2 focus:ring-lime-500 bg-stone-50">
        </div>
        
        <div>
            <label for="email" class="block text-sm font-bold text-stone-700 mb-1">Adresse e-mail</label>
            <input id="email" name="email" type="email" required class="w-full px-4 py-3 rounded-xl border border-stone-300 focus:outline-none focus:ring-2 focus:ring-lime-500 bg-stone-50">
        </div>
        
        <div>
            <label for="mot_de_passe" class="block text-sm font-bold text-stone-700 mb-1">Mot de passe</label>
            <input id="mot_de_passe" name="mot_de_passe" type="password" required class="w-full px-4 py-3 rounded-xl border border-stone-300 focus:outline-none focus:ring-2 focus:ring-lime-500 bg-stone-50">
        </div>
        
        <div class="pt-2">
            <button type="submit" class="w-full flex justify-center py-3 px-4 border border-transparent rounded-xl shadow-sm text-sm font-bold text-white bg-lime-700 hover:bg-lime-800 active:scale-95 transition">
                Créer mon compte
            </button>
        </div>
    </form>
    
    <div class="mt-6 text-center border-t border-stone-100 pt-5">
        <p class="text-sm text-stone-600">Déjà un compte ? <a href="/connexion" class="font-bold text-lime-700 hover:underline">Se connecter</a></p>
    </div>
    """
    return layout_auth("Créer un compte", contenu)

@router.post("/inscription")
@router.post("/inscription")
def traiter_inscription(
    background_tasks: BackgroundTasks,
    prenom: str = Form(...), 
    email: str = Form(...), 
    mot_de_passe: str = Form(...)
):
    email_hash = hacher_email(email)
    mdp_hash = hacher_mot_de_passe(mot_de_passe)
    
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        
        # 1. On vérifie si l'email existe déjà
        cursor.execute("SELECT id_participant FROM Participant WHERE email_hash = ?", (email_hash,))
        if cursor.fetchone():
            # ANTI-ÉNUMÉRATION : On envoie l'email d'avertissement au lieu d'afficher une erreur
            background_tasks.add_task(envoyer_email_compte_existant, email)
            
            # On fait croire à l'utilisateur que tout s'est bien passé pour ne donner aucun indice
            return RedirectResponse(url="/connexion", status_code=303)
            
        # 2. Si le compte n'existe pas, on le crée normalement
        id_participant = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO Participant (id_participant, prenom, email_hash, mot_de_passe_hash, score_total)
            VALUES (?, ?, ?, ?, 0)
        """, (id_participant, prenom, email_hash, mdp_hash))
        conn.commit()
        
    # Lancement de l'email de bienvenue en arrière-plan
    background_tasks.add_task(envoyer_email_bienvenue, email, prenom)
        
    return RedirectResponse(url="/connexion", status_code=303)