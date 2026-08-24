import sqlite3
import uuid
from fastapi import APIRouter, Form, BackgroundTasks, Response, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from securite import (hacher_email, hacher_mot_de_passe, verifier_mot_de_passe, 
                      generer_token_inscription, lire_token_inscription, 
                      generer_token_mdp, lire_token_mdp)
from emails import envoyer_email_bienvenue, envoyer_email_compte_existant, envoyer_email_reinitialisation
from jeu import layout_jeu


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
def traiter_inscription(
    request: Request,
    background_tasks: BackgroundTasks,
    prenom: str = Form(...), 
    email: str = Form(...), 
    mot_de_passe: str = Form(...)
):
    email_hash = hacher_email(email)
    mdp_hash = hacher_mot_de_passe(mot_de_passe)
    
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        
        # 1. On vérifie juste si le compte existe déjà
        cursor.execute("SELECT id_participant FROM Participant WHERE email_hash = ?", (email_hash,))
        if cursor.fetchone():
            background_tasks.add_task(envoyer_email_compte_existant, email)
            return RedirectResponse(url="/inscription/succes", status_code=303)
            
    # 2. AUCUNE MODIFICATION DE LA BASE DE DONNÉES ICI !
    # On génère un jeton qui contient toutes les informations en transit
    token = generer_token_inscription(prenom, email, mdp_hash)
    lien_verification = f"{request.base_url}verification-email?token={token}"
    
    background_tasks.add_task(envoyer_email_bienvenue, email, prenom, lien_verification)
        
    return RedirectResponse(url="/inscription/succes", status_code=303)


@router.get("/verification-email", response_class=HTMLResponse)
def verifier_email(token: str):
    # 1. On déchiffre le jeton pour récupérer les données en transit
    donnees = lire_token_inscription(token)
    
    if not donnees:
        erreur = """
        <div class="text-center">
            <div class="text-red-500 text-4xl mb-2">❌</div>
            <h3 class="text-lg font-bold">Lien expiré ou invalide</h3>
            <p class="text-sm text-stone-600 mb-6">Demande un nouveau lien de vérification.</p>
        </div>
        """
        return HTMLResponse(layout_auth("Erreur", erreur), status_code=400)
        
    # 2. On extrait les données du jeton valide
    prenom = donnees["prenom"]
    email_clair = donnees["email"]
    mdp_hash = donnees["mdp_hash"]
    
    email_hash = hacher_email(email_clair)
    
    # 3. On fait enfin l'insertion officielle dans la base de données
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        
        # On s'assure que l'utilisateur n'a pas cliqué deux fois sur le lien
        cursor.execute("SELECT id_participant FROM Participant WHERE email_hash = ?", (email_hash,))
        if not cursor.fetchone():
            id_participant = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO Participant (id_participant, prenom, email_hash, mot_de_passe_hash, score_total)
                VALUES (?, ?, ?, ?, 0)
            """, (id_participant, prenom, email_hash, mdp_hash))
            conn.commit()
        
    succes = """
    <div class="text-center">
        <div class="text-emerald-500 text-6xl mb-4">✅</div>
        <h3 class="text-2xl font-black text-stone-800 mb-3">E-mail validé !</h3>
        <p class="text-sm text-stone-600 mb-6">Ton compte a été créé avec succès.</p>
        <a href="/connexion" class="w-full flex justify-center py-3 px-4 rounded-xl shadow-sm font-bold text-white bg-lime-700 hover:bg-lime-800 transition">Se connecter</a>
    </div>
    """
    return layout_auth("Compte activé", succes)



@router.get("/inscription/succes", response_class=HTMLResponse)
def page_succes_inscription():
    contenu = """
    <div class="text-center py-4">
        <div class="text-6xl mb-4">✨</div>
        <h3 class="text-2xl font-black text-stone-800 mb-3">Inscription en cours !</h3>
        <p class="text-sm text-stone-600 mb-8 leading-relaxed">
            Un e-mail de confirmation vient de t'être envoyé.<br>
            Clique sur le lien à l'intérieur pour activer ton compte !
        </p>
        <a href="/connexion" class="w-full flex justify-center py-3 px-4 border border-transparent rounded-xl shadow-sm text-sm font-bold text-white bg-lime-700 hover:bg-lime-800 active:scale-95 transition">
            Aller à la connexion
        </a>
    </div>
    """
    return layout_auth("Vérifie tes e-mails", contenu)


# --- PAGE DE CONNEXION ---

@router.get("/connexion", response_class=HTMLResponse)
def page_connexion():
    contenu = """
    <form action="/connexion" method="POST" class="space-y-5">
        <div>
            <label for="email" class="block text-sm font-bold text-stone-700 mb-1">Adresse e-mail</label>
            <input id="email" name="email" type="email" required class="w-full px-4 py-3 rounded-xl border border-stone-300 focus:outline-none focus:ring-2 focus:ring-lime-500 bg-stone-50">
        </div>
        
        <div>
            <div class="flex justify-between items-center mb-1">
                <label for="mot_de_passe" class="block text-sm font-bold text-stone-700">Mot de passe</label>
                <a href="/mot-de-passe-oublie" class="text-[11px] font-bold text-lime-700 hover:underline">Oublié ?</a>
            </div>
            <input id="mot_de_passe" name="mot_de_passe" type="password" required class="w-full px-4 py-3 rounded-xl border border-stone-300 focus:outline-none focus:ring-2 focus:ring-lime-500 bg-stone-50">
        </div>
        
        <div class="pt-2">
            <button type="submit" class="w-full flex justify-center py-3 px-4 border border-transparent rounded-xl shadow-sm text-sm font-bold text-white bg-lime-700 hover:bg-lime-800 active:scale-95 transition">
                Se connecter
            </button>
        </div>
    </form>
    
    <div class="mt-6 text-center border-t border-stone-100 pt-5">
        <p class="text-sm text-stone-600">Pas encore de compte ? <a href="/inscription" class="font-bold text-lime-700 hover:underline">S'inscrire</a></p>
    </div>
    """
    return layout_auth("Connexion", contenu)

@router.post("/connexion")
def traiter_connexion(email: str = Form(...), mot_de_passe: str = Form(...)):
    # 1. On recrée le hachage de l'email pour chercher l'utilisateur
    email_hash = hacher_email(email)
    
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT id_participant, mot_de_passe_hash FROM Participant WHERE email_hash = ?", (email_hash,))
        utilisateur = cursor.fetchone()
        
        # 2. Vérification de sécurité (Anti-énumération et Mot de passe)
        # On utilise "not utilisateur" pour voir si le compte n'existe pas, 
        # OU la fonction bcrypt pour voir si le mot de passe est faux.
        if not utilisateur or not verifier_mot_de_passe(mot_de_passe, utilisateur['mot_de_passe_hash']):
            erreur_html = """
            <div class="text-center">
                <div class="text-red-500 text-4xl mb-2">❌</div>
                <h3 class="text-lg font-bold text-stone-800 mb-2">Identifiants incorrects</h3>
                <p class="text-sm text-stone-600 mb-6">L'adresse e-mail ou le mot de passe est invalide.</p>
                <a href="/connexion" class="w-full block py-3 px-4 bg-stone-200 hover:bg-stone-300 text-stone-800 font-bold rounded-xl transition">Réessayer</a>
            </div>
            """
            # On renvoie la même erreur générique pour les deux cas
            return HTMLResponse(layout_auth("Erreur", erreur_html), status_code=400)
            
        # 3. Succès de la connexion !
        id_participant = utilisateur['id_participant']
        
        # On prépare la redirection vers le carnet de l'utilisateur
        response = RedirectResponse(url=f"/carnet/{id_participant}", status_code=303)
        
        # 4. Le Cookie de Session ultra-sécurisé
        response.set_cookie(
            key="session_faunabingo", 
            value=id_participant, 
            httponly=True,       # Empêche le piratage par des scripts (XSS)
            max_age=31536000     # Garde l'utilisateur connecté pendant 1 an (en secondes)
        )
        
        return response
    
    # --- DÉCONNEXION ---
@router.get("/deconnexion")
def se_deconnecter():
    # On redirige vers l'accueil
    response = RedirectResponse(url="/", status_code=303)
    # On détruit le cookie de session !
    response.delete_cookie(key="session_faunabingo")
    return response 

# --- MOT DE PASSE OUBLIÉ ---

@router.get("/mot-de-passe-oublie", response_class=HTMLResponse)
def page_demande_reset():
    contenu = """
    <div class="text-center mb-6">
        <div class="text-4xl mb-2">🔑</div>
        <h3 class="text-xl font-bold text-stone-800">Mot de passe oublié</h3>
        <p class="text-sm text-stone-600 mt-2">Saisis ton adresse e-mail pour recevoir un lien de réinitialisation.</p>
    </div>
    <form action="/mot-de-passe-oublie" method="POST" class="space-y-4">
        <div>
            <input id="email" name="email" type="email" placeholder="Ton adresse e-mail" required class="w-full px-4 py-3 rounded-xl border border-stone-300 focus:outline-none focus:ring-2 focus:ring-lime-500 bg-stone-50 text-center">
        </div>
        <button type="submit" class="w-full flex justify-center py-3 px-4 rounded-xl shadow-sm font-bold text-white bg-lime-700 hover:bg-lime-800 transition">
            Envoyer le lien
        </button>
    </form>
    <div class="mt-4 text-center">
        <a href="/connexion" class="text-sm font-bold text-stone-500 hover:text-stone-700">Retour à la connexion</a>
    </div>
    """
    return layout_auth("Mot de passe oublié", contenu)

@router.post("/mot-de-passe-oublie")
def traiter_demande_reset(request: Request, background_tasks: BackgroundTasks, email: str = Form(...)):
    email_hash = hacher_email(email)
    
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id_participant FROM Participant WHERE email_hash = ?", (email_hash,))
        
        # Si le compte existe, on génère le jeton et on envoie l'e-mail
        if cursor.fetchone():
            token = generer_token_mdp(email)
            lien_reset = f"{request.base_url}reinitialiser-mot-de-passe?token={token}"
            background_tasks.add_task(envoyer_email_reinitialisation, email, lien_reset)
            
    succes = """
    <div class="text-center py-4">
        <div class="text-5xl mb-4">✉️</div>
        <h3 class="text-xl font-bold text-stone-800 mb-3">Vérifie tes e-mails</h3>
        <p class="text-sm text-stone-600 mb-6 leading-relaxed">
            Si un compte est associé à cette adresse, un lien de réinitialisation vient d'être envoyé.
        </p>
        <a href="/connexion" class="w-full block py-3 px-4 bg-stone-200 hover:bg-stone-300 text-stone-800 font-bold rounded-xl transition">Retour</a>
    </div>
    """
    return HTMLResponse(content=layout_auth("Email envoyé", succes))


@router.get("/reinitialiser-mdp", response_class=HTMLResponse)
def page_reinitialiser_mdp(request: Request, token: str = Query(...)):
    # 1. On déchiffre le jeton pour voir s'il est valide et récupérer l'email
    email = lire_token_mdp(token)
    
    if not email:
        # Si le jeton est expiré ou trafiqué
        return layout_jeu("Erreur", "<div class='text-center p-10 bg-red-100 rounded-xl'>Le lien est invalide ou a expiré.</div>")

    # 2. Si le jeton est bon, on affiche le formulaire
    contenu = f"""
    <div class="max-w-md mx-auto mt-10 bg-white p-6 rounded-xl shadow-sm border border-stone-200">
        <h2 class="text-2xl font-black mb-4">Nouveau mot de passe</h2>
        <form action="/reinitialiser-mdp" method="POST" class="space-y-4">
            <!-- On renvoie le jeton caché pour que le POST sache de qui on parle -->
            <input type="hidden" name="token" value="{token}">
            
            <div>
                <label class="block text-sm font-bold text-stone-700">Nouveau mot de passe</label>
                <input type="password" name="nouveau_mdp" required minlength="8" class="w-full px-4 py-2 border rounded-lg">
            </div>
            <button type="submit" class="w-full bg-lime-700 text-white font-bold py-3 rounded-lg shadow-sm">
                Enregistrer le mot de passe
            </button>
        </form>
    </div>
    """
    
    return layout_jeu("Nouveau mot de passe", contenu)


@router.post("/reinitialiser-mdp", response_class=HTMLResponse)
def traiter_nouveau_mdp(request: Request, token: str = Form(...), nouveau_mdp: str = Form(...)):
    # 1. On revérifie le jeton (sécurité)
    email = lire_token_mdp(token)
    if not email:
        return layout_jeu("Erreur", "<div class='text-center p-10 bg-red-100 rounded-xl'>Le lien a expiré.</div>")
        
    # 2. On hache l'email pour le chercher dans la BDD, et on hache le nouveau MDP
    email_hache = hacher_email(email) # Assure-toi d'importer cette fonction
    mdp_hache = hacher_mot_de_passe(nouveau_mdp)

    # 3. On met à jour la base de données
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE Participant SET mot_de_passe_hash = ? WHERE email_hash = ?", (mdp_hache, email_hache))
        conn.commit()

    # 4. On redirige vers la page de connexion avec un message de succès
    contenu = """
    <div class="max-w-md mx-auto mt-10 text-center bg-lime-50 p-6 rounded-xl border border-lime-200">
        <h2 class="text-2xl font-black text-lime-800 mb-4">Succès ! 🎉</h2>
        <p class="text-lime-700 mb-6">Ton mot de passe a bien été modifié.</p>
        <a href="/connexion" class="bg-lime-700 text-white font-bold py-2 px-6 rounded-lg inline-block">Se connecter</a>
    </div>
    """
    return layout_jeu("Mot de passe modifié", contenu)