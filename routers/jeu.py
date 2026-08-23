import sqlite3
import uuid
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

router = APIRouter(tags=["Jeu"])
DB_NAME = "database/bingo_faune.db"

def layout_jeu(titre: str, contenu: str, header_links: str = ""):
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
        <nav class="bg-lime-700 text-white shadow-md mb-6">
            <div class="max-w-5xl mx-auto px-4 py-3 flex justify-between items-center">
                <h1 class="text-xl font-bold tracking-tight">🌿 FaunaBingo</h1>
                {header_links}
            </div>
        </nav>
        <!-- CORRECTION ICI : max-w-5xl permet d'élargir sur PC ! -->
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
def page_classement():
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id_participant, p.prenom, p.score_total,
                   COUNT(o.id_observation) as total_obs,
                   SUM(CASE WHEN o.type_preuve = 'PHOTO' THEN 1 ELSE 0 END) as total_photos
            FROM Participant p LEFT JOIN Observation o ON p.id_participant = o.id_participant
            GROUP BY p.id_participant ORDER BY p.score_total DESC, total_obs DESC
        """)
        classement = cursor.fetchall()

    html_lignes = ""
    for index, joueur in enumerate(classement):
        medaille = ["🥇", "🥈", "🥉"][index] if index < 3 else f"<span class='text-xl text-stone-400 font-black'>{index+1}</span>"
        bg_color = ["bg-amber-100 border-amber-300", "bg-slate-200 border-slate-400", "bg-orange-100 border-orange-300"][index] if index < 3 else "bg-white border-stone-200"
        text_color = ["text-amber-800", "text-slate-800", "text-orange-800"][index] if index < 3 else "text-stone-700"

        html_lignes += f"""
        <div class="{bg_color} border p-4 rounded-2xl shadow-sm mb-3 flex items-center justify-between transition">
            <div class="flex items-center space-x-4"><div class="text-3xl w-10 text-center">{medaille}</div><div><h3 class="text-lg font-bold {text_color} leading-tight">{joueur['prenom']}</h3><p class="text-[11px] text-stone-500 mt-1 uppercase tracking-wide font-medium">{joueur['total_obs']} Espèces • {joueur['total_photos'] or 0} Photos</p></div></div>
            <div class="text-right"><div class="text-3xl font-black {text_color} leading-none">{joueur['score_total']}</div><div class="text-[10px] uppercase font-bold text-stone-400 tracking-wider mt-1">Points</div></div>
        </div>
        """
    contenu = f'<div class="mb-8 text-center mt-4"><h2 class="text-3xl font-black text-stone-800 mb-2 tracking-tight">Le Podium</h2></div><div class="space-y-2">{html_lignes if html_lignes else "<p>Aucun participant.</p>"}</div>'
    return layout_jeu("Classement", contenu, '<a href="/" class="text-xs bg-lime-800 hover:bg-lime-900 px-3 py-1.5 rounded-lg transition font-medium shadow-sm flex items-center">🏠 Retour</a>')