import sqlite3
from fastapi import APIRouter, Form, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from securite import hacher_email
from emails import envoyer_email_demande_ami, envoyer_email_invitation
from routers.jeu import layout_jeu, DB_NAME

# On importe ton design existant
from routers.jeu import layout_jeu, DB_NAME

router = APIRouter(tags=["Amis"])

@router.get("/amis", response_class=HTMLResponse)
def page_amis(request: Request):
    session_id = request.cookies.get("session_faunabingo")
    if not session_id:
        return RedirectResponse(url="/connexion", status_code=303)
        
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 1. Infos du joueur
        cursor.execute("SELECT prenom FROM Participant WHERE id_participant = ?", (session_id,))
        joueur = cursor.fetchone()

        # 2. Récupérer les amis validés (ACCEPTE)
        # La jointure permet de récupérer les infos de l'ami, qu'on soit demandeur ou receveur
        cursor.execute("""
            SELECT p.id_participant, p.prenom, p.score_total 
            FROM Amitie a
            JOIN Participant p ON (p.id_participant = a.id_demandeur OR p.id_participant = a.id_receveur)
            WHERE (a.id_demandeur = ? OR a.id_receveur = ?) 
              AND a.statut = 'ACCEPTE' 
              AND p.id_participant != ?
            ORDER BY p.score_total DESC
        """, (session_id, session_id, session_id))
        amis = cursor.fetchall()

        # 3. Récupérer les demandes REÇUES en attente
        cursor.execute("""
            SELECT a.id_demandeur, p.prenom 
            FROM Amitie a
            JOIN Participant p ON p.id_participant = a.id_demandeur
            WHERE a.id_receveur = ? AND a.statut = 'EN_ATTENTE'
        """, (session_id,))
        demandes_recues = cursor.fetchall()
        
        # 4. Récupérer les demandes ENVOYÉES en attente (pour info)
        cursor.execute("""
            SELECT p.prenom 
            FROM Amitie a
            JOIN Participant p ON p.id_participant = a.id_receveur
            WHERE a.id_demandeur = ? AND a.statut = 'EN_ATTENTE'
        """, (session_id,))
        demandes_envoyees = cursor.fetchall()

    # --- CONSTRUCTION DU HTML ---
    
    # Formulaire d'ajout
    html_ajout = """
    <div class="bg-white p-6 rounded-xl shadow-sm border border-stone-200 mb-6">
        <h3 class="text-lg font-bold text-stone-800 mb-2">Ajouter un ami</h3>
        <p class="text-sm text-stone-500 mb-4">Saisis l'adresse e-mail de ton ami pour lui envoyer une demande.</p>
        <form action="/amis/ajouter" method="POST" class="flex gap-2">
            <input type="email" name="email_ami" required placeholder="email@exemple.com" class="flex-1 px-4 py-2 border border-stone-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-lime-500">
            <button type="submit" class="bg-lime-700 hover:bg-lime-800 text-white px-4 py-2 rounded-lg font-bold transition shadow-sm">Demander</button>
        </form>
    </div>
    """

    # Demandes reçues
    html_demandes = ""
    if demandes_recues:
        html_demandes = '<h3 class="text-lg font-bold text-stone-800 mb-3">Demandes reçues</h3><div class="space-y-2 mb-6">'
        for d in demandes_recues:
            html_demandes += f"""
            <div class="flex justify-between items-center bg-amber-50 p-3 rounded-lg border border-amber-200">
                <span class="font-bold text-stone-800">{d['prenom']}</span>
                <div class="flex gap-2">
                    <form action="/amis/repondre" method="POST">
                        <input type="hidden" name="id_demandeur" value="{d['id_demandeur']}">
                        <button type="submit" name="action" value="accepter" class="bg-emerald-600 hover:bg-emerald-700 text-white text-xs px-3 py-1.5 rounded font-bold shadow-sm">✅ Accepter</button>
                        <button type="submit" name="action" value="refuser" class="bg-stone-200 hover:bg-red-500 hover:text-white text-stone-700 text-xs px-3 py-1.5 rounded font-bold transition">❌ Refuser</button>
                    </form>
                </div>
            </div>
            """
        html_demandes += '</div>'

    # Liste des amis (façon classement avec cases à cocher)
    html_liste_amis = '<div class="flex justify-between items-center mb-3"><h3 class="text-lg font-bold text-stone-800">Mes Amis</h3>'
    if amis:
        # Le bouton pour valider la sélection
        html_liste_amis += '<button type="submit" form="form-comparer" class="bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-1.5 rounded-lg text-sm font-bold shadow-sm transition cursor-pointer">⚔️ Comparer</button></div>'
        
        # Le formulaire qui va envoyer les IDs cochés
        html_liste_amis += '<form id="form-comparer" action="/comparer" method="GET" class="space-y-3">'
        for a in amis:
            html_liste_amis += f"""
            <label class="flex justify-between items-center bg-white p-3 rounded-xl shadow-sm border border-stone-200 cursor-pointer hover:border-indigo-300 transition">
                <div class="flex items-center gap-3">
                    <!-- LA FAMEUSE CASE À COCHER -->
                    <input type="checkbox" name="amis_ids" value="{a['id_participant']}" class="w-5 h-5 accent-indigo-600 cursor-pointer">
                    
                    <div class="w-10 h-10 bg-lime-100 rounded-full flex items-center justify-center text-lime-700 font-black text-lg">
                        {a['prenom'][0].upper()}
                    </div>
                    <div>
                        <div class="font-bold text-stone-800">{a['prenom']}</div>
                        <a href="/carnet/{a['id_participant']}" class="text-[10px] text-indigo-600 font-bold hover:underline">Voir son carnet 👀</a>
                    </div>
                </div>
                <div class="text-right">
                    <div class="font-black text-lime-700 text-lg">{a['score_total']} pts</div>
                    <!-- On utilise un bouton JS pour ne pas casser le formulaire de comparaison -->
                    <button type="button" onclick="document.getElementById('form-supprimer-{a['id_participant']}').submit()" class="text-[10px] text-stone-400 hover:text-red-500 transition">Retirer</button>
                </div>
            </label>
            """
        html_liste_amis += '</form>'

        # Formulaires cachés pour supprimer un ami (obligatoire pour que le HTML soit valide)
        for a in amis:
            html_liste_amis += f"""
            <form id="form-supprimer-{a['id_participant']}" action="/amis/supprimer" method="POST" class="hidden">
                <input type="hidden" name="id_ami" value="{a['id_participant']}">
            </form>
            """
    else:
        html_liste_amis += '</div><p class="text-sm text-stone-500 italic bg-white p-4 rounded-xl border border-stone-200 text-center">Tu n\'as pas encore d\'amis ajoutés.</p>'
        
        
        
    # Demandes envoyées (en attente)
    html_envoyees = ""
    if demandes_envoyees:
        html_envoyees = '<div class="mt-6 pt-4 border-t border-stone-200"><h4 class="text-xs font-bold text-stone-500 uppercase mb-2">Demandes envoyées en attente</h4>'
        for d in demandes_envoyees:
            html_envoyees += f'<div class="text-sm text-stone-600 mb-1">⏳ En attente de : <b>{d["prenom"]}</b></div>'
        html_envoyees += '</div>'


    contenu = f"""
    <div class="mb-6">
        <h2 class="text-3xl font-black text-stone-800">Système d'Amis 🤝</h2>
    </div>
    {html_ajout}
    {html_demandes}
    {html_liste_amis}
    {html_envoyees}
    """
    
    header_links = f"""
    <div class="flex space-x-2 items-center">
        <a href="/carnet/{session_id}" class="text-[10px] sm:text-xs bg-lime-800 hover:bg-lime-900 px-2 sm:px-3 py-1.5 rounded-lg transition font-medium shadow-sm">📖 Mon Carnet</a>
        <a href="/classement" class="text-[10px] sm:text-xs bg-lime-800 hover:bg-lime-900 px-2 sm:px-3 py-1.5 rounded-lg transition font-medium shadow-sm">🏆 Classement</a>
        <a href="/deconnexion" class="text-[10px] sm:text-xs bg-stone-700 hover:bg-red-700 px-2 sm:px-3 py-1.5 rounded-lg transition font-medium shadow-sm">👋 Quitter</a>
    </div>
    """
    return HTMLResponse(content=layout_jeu(f"Amis - {joueur['prenom']}", contenu, header_links))

# --- ACTIONS BACKEND ---

@router.post("/amis/ajouter")
def ajouter_ami(request: Request, background_tasks: BackgroundTasks, email_ami: str = Form(...)):
    session_id = request.cookies.get("session_faunabingo")
    if not session_id: return RedirectResponse(url="/connexion", status_code=303)
    
    email_clair = email_ami.strip()
    email_hash_cible = hacher_email(email_clair)
    
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        
        # 1. Récupérer le prénom de celui qui demande (pour l'e-mail)
        cursor.execute("SELECT prenom FROM Participant WHERE id_participant = ?", (session_id,))
        demandeur = cursor.fetchone()
        prenom_demandeur = demandeur[0] if demandeur else "Un ami"
        
        # 2. Chercher si la cible existe dans la base
        cursor.execute("SELECT id_participant FROM Participant WHERE email_hash = ?", (email_hash_cible,))
        cible = cursor.fetchone()
        
        # SI LA CIBLE EXISTE : On ajoute la demande en BDD et on notifie
        if cible and cible[0] != session_id:
            id_cible = cible[0]
            
            # Vérifier qu'ils ne sont pas déjà amis (ou en attente)
            cursor.execute("""
                SELECT statut FROM Amitie 
                WHERE (id_demandeur = ? AND id_receveur = ?) 
                   OR (id_demandeur = ? AND id_receveur = ?)
            """, (session_id, id_cible, id_cible, session_id))
            
            if not cursor.fetchone():
                # Création de la demande
                cursor.execute("INSERT INTO Amitie (id_demandeur, id_receveur, statut) VALUES (?, ?, 'EN_ATTENTE')", (session_id, id_cible))
                conn.commit()
                
                # E-mail de notification
                lien_amis = f"{request.base_url}amis"
                background_tasks.add_task(envoyer_email_demande_ami, email_clair, prenom_demandeur, lien_amis)
                
        # SI LA CIBLE N'EXISTE PAS : On envoie une invitation à s'inscrire !
        elif not cible:
            lien_accueil = f"{request.base_url}"
            background_tasks.add_task(envoyer_email_invitation, email_clair, prenom_demandeur, lien_accueil)
                
    return RedirectResponse(url="/amis", status_code=303)



@router.post("/amis/repondre")
def repondre_demande(request: Request, id_demandeur: str = Form(...), action: str = Form(...)):
    session_id = request.cookies.get("session_faunabingo")
    if not session_id: return RedirectResponse(url="/connexion", status_code=303)
    
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        if action == "accepter":
            cursor.execute("UPDATE Amitie SET statut = 'ACCEPTE' WHERE id_demandeur = ? AND id_receveur = ?", (id_demandeur, session_id))
        elif action == "refuser":
            cursor.execute("DELETE FROM Amitie WHERE id_demandeur = ? AND id_receveur = ?", (id_demandeur, session_id))
        conn.commit()
        
    return RedirectResponse(url="/amis", status_code=303)

@router.post("/amis/supprimer")
def supprimer_ami(request: Request, id_ami: str = Form(...)):
    session_id = request.cookies.get("session_faunabingo")
    if not session_id: return RedirectResponse(url="/connexion", status_code=303)
    
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        # L'amitié peut être dans les deux sens, on supprime l'une ou l'autre
        cursor.execute("""
            DELETE FROM Amitie 
            WHERE (id_demandeur = ? AND id_receveur = ?) 
               OR (id_demandeur = ? AND id_receveur = ?)
        """, (session_id, id_ami, id_ami, session_id))
        conn.commit()
        
    return RedirectResponse(url="/amis", status_code=303)


