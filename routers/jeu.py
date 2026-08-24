import sqlite3
import uuid
from fastapi import APIRouter, Form, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse

router = APIRouter(tags=["Jeu"])
DB_NAME = "database/bingo_faune.db"

def layout_jeu(titre: str, contenu: str, header_links: str = ""):
    # Le menu est maintenant FIXE et identique sur toutes les pages
    menu_fixe = """
    <div class="flex space-x-1 sm:space-x-2 items-center">
        <a href="/mon-carnet" class="text-[10px] sm:text-xs bg-lime-800 hover:bg-lime-900 px-2 sm:px-3 py-2 rounded-lg transition font-medium shadow-sm flex items-center" title="Mon Carnet">📖<span class="hidden sm:inline ml-1">Carnet</span></a>
        <a href="/amis" class="text-[10px] sm:text-xs bg-lime-800 hover:bg-lime-900 px-2 sm:px-3 py-2 rounded-lg transition font-medium shadow-sm flex items-center" title="Amis">🤝<span class="hidden sm:inline ml-1">Amis</span></a>
        <a href="/classement" class="text-[10px] sm:text-xs bg-lime-800 hover:bg-lime-900 px-2 sm:px-3 py-2 rounded-lg transition font-medium shadow-sm flex items-center" title="Classement">🏆<span class="hidden sm:inline ml-1">Class.</span></a>
        <a href="/deconnexion" class="text-[10px] sm:text-xs bg-stone-700 hover:bg-red-700 px-2 sm:px-3 py-2 rounded-lg transition font-medium shadow-sm flex items-center" title="Quitter">👋<span class="hidden sm:inline ml-1">Quitter</span></a>
    </div>
    """
    
    return f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{titre}</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-50 text-slate-800 font-sans min-h-screen pb-20">
        <nav class="bg-lime-700 text-white shadow-md mb-6 sticky top-0 z-50">
            <div class="max-w-5xl mx-auto px-4 py-3 flex justify-between items-center">
                <a href="/mon-carnet" class="text-lg sm:text-xl font-bold tracking-tight hover:text-lime-200 transition">🌿 FaunaBingo</a>
                {menu_fixe}
            </div>
        </nav>
        <main class="max-w-5xl mx-auto px-4 md:px-8">
            {contenu}
        </main>
    </body>
    </html>
    """

# --- PAGE 1 : ACCUEIL PUBLIC ---
@router.get("/", response_class=HTMLResponse)
def page_accueil(request: Request):
    # 1. Redirection automatique si l'utilisateur est déjà connecté
    session_id = request.cookies.get("session_faunabingo")
    if session_id:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id_participant FROM Participant WHERE id_participant = ?", (session_id,))
            if cursor.fetchone():
                return RedirectResponse(url=f"/carnet/{session_id}", status_code=303)

    # 2. Page d'accueil pour les visiteurs déconnectés
    contenu = """
    <div class="text-center mb-10 mt-8">
        <div class="text-6xl mb-4">🌿</div>
        <h2 class="text-4xl font-black text-stone-800 mb-4 tracking-tight">FaunaBingo</h2>
        <p class="text-stone-500 text-base leading-relaxed px-4">
            Découvre la nature, identifie les espèces et participe à la plus grande aventure d'observation !
        </p>
    </div>
    
    <div class="space-y-4 mt-8">
        <a href="/inscription" class="block w-full bg-lime-700 hover:bg-lime-800 text-white p-4 rounded-xl shadow-sm font-bold text-center transition active:scale-95 text-lg">
            Créer un compte
        </a>
        <a href="/connexion" class="block w-full bg-white hover:bg-stone-50 text-stone-700 border border-stone-200 p-4 rounded-xl shadow-sm font-bold text-center transition active:scale-95 text-lg">
            Se connecter
        </a>
    </div>
    
    <div class="mt-8">
        <a href="/classement" class="block w-full bg-amber-500 hover:bg-amber-600 text-white p-4 rounded-xl shadow-sm font-bold text-center transition active:scale-95 text-lg">
            🏆 Voir le Classement Global
        </a>
    </div>
    """
    
    return layout_jeu("Accueil - FaunaBingo", contenu)

# --- PAGE 2 : LE CARNET DE BORD ---

@router.get("/carnet/{id_participant}", response_class=HTMLResponse)
def carnet_bord(request: Request, id_participant: str):
    session_id = request.cookies.get("session_faunabingo")
    if session_id != id_participant:
        return RedirectResponse(url="/connexion", status_code=303)
        
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM Participant WHERE id_participant = ?", (id_participant,))
        joueur = cursor.fetchone()
        
        cursor.execute("SELECT * FROM Espece ORDER BY classe, nom_courant")
        toutes_especes = cursor.fetchall()
        
        # On récupère les ID ET le type de preuve des espèces trouvées (sous forme de dictionnaire)
        cursor.execute("SELECT id_espece, type_preuve FROM Observation WHERE id_participant = ?", (id_participant,))
        especes_trouvees = {row['id_espece']: row['type_preuve'] for row in cursor.fetchall()}
        
    categories = {}
    for esp in toutes_especes:
        nom_cat = esp['classe'] if esp['classe'] else "Non classé"
        if nom_cat not in categories:
            categories[nom_cat] = {'total': 0, 'trouvees': 0, 'html_especes': ""}
            
        categories[nom_cat]['total'] += 1
        est_trouvee = esp['id_espece'] in especes_trouvees
        
        # --- C'EST CETTE PARTIE QUI TE MANQUAIT ---
        type_preuve_actuel = ""
        if est_trouvee:
            categories[nom_cat]['trouvees'] += 1
            type_preuve_actuel = especes_trouvees[esp['id_espece']]
        # ------------------------------------------
            
        # On définit le badge selon le statut
        badge = f"✅ {type_preuve_actuel}" if est_trouvee else "" 
        img_src = f"/{esp['image_reference']}" if esp['image_reference'] else "/static/placeholder.png"
        
        # --- LA LOGIQUE DES BOUTONS DYNAMIQUES ET COULEURS PLEINES ---
        html_actions = '<div class="mt-3 flex gap-1 sm:gap-2">'
        
        # S'il n'a pas encore fait de photo, on affiche le formulaire pour s'améliorer
        if type_preuve_actuel != "PHOTO":
            html_actions += f'''<form action="/carnet/{id_participant}/observer" method="POST" class="flex flex-1 gap-1 sm:gap-2">
                <input type="hidden" name="id_espece" value="{esp['id_espece']}">'''
                
            # CORRECTION ICI : Le bouton ENTENDU n'apparaît que s'il rapporte plus de 0 point !
            if not type_preuve_actuel and esp["points_entendu"] > 0:
                html_actions += f'<button type="submit" name="type_preuve" value="ENTENDU" class="flex-1 text-[10px] font-bold bg-indigo-600 text-white py-1.5 rounded shadow-sm hover:bg-indigo-700 transition">🔊 {esp["points_entendu"]}</button>'
                
            # Bouton VU (visible au début ou si on a juste entendu)
            if type_preuve_actuel in ["", "ENTENDU"]:
                html_actions += f'<button type="submit" name="type_preuve" value="VU" class="flex-1 text-[10px] font-bold bg-amber-500 text-white py-1.5 rounded shadow-sm hover:bg-amber-600 transition">👀 {esp["points_vu"]}</button>'
                
            # Bouton PHOTO (Toujours visible tant qu'on n'a pas coché photo)
            html_actions += f'<button type="submit" name="type_preuve" value="PHOTO" class="flex-1 text-[10px] font-bold bg-emerald-600 text-white py-1.5 rounded shadow-sm hover:bg-emerald-700 transition">📸 {esp["points_photo"]}</button>'
            html_actions += '</form>'
            
        # Bouton ANNULER (visible dès qu'une preuve existe)
        if type_preuve_actuel:
            # Si on a la photo, le bouton annuler prend toute la largeur. Sinon, c'est juste une petite croix à côté.
            btn_texte = "❌ Annuler" if type_preuve_actuel == "PHOTO" else "❌"
            flex_class = "flex-1" if type_preuve_actuel == "PHOTO" else "shrink-0"
            html_actions += f'''<form action="/carnet/{id_participant}/annuler" method="POST" class="flex {flex_class}">
                <input type="hidden" name="id_espece" value="{esp['id_espece']}">
                <button type="submit" class="w-full px-3 text-[10px] font-bold bg-red-600 text-white py-1.5 rounded shadow-sm hover:bg-red-700 transition">{btn_texte}</button>
            </form>'''
            
        html_actions += '</div>'
        # -------------------------------------------------------------
            
        carte = f"""
        <div id="espece-{esp['id_espece']}" class="carte-espece scroll-mt-40 bg-white rounded-xl shadow-sm border border-stone-200 overflow-hidden transition-all duration-300">
            <div class="carte-img-container shrink-0 bg-stone-100 relative">
                <img src="{img_src}" class="carte-img w-full h-full object-cover">
            </div>
            <div class="p-3 flex-1 flex flex-col justify-between">
                <div>
                    <div class="flex justify-between items-start mb-1">
                        <h4 class="font-bold text-stone-800 text-sm leading-tight">{esp['nom_courant']}</h4>
                        <span class="text-[10px] font-black text-emerald-700 bg-emerald-50 px-1 rounded">{badge}</span>
                    </div>
                    <p class="text-[10px] text-stone-500 italic">{esp['nom_scientifique'] or ''}</p>
                </div>
                
                {html_actions}
                
            </div>
        </div>
        """
        categories[nom_cat]['html_especes'] += carte
        

    # BOUTONS FILTRES (Ajout de 'this' dans le onclick pour détecter la désélection)
    html_boutons_filtres = """
    <div class="flex space-x-2 overflow-x-auto pb-3 pt-2 px-1 scroll-adaptatif" id="conteneur-filtres">
        <button onclick="filtrerCategorie('Toutes', this)" class="btn-filtre active shrink-0 px-4 py-2 rounded-full bg-lime-700 text-white font-bold text-sm shadow-sm transition">
            Toutes
        </button>
    """
    for nom_cat, stats in categories.items():
        html_boutons_filtres += f"""
        <button onclick="filtrerCategorie('{nom_cat}', this)" class="btn-filtre shrink-0 px-4 py-2 rounded-full bg-white border border-stone-200 text-stone-600 font-medium text-sm hover:bg-stone-50 hover:border-lime-300 transition">
            {nom_cat} <span class="ml-1 text-[10px] bg-stone-100 px-1.5 py-0.5 rounded-md text-stone-500 font-bold">{stats['trouvees']}/{stats['total']}</span>
        </button>
        """
    html_boutons_filtres += "</div>"
    
    html_sections_categories = ""
    for nom_cat, stats in categories.items():
        html_sections_categories += f"""
        <div class="section-categorie mb-8" data-categorie="{nom_cat}">
            <div class="flex items-center justify-between mb-4 border-b border-stone-200 pb-2">
                <h3 class="text-lg font-black text-stone-800">{nom_cat}</h3>
            </div>
            <div class="grille-categories">
                {stats['html_especes']}
            </div>
        </div>
        """

    contenu = f"""
    <div class="flex justify-between items-end mb-4">
        <div>
            <h2 class="text-3xl font-black text-stone-800">Ton Carnet</h2>
            <p class="text-stone-500 font-medium mt-1">Score : <span id="score-total" class="text-lime-700 font-bold">{joueur['score_total']} pts</span></p>
        </div>
        <button onclick="toggleVue()" id="btn-vue" class="px-3 py-2 bg-white border border-stone-300 shadow-sm rounded-lg text-sm font-bold text-stone-600 hover:bg-stone-50 transition flex items-center">
            📄 Liste
        </button>
    </div>
    
    <div class="sticky top-0 bg-slate-50 z-40 -mx-4 px-4 md:-mx-8 md:px-8 border-b border-stone-200 mb-6 shadow-[0_4px_6px_-1px_rgba(248,250,252,1)]">
        {html_boutons_filtres}
    </div>

    <div id="liste-especes" class="mode-liste">
        {html_sections_categories}
    </div>

    <style>
        @media (max-width: 768px) {{
            .scroll-adaptatif::-webkit-scrollbar {{ display: none; }}
            .scroll-adaptatif {{ -ms-overflow-style: none; scrollbar-width: none; }}
        }}
        .scroll-adaptatif::-webkit-scrollbar {{ height: 6px; }}
        .scroll-adaptatif::-webkit-scrollbar-thumb {{ background-color: #cbd5e1; border-radius: 4px; }}

        .mode-liste .grille-categories {{ display: flex; flex-direction: column; gap: 0.75rem; }}
        .mode-liste .carte-espece {{ display: flex; flex-direction: row; height: 130px; }}
        .mode-liste .carte-img-container {{ width: 130px; height: 100%; border-right: 1px solid #e7e5e4; }}

        .mode-grille .grille-categories {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 1rem; }}
        .mode-grille .carte-espece {{ display: flex; flex-direction: column; height: 100%; }}
        .mode-grille .carte-img-container {{ width: 100%; height: 130px; border-bottom: 1px solid #e7e5e4; }}
        
        @media (min-width: 1024px) {{
            .mode-grille .grille-categories {{ grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1.5rem; }}
            .mode-grille .carte-img-container {{ height: 160px; }}
        }}
    </style>

    <script>
    function filtrerCategorie(categorieChoisie, boutonClique = null) {{
        // SI LE BOUTON ÉTAIT DÉJÀ ACTIF, ON RETOURNE SUR "TOUTES"
        if (boutonClique && boutonClique.classList.contains('active') && categorieChoisie !== 'Toutes') {{
            categorieChoisie = 'Toutes';
        }}

        const sections = document.querySelectorAll('.section-categorie');
        sections.forEach(sec => {{
            if (categorieChoisie === 'Toutes' || sec.dataset.categorie === categorieChoisie) {{
                sec.style.display = 'block';
            }} else {{
                sec.style.display = 'none';
            }}
        }});

        const boutons = document.querySelectorAll('.btn-filtre');
        boutons.forEach(btn => {{
            btn.className = "btn-filtre shrink-0 px-4 py-2 rounded-full bg-white border border-stone-200 text-stone-600 font-medium text-sm hover:bg-stone-50 hover:border-lime-300 transition";
            
            if (categorieChoisie === 'Toutes' && btn.innerText.trim() === 'Toutes') {{
                btn.className = "btn-filtre active shrink-0 px-4 py-2 rounded-full bg-lime-700 text-white font-bold text-sm shadow-sm transition";
            }} else if (categorieChoisie !== 'Toutes' && btn.innerText.includes(categorieChoisie)) {{
                btn.className = "btn-filtre active shrink-0 px-4 py-2 rounded-full bg-lime-700 text-white font-bold text-sm shadow-sm transition";
            }}
        }});
    }}

    function toggleVue(forcerMode = null) {{
        const conteneur = document.getElementById('liste-especes');
        const btn = document.getElementById('btn-vue');
        
        const modeActuel = conteneur.classList.contains('mode-liste') ? 'liste' : 'grille';
        const nouveauMode = forcerMode ? forcerMode : (modeActuel === 'liste' ? 'grille' : 'liste');

        if (nouveauMode === 'grille') {{
            conteneur.classList.remove('mode-liste');
            conteneur.classList.add('mode-grille');
            btn.innerHTML = '🔲 Grille';
            localStorage.setItem('vue-faunabingo', 'grille');
        }} else {{
            conteneur.classList.remove('mode-grille');
            conteneur.classList.add('mode-liste');
            btn.innerHTML = '📄 Liste';
            localStorage.setItem('vue-faunabingo', 'liste');
        }}
    }}

    document.addEventListener("DOMContentLoaded", () => {{
        const preference = localStorage.getItem('vue-faunabingo');
        if (preference === 'grille') {{
            toggleVue('grille');
        }}
    }});

    // --- MAGIE FLUIDE : Mise à jour sans rechargement ---
    document.addEventListener('submit', async function(e) {{
        // On vérifie que le formulaire envoyé se trouve bien dans une carte espèce
        if (e.target.closest('.carte-espece')) {{
            e.preventDefault(); // Bloque le rechargement brutal de la page
            
            const form = e.target;
            const formData = new FormData(form);
            
            // On ajoute la valeur du bouton cliqué au formulaire (Vu, Entendu, Photo)
            const submitter = e.submitter;
            if (submitter && submitter.name) {{
                formData.append(submitter.name, submitter.value);
            }}
            
            // On envoie les données au serveur en arrière-plan
            const response = await fetch(form.action, {{
                method: form.method,
                body: formData
            }});
            
            if (response.ok) {{
                // On récupère la nouvelle page web générée par le serveur
                const texteHTML = await response.text();
                const parser = new DOMParser();
                const nouvellePage = parser.parseFromString(texteHTML, "text/html");
                
                // 1. Mettre à jour UNIQUEMENT la carte de l'animal modifié
                const idEspece = form.querySelector('input[name="id_espece"]').value;
                const ancienneCarte = document.getElementById('espece-' + idEspece);
                const nouvelleCarte = nouvellePage.getElementById('espece-' + idEspece);
                if (ancienneCarte && nouvelleCarte) {{
                    ancienneCarte.innerHTML = nouvelleCarte.innerHTML;
                    ancienneCarte.className = nouvelleCarte.className;
                }}
                
                // 2. Mettre à jour le score global en haut
                const ancienScore = document.getElementById('score-total');
                const nouveauScore = nouvellePage.getElementById('score-total');
                if (ancienScore && nouveauScore) {{
                    ancienScore.innerHTML = nouveauScore.innerHTML;
                }}
                
                // 3. Mettre à jour les compteurs des filtres (X/Y trouvées)
                const anciensFiltres = document.getElementById('conteneur-filtres');
                const nouveauxFiltres = nouvellePage.getElementById('conteneur-filtres');
                if (anciensFiltres && nouveauxFiltres) {{
                    anciensFiltres.innerHTML = nouveauxFiltres.innerHTML;
                }}
                
                // 4. Réappliquer le filtre visuel actuel pour ne rien casser
                const filtreActif = document.querySelector('.btn-filtre.active');
                if (filtreActif) {{
                    const nomFiltre = filtreActif.childNodes[0].nodeValue.trim();
                    filtrerCategorie(nomFiltre);
                }}
            }}
        }}
    }});
    </script>
    """
    
    header_links = """
    <div class="flex space-x-2 items-center">
        <a href="/amis" class="text-[10px] sm:text-xs bg-lime-800 hover:bg-lime-900 px-2 sm:px-3 py-1.5 rounded-lg transition font-medium shadow-sm">🤝 Amis</a>
        <a href="/classement" class="text-[10px] sm:text-xs bg-lime-800 hover:bg-lime-900 px-2 sm:px-3 py-1.5 rounded-lg transition font-medium shadow-sm">🏆 Classement</a>
        <a href="/deconnexion" class="text-[10px] sm:text-xs bg-stone-700 hover:bg-red-700 px-2 sm:px-3 py-1.5 rounded-lg transition font-medium shadow-sm">👋 Quitter</a>
    </div>
    """
    
    return layout_jeu(f"Carnet - {joueur['prenom']}", contenu, header_links)





# --- ACTIONS : OBSERVER ET ANNULER ---
@router.post("/carnet/{id_participant}/observer")
def enregistrer_observation(request: Request, id_participant: str, id_espece: str = Form(...), type_preuve: str = Form(...)):
    # Sécurité : on vérifie que l'action est bien faite par le propriétaire du carnet
    session_id = request.cookies.get("session_faunabingo")
    if session_id != id_participant:
        return RedirectResponse(url="/connexion", status_code=303)
        
    valeur_preuve = {'ENTENDU': 1, 'VU': 2, 'PHOTO': 3}
    
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id_observation, type_preuve FROM Observation WHERE id_participant = ? AND id_espece = ?", (id_participant, id_espece))
        obs_existante = cursor.fetchone()
        
        cursor.execute("SELECT points_entendu, points_vu, points_photo FROM Espece WHERE id_espece = ?", (id_espece,))
        esp = cursor.fetchone()
        pts = {'ENTENDU': esp[0], 'VU': esp[1], 'PHOTO': esp[2]}
        
        if obs_existante:
            ancien_type = obs_existante[1]
            # On améliore l'observation seulement si la nouvelle preuve est meilleure
            if valeur_preuve[type_preuve] > valeur_preuve[ancien_type]:
                points_supplementaires = pts[type_preuve] - pts[ancien_type]
                cursor.execute("UPDATE Observation SET type_preuve = ? WHERE id_observation = ?", (type_preuve, obs_existante[0]))
                cursor.execute("UPDATE Participant SET score_total = score_total + ? WHERE id_participant = ?", (points_supplementaires, id_participant))
        else:
            id_observation = str(uuid.uuid4())
            cursor.execute("INSERT INTO Observation (id_observation, id_participant, id_espece, type_preuve) VALUES (?, ?, ?, ?)", (id_observation, id_participant, id_espece, type_preuve))
            cursor.execute("UPDATE Participant SET score_total = score_total + ? WHERE id_participant = ?", (pts[type_preuve], id_participant))
            
        conn.commit()
    return RedirectResponse(url=f"/carnet/{id_participant}", status_code=303)

@router.post("/carnet/{id_participant}/annuler")
def annuler_observation(request: Request, id_participant: str, id_espece: str = Form(...)):
    # Sécurité
    session_id = request.cookies.get("session_faunabingo")
    if session_id != id_participant:
        return RedirectResponse(url="/connexion", status_code=303)
        
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id_observation, type_preuve FROM Observation WHERE id_participant = ? AND id_espece = ?", (id_participant, id_espece))
        obs = cursor.fetchone()
        
        if obs:
            cursor.execute("SELECT points_entendu, points_vu, points_photo FROM Espece WHERE id_espece = ?", (id_espece,))
            esp = cursor.fetchone()
            pts = {'ENTENDU': esp[0], 'VU': esp[1], 'PHOTO': esp[2]}
            
            cursor.execute("UPDATE Participant SET score_total = score_total - ? WHERE id_participant = ?", (pts[obs[1]], id_participant))
            cursor.execute("DELETE FROM Observation WHERE id_observation = ?", (obs[0],))
            conn.commit()
    return RedirectResponse(url=f"/carnet/{id_participant}", status_code=303)

# --- PAGE 3 : LE CLASSEMENT EN DIRECT ---
@router.get("/classement", response_class=HTMLResponse)
def page_classement(request: Request, amis: str = "0"):
    session_id = request.cookies.get("session_faunabingo")
    if not session_id:
        return RedirectResponse(url="/connexion", status_code=303)
        
    # Vérifie si on veut voir le classement filtré sur les amis
    vue_amis = (amis == "1")
    
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Info du joueur actuel
        cursor.execute("SELECT prenom FROM Participant WHERE id_participant = ?", (session_id,))
        joueur = cursor.fetchone()
        
        if vue_amis:
            # REQUÊTE AMIS : Moi-même + Tous mes amis acceptés (dans les deux sens)
            cursor.execute("""
                SELECT id_participant, prenom, score_total 
                FROM Participant 
                WHERE id_participant = ? 
                   OR id_participant IN (
                       SELECT id_receveur FROM Amitie WHERE id_demandeur = ? AND statut = 'ACCEPTE'
                       UNION
                       SELECT id_demandeur FROM Amitie WHERE id_receveur = ? AND statut = 'ACCEPTE'
                   )
                ORDER BY score_total DESC
            """, (session_id, session_id, session_id))
        else:
            # REQUÊTE GLOBALE : Tout le monde
            cursor.execute("""
                SELECT id_participant, prenom, score_total 
                FROM Participant 
                ORDER BY score_total DESC
            """)
            
        classement = cursor.fetchall()

    # --- CONSTRUCTION DE L'INTERFACE ---
    
    # Boutons pour basculer (style "Switch" iOS)
    style_btn_actif = "bg-white shadow-sm text-stone-800 pointer-events-none"
    style_btn_inactif = "text-stone-500 hover:text-stone-800"
    
    html_boutons = f"""
    <div class="flex p-1 bg-stone-200 rounded-lg mb-6 mx-auto max-w-sm">
        <a href="/classement" class="flex-1 text-center py-2 text-sm font-bold rounded-md transition {style_btn_actif if not vue_amis else style_btn_inactif}">
            🌍 Global
        </a>
        <a href="/classement?amis=1" class="flex-1 text-center py-2 text-sm font-bold rounded-md transition {style_btn_actif if vue_amis else style_btn_inactif}">
            🤝 Mes Amis
        </a>
    </div>
    """

    # Liste du classement
    html_liste = '<div class="space-y-3 max-w-2xl mx-auto">'
    for index, p in enumerate(classement):
        rank = index + 1
        
        # Les médailles pour le podium
        if rank == 1: medaille = "🥇"
        elif rank == 2: medaille = "🥈"
        elif rank == 3: medaille = "🥉"
        else: medaille = f"<span class='text-stone-400 font-bold text-sm'>#{rank}</span>"
        
        # Mettre en évidence le joueur connecté
        est_moi = (p['id_participant'] == session_id)
        bg_class = "bg-lime-50 border-lime-200" if est_moi else "bg-white border-stone-200"
        text_class = "text-lime-800" if est_moi else "text-stone-800"
        label_moi = "<span class='ml-2 text-[10px] bg-lime-200 text-lime-800 px-2 py-0.5 rounded-full font-black uppercase'>Toi</span>" if est_moi else ""
        
        html_liste += f"""
        <div class="flex items-center justify-between p-4 rounded-xl shadow-sm border transition-all hover:shadow-md {bg_class}">
            <div class="flex items-center gap-3 sm:gap-5">
                <div class="w-8 text-center text-2xl">{medaille}</div>
                <div>
                    <div class="font-bold text-lg {text_class} flex items-center">{p['prenom']} {label_moi}</div>
                    <a href="/carnet/{p['id_participant']}" class="text-xs text-indigo-600 font-bold hover:underline transition">Voir son carnet 👀</a>
                </div>
            </div>
            <div class="text-right">
                <div class="font-black text-xl {text_class}">{p['score_total']}</div>
                <div class="text-[10px] uppercase font-bold text-stone-400 -mt-1">Points</div>
            </div>
        </div>
        """
        
    html_liste += '</div>'
    
    # Petit message sympa si le joueur filtre sur "Amis" mais n'en a pas encore
    if vue_amis and len(classement) == 1:
        html_liste += """
        <div class="text-center p-6 bg-white rounded-xl shadow-sm border border-stone-200 mt-4 max-w-2xl mx-auto">
            <div class="text-4xl mb-2">😢</div>
            <p class="text-sm text-stone-600 font-medium mb-4">Tu es seul dans ce classement pour le moment...</p>
            <a href="/amis" class="inline-block bg-lime-700 hover:bg-lime-800 text-white font-bold py-2 px-5 rounded-xl transition shadow-sm">
                Ajouter des amis
            </a>
        </div>
        """

    contenu = f"""
    <div class="text-center mb-6">
        <h2 class="text-3xl font-black text-stone-800 mb-2">Classement</h2>
        <p class="text-stone-500 text-sm">Découvre qui est le meilleur explorateur.</p>
    </div>
    
    {html_boutons}
    {html_liste}
    """
    
    header_links = f"""
    <div class="flex space-x-2 items-center">
        <a href="/amis" class="text-[10px] sm:text-xs bg-lime-800 hover:bg-lime-900 px-2 sm:px-3 py-1.5 rounded-lg transition font-medium shadow-sm">🤝 Amis</a>
        <a href="/carnet/{session_id}" class="text-[10px] sm:text-xs bg-lime-800 hover:bg-lime-900 px-2 sm:px-3 py-1.5 rounded-lg transition font-medium shadow-sm">📖 Mon Carnet</a>
        <a href="/deconnexion" class="text-[10px] sm:text-xs bg-stone-700 hover:bg-red-700 px-2 sm:px-3 py-1.5 rounded-lg transition font-medium shadow-sm">👋 Quitter</a>
    
    </div>
    """
    
    return layout_jeu(f"Classement - {joueur['prenom']}", contenu, header_links)

@router.get("/mon-carnet")
def redirection_mon_carnet(request: Request):
    """Redirige toujours vers le carnet du joueur connecté."""
    session_id = request.cookies.get("session_faunabingo")
    if session_id:
        return RedirectResponse(url=f"/carnet/{session_id}", status_code=303)
    return RedirectResponse(url="/connexion", status_code=303)


@router.get("/comparer", response_class=HTMLResponse)
def page_comparaison_groupe(request: Request, amis_ids: list[str] = Query(default=[])):
    session_id = request.cookies.get("session_faunabingo")
    if not session_id: return RedirectResponse(url="/connexion", status_code=303)

    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 1. Récupérer tes infos
        cursor.execute("SELECT id_participant, prenom FROM Participant WHERE id_participant = ?", (session_id,))
        moi = cursor.fetchone()
        
        # Sécurité si le cookie est périmé
        if not moi:
            return RedirectResponse(url="/deconnexion", status_code=303)

        # 2. Récupérer UNIQUEMENT les amis qui ont été cochés
        mes_amis = []
        if amis_ids:
            placeholders = ','.join(['?'] * len(amis_ids))
            parametres_sql = [session_id, session_id, session_id] + amis_ids
            
            cursor.execute(f"""
                SELECT p.id_participant, p.prenom 
                FROM Amitie a
                JOIN Participant p ON (p.id_participant = a.id_demandeur OR p.id_participant = a.id_receveur)
                WHERE (a.id_demandeur = ? OR a.id_receveur = ?) 
                  AND a.statut = 'ACCEPTE' 
                  AND p.id_participant != ?
                  AND p.id_participant IN ({placeholders})
            """, tuple(parametres_sql))
            mes_amis = cursor.fetchall()
        
        # On crée le groupe : Toi + Tes amis sélectionnés
        joueurs = [moi] + mes_amis
        ids_joueurs = [j['id_participant'] for j in joueurs]

        # 3. Récupérer toutes les espèces
        cursor.execute("SELECT * FROM Espece ORDER BY classe, nom_courant")
        toutes_especes = cursor.fetchall()

        # 4. Récupérer les observations de ce groupe spécifique
        placeholders_obs = ','.join(['?'] * len(ids_joueurs))
        cursor.execute(f"SELECT id_participant, id_espece, type_preuve FROM Observation WHERE id_participant IN ({placeholders_obs})", tuple(ids_joueurs))
        obs_brutes = cursor.fetchall()

        # 5. On range les observations par joueur
        obs_groupe = {j['id_participant']: {} for j in joueurs}
        for o in obs_brutes:
            obs_groupe[o['id_participant']][o['id_espece']] = o['type_preuve']

    # --- CONSTRUCTION DU TABLEAU MULTI-JOUEURS ---
    
    def icone_preuve(preuve):
        if preuve == "PHOTO": return "📸"
        if preuve == "VU": return "👀"
        if preuve == "ENTENDU": return "🔊"
        return "<span class='text-stone-200 font-normal'>-</span>"

    # En-têtes (Toi, Ami 1, Ami 2...)
    html_entetes = f'<th class="px-3 py-3 font-bold text-sm min-w-[160px] sticky left-0 bg-stone-800 z-20 shadow-[2px_0_5px_-2px_rgba(0,0,0,0.3)]">Espèce</th>'
    for j in joueurs:
        if j['id_participant'] == session_id:
            nom = "Toi"
            bg_th = "bg-lime-700"
        else:
            nom = j['prenom']
            bg_th = "bg-stone-700"
        html_entetes += f'<th class="px-2 py-3 font-bold text-sm text-center min-w-[80px] {bg_th} border-l border-stone-600 z-10">{nom}</th>'

    html_lignes = ""
    categorie_actuelle = ""
    colonnes_totales = len(joueurs) + 1

    for esp in toutes_especes:
        nom_cat = esp['classe'] if esp['classe'] else "Non classé"
        
        # Intercalaire de catégorie
        if nom_cat != categorie_actuelle:
            html_lignes += f'''
            <tr class="bg-stone-200 border-b border-stone-300">
                <td colspan="{colonnes_totales}" class="px-3 py-2 font-black text-stone-700 text-sm uppercase tracking-wide sticky left-0 z-10 bg-stone-200 shadow-[2px_0_5px_-2px_rgba(0,0,0,0.1)]">{nom_cat}</td>
            </tr>
            '''
            categorie_actuelle = nom_cat

        # Vérifier si au moins une personne du groupe a trouvé l'animal
        nb_trouvailles = sum(1 for j in joueurs if esp['id_espece'] in obs_groupe[j['id_participant']])
        opacite = "opacity-50 grayscale" if nb_trouvailles == 0 else ""
        img_src = f"/{esp['image_reference']}" if esp['image_reference'] else "/static/placeholder.png"

        html_lignes += f'<tr class="border-b border-stone-100 {opacite}">'
        
        # Colonne Espèce (Toujours fixée à gauche)
        html_lignes += f'''
            <td class="px-2 py-2 flex items-center gap-3 sticky left-0 bg-white shadow-[2px_0_5px_-2px_rgba(0,0,0,0.1)] z-10">
                <img src="{img_src}" class="w-10 h-10 sm:w-12 sm:h-12 rounded-lg object-cover bg-stone-100 shrink-0 shadow-sm">
                <div>
                    <div class="font-bold text-stone-800 text-xs sm:text-sm leading-tight">{esp['nom_courant']}</div>
                    <div class="text-[9px] sm:text-[10px] text-stone-500 italic">{esp['nom_scientifique']}</div>
                </div>
            </td>
        '''
        
        # Colonnes des joueurs
        for index, j in enumerate(joueurs):
            preuve = obs_groupe[j['id_participant']].get(esp['id_espece'])
            
            # Petites couleurs alternées pour aider la lecture horizontale
            if j['id_participant'] == session_id:
                bg_cell = "bg-lime-50" if preuve else "bg-white"
            else:
                bg_cell = "bg-indigo-50" if preuve else ("bg-stone-50" if index % 2 == 1 else "bg-white")
                
            html_lignes += f'<td class="text-center text-lg {bg_cell} border-l border-stone-100">{icone_preuve(preuve)}</td>'
            
        html_lignes += '</tr>'

    contenu = f"""
    <div class="flex justify-between items-center mb-6">
        <div>
            <h2 class="text-2xl font-black text-stone-800">Comparateur ⚔️</h2>
            <p class="text-stone-500 text-sm">Le tableau de chasse du groupe</p>
        </div>
        <a href="/amis" class="px-3 py-2 bg-white border border-stone-300 shadow-sm rounded-lg text-sm font-bold text-stone-600 hover:bg-stone-50 transition flex items-center gap-1">
            ⬅️ <span class="hidden sm:inline">Retour</span>
        </a>
    </div>

    <div class="bg-white rounded-xl shadow-sm border border-stone-200 overflow-x-auto mb-8 relative">
        <table class="w-full text-left border-collapse min-w-max">
            <thead>
                <tr class="bg-stone-800 text-white">
                    {html_entetes}
                </tr>
            </thead>
            <tbody>
                {html_lignes}
            </tbody>
        </table>
    </div>
    """
    
    return layout_jeu("Comparateur", contenu)   