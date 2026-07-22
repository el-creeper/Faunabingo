import sqlite3
import uuid
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

router = APIRouter(tags=["Jeu"])
DB_NAME = "database/bingo_faune.db"

def layout_jeu(titre: str, contenu: str, header_links: str = "") -> str:
    return f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>{titre}</title>
        <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    </head>
    <body class="bg-stone-100 text-stone-800 font-sans min-h-screen pb-16">
        <nav class="bg-lime-700 text-white shadow-md sticky top-0 z-50">
            <div class="max-w-md mx-auto px-4 py-3 flex justify-between items-center">
                <a href="/" class="text-xl font-bold tracking-wide">🌿 FaunaBingo</a>
                {header_links}
            </div>
        </nav>
        <main class="max-w-md mx-auto px-4 py-6">
            {contenu}
        </main>
    </body>
    </html>
    """

@router.get("/", response_class=HTMLResponse)
def page_accueil():
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Participant ORDER BY prenom")
        participants = cursor.fetchall()
    
    boutons = "".join([f'<a href="/carnet/{p["id_participant"]}" class="block w-full bg-white p-5 rounded-2xl shadow-sm border border-stone-200 mb-4 hover:bg-lime-50 hover:border-lime-400 transition active:scale-95 text-center"><span class="text-xl font-bold text-stone-700">{p["prenom"]}</span></a>' for p in participants])

    contenu = f"""
    <div class="text-center mb-8 mt-4"><h2 class="text-3xl font-black text-stone-800 mb-2 tracking-tight">L'Expédition</h2><p class="text-stone-500 text-sm">Sélectionne ton profil pour accéder à ton carnet.</p></div>
    <div class="space-y-2">{boutons if boutons else '<p class="text-center text-stone-400">Aucun participant.</p>'}</div>
    <div class="mt-8"><a href="/classement" class="block w-full bg-amber-500 hover:bg-amber-600 text-white p-4 rounded-xl shadow-sm font-bold text-center transition active:scale-95 text-lg">🏆 Voir le Classement</a></div>
    <div class="mt-16 text-center"><a href="/admin" class="text-xs text-stone-400 underline hover:text-stone-600 transition">⚙️ Panel d'administration</a></div>
    """
    return layout_jeu("Accueil", contenu)


@router.get("/carnet/{id_participant}", response_class=HTMLResponse)
def carnet_bord(id_participant: str):
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT prenom FROM Participant WHERE id_participant = ?", (id_participant,))
        joueur = cursor.fetchone()
        if not joueur: return RedirectResponse(url="/")
            
        cursor.execute("""
            SELECT e.*, o.type_preuve, o.id_observation 
            FROM Espece e LEFT JOIN Observation o ON e.id_espece = o.id_espece AND o.id_participant = ?
            ORDER BY e.classe, e.nom_courant
        """, (id_participant,))
        especes = cursor.fetchall()

    groupes = {}
    for esp in especes:
        classe = esp['classe'] or 'Autres'
        if classe not in groupes: groupes[classe] = []
        groupes[classe].append(esp)

    html_groupes = ""
    for classe, liste_especes in groupes.items():
        html_groupes += f'<h3 class="text-lg font-bold text-stone-700 mt-6 mb-3 border-b-2 border-lime-200 pb-1 categorie-titre">{classe}</h3><div class="space-y-3">'
        
        for esp in liste_especes:
            img_html = f'<img src="/{esp["image_reference"]}" class="w-20 h-20 object-cover rounded-lg shadow-sm">' if esp['image_reference'] else '<div class="w-20 h-20 bg-stone-200 rounded-lg flex items-center justify-center text-[10px] text-stone-400">Pas photo</div>'
            
            # --- LOGIQUE D'AFFICHAGE A 3 ETAPES ---
            actions_html = ""
            btn_entendu = f'<form action="/carnet/{id_participant}/observer" method="POST" class="flex-1"><input type="hidden" name="id_espece" value="{esp["id_espece"]}"><input type="hidden" name="type_preuve" value="ENTENDU"><button type="submit" class="w-full bg-indigo-500 text-white text-[10px] font-bold py-1.5 rounded-lg shadow-sm active:scale-95 transition">🎧 ({esp["points_entendu"]})</button></form>' if esp['points_entendu'] > 0 else ''
            btn_vu = f'<form action="/carnet/{id_participant}/observer" method="POST" class="flex-1"><input type="hidden" name="id_espece" value="{esp["id_espece"]}"><input type="hidden" name="type_preuve" value="VU"><button type="submit" class="w-full bg-amber-500 text-white text-[10px] font-bold py-1.5 rounded-lg shadow-sm active:scale-95 transition">👀 ({esp["points_vu"]})</button></form>'
            btn_photo = f'<form action="/carnet/{id_participant}/observer" method="POST" class="flex-1"><input type="hidden" name="id_espece" value="{esp["id_espece"]}"><input type="hidden" name="type_preuve" value="PHOTO"><button type="submit" class="w-full bg-emerald-600 text-white text-[10px] font-bold py-1.5 rounded-lg shadow-sm active:scale-95 transition">📸 ({esp["points_photo"]})</button></form>'
            btn_annuler = f'<form action="/carnet/{id_participant}/annuler" method="POST" class="flex-none"><input type="hidden" name="id_espece" value="{esp["id_espece"]}"><button type="submit" class="text-stone-400 hover:text-red-500 px-2 py-1" title="Annuler">❌</button></form>'

            if esp['type_preuve'] == 'PHOTO':
                actions_html = f'<div class="flex items-center justify-between mt-2"><div class="inline-block px-3 py-1 rounded-full text-[10px] font-bold border bg-emerald-100 text-emerald-800 border-emerald-300">📸 PHOTO !</div>{btn_annuler}</div>'
            elif esp['type_preuve'] == 'VU':
                pts_diff = esp['points_photo'] - esp['points_vu']
                actions_html = f'<div class="flex items-center space-x-1 mt-2"><div class="inline-block px-2 py-1.5 rounded-lg text-[10px] font-bold border bg-amber-100 text-amber-800 border-amber-300 shadow-sm">👀 VU !</div><form action="/carnet/{id_participant}/observer" method="POST" class="flex-1"><input type="hidden" name="id_espece" value="{esp["id_espece"]}"><input type="hidden" name="type_preuve" value="PHOTO"><button type="submit" class="w-full bg-emerald-600 text-white text-[10px] font-bold py-1.5 rounded-lg shadow-sm active:scale-95 transition">📸 Photo (+{pts_diff})</button></form>{btn_annuler}</div>'
            elif esp['type_preuve'] == 'ENTENDU':
                pts_diff_vu = esp['points_vu'] - esp['points_entendu']
                pts_diff_photo = esp['points_photo'] - esp['points_entendu']
                actions_html = f'<div class="flex items-center space-x-1 mt-2"><div class="inline-block px-2 py-1.5 rounded-lg text-[10px] font-bold border bg-indigo-100 text-indigo-800 border-indigo-300 shadow-sm">🎧 ENTENDU !</div><form action="/carnet/{id_participant}/observer" method="POST" class="flex-1"><input type="hidden" name="id_espece" value="{esp["id_espece"]}"><input type="hidden" name="type_preuve" value="VU"><button type="submit" class="w-full bg-amber-500 text-white text-[10px] font-bold py-1.5 rounded-lg shadow-sm active:scale-95 transition">👀 Vu (+{pts_diff_vu})</button></form><form action="/carnet/{id_participant}/observer" method="POST" class="flex-1"><input type="hidden" name="id_espece" value="{esp["id_espece"]}"><input type="hidden" name="type_preuve" value="PHOTO"><button type="submit" class="w-full bg-emerald-600 text-white text-[10px] font-bold py-1.5 rounded-lg shadow-sm active:scale-95 transition">📸 Ph (+{pts_diff_photo})</button></form>{btn_annuler}</div>'
            else:
                actions_html = f'<div class="flex space-x-1 mt-2">{btn_entendu}{btn_vu}{btn_photo}</div>'

            html_groupes += f'<div class="bg-white p-3 rounded-xl shadow-sm border border-stone-200 animal-card" data-nom="{esp["nom_courant"].lower()} {esp["nom_scientifique"].lower() if esp["nom_scientifique"] else ""}"><div class="flex space-x-3">{img_html}<div class="flex-1"><h4 class="font-bold text-stone-800 leading-tight">{esp["nom_courant"]}</h4><p class="text-[10px] italic text-stone-500 mb-1">{esp["nom_scientifique"] or ""}</p>{actions_html}</div></div></div>'
        html_groupes += '</div>'

    contenu = f"""
    <div class="mb-5 flex justify-between items-end"><div><p class="text-sm text-stone-500">Carnet de bord</p><h2 class="text-2xl font-bold text-stone-800">{joueur['prenom']}</h2></div></div>
    <div class="sticky top-[58px] z-40 bg-stone-100 py-2 pb-4"><input type="text" id="searchBar" onkeyup="rechercherAnimal()" placeholder="🔍 Rechercher un animal..." class="w-full px-4 py-3 rounded-xl border border-stone-300 shadow-sm focus:outline-lime-500 text-sm"></div>
    {html_groupes}
    <script>
    function rechercherAnimal() {{
        let texte = document.getElementById('searchBar').value.toLowerCase();
        document.querySelectorAll('.animal-card').forEach(carte => {{
            carte.style.display = carte.getAttribute('data-nom').includes(texte) ? 'block' : 'none';
        }});
        document.querySelectorAll('.categorie-titre').forEach(titre => {{
            let hasVisible = Array.from(titre.nextElementSibling.querySelectorAll('.animal-card')).some(c => c.style.display !== 'none');
            titre.style.display = hasVisible ? 'block' : 'none';
        }});
    }}
    </script>
    """
    return layout_jeu(f"Carnet - {joueur['prenom']}", contenu, '<a href="/classement" class="text-xs bg-lime-800 hover:bg-lime-900 px-3 py-1.5 rounded-lg transition font-medium shadow-sm">🏆 Classement</a>')


@router.post("/carnet/{id_participant}/observer")
def enregistrer_observation(id_participant: str, id_espece: str = Form(...), type_preuve: str = Form(...)):
    # Ordre d'importance des preuves pour éviter les régressions
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
def annuler_observation(id_participant: str, id_espece: str = Form(...)):
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

# --- PAGE 1 : CHOIX DU JOUEUR ---
@router.get("/", response_class=HTMLResponse)
def page_accueil():
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Participant ORDER BY prenom")
        participants = cursor.fetchall()
    
    boutons = ""
    for p in participants:
        boutons += f"""
        <a href="/carnet/{p['id_participant']}" class="block w-full bg-white p-5 rounded-2xl shadow-sm border border-stone-200 mb-4 hover:bg-lime-50 hover:border-lime-400 transition active:scale-95 text-center">
            <span class="text-xl font-bold text-stone-700">{p['prenom']}</span>
        </a>
        """

    contenu = f"""
    <div class="text-center mb-8 mt-4">
        <h2 class="text-3xl font-black text-stone-800 mb-2 tracking-tight">L'Expédition</h2>
        <p class="text-stone-500 text-sm">Sélectionne ton profil pour accéder à ton carnet.</p>
    </div>
    <div class="space-y-2">
        {boutons if boutons else '<p class="text-center text-stone-400">Aucun participant trouvé.</p>'}
    </div>
    
    <div class="mt-8">
        <a href="/classement" class="block w-full bg-amber-500 hover:bg-amber-600 text-white p-4 rounded-xl shadow-sm font-bold text-center transition active:scale-95 text-lg">
            🏆 Voir le Classement
        </a>
    </div>

    <div class="mt-16 text-center">
        <a href="/admin" class="text-xs text-stone-400 underline hover:text-stone-600 transition">⚙️ Panel d'administration</a>
    </div>
    """
    return layout_jeu("Accueil - FaunaBingo", contenu)

# --- PAGE 2 : LE CARNET DE BORD ---
@router.get("/carnet/{id_participant}", response_class=HTMLResponse)
def carnet_bord(id_participant: str):
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT prenom FROM Participant WHERE id_participant = ?", (id_participant,))
        joueur = cursor.fetchone()
        if not joueur:
            return RedirectResponse(url="/")
            
        cursor.execute("""
            SELECT e.*, o.type_preuve, o.id_observation 
            FROM Espece e
            LEFT JOIN Observation o ON e.id_espece = o.id_espece AND o.id_participant = ?
            ORDER BY e.classe, e.nom_courant
        """, (id_participant,))
        especes = cursor.fetchall()

    groupes = {}
    for esp in especes:
        classe = esp['classe'] or 'Autres'
        if classe not in groupes:
            groupes[classe] = []
        groupes[classe].append(esp)

    html_groupes = ""
    for classe, liste_especes in groupes.items():
        html_groupes += f'<h3 class="text-lg font-bold text-stone-700 mt-6 mb-3 border-b-2 border-lime-200 pb-1 categorie-titre">{classe}</h3>'
        html_groupes += '<div class="space-y-3">'
        
        for esp in liste_especes:
            img_html = f'<img src="/{esp["image_reference"]}" class="w-20 h-20 object-cover rounded-lg shadow-sm">' if esp['image_reference'] else '<div class="w-20 h-20 bg-stone-200 rounded-lg flex items-center justify-center text-[10px] text-stone-400">Pas photo</div>'
            
            actions_html = ""
            if esp['type_preuve'] == 'PHOTO':
                actions_html = f"""
                    <div class="flex items-center justify-between mt-2">
                        <div class="inline-block px-3 py-1 rounded-full text-[10px] font-bold border bg-emerald-100 text-emerald-800 border-emerald-300">
                            📸 PHOTO !
                        </div>
                        <form action="/carnet/{id_participant}/annuler" method="POST">
                            <input type="hidden" name="id_espece" value="{esp['id_espece']}">
                            <button type="submit" class="text-stone-400 hover:text-red-500 text-[10px] underline px-2 py-1">Annuler</button>
                        </form>
                    </div>
                """
            elif esp['type_preuve'] == 'VU':
                pts_diff = esp['points_photo'] - esp['points_vu']
                actions_html = f"""
                    <div class="flex items-center space-x-1 mt-2">
                        <div class="inline-block px-2 py-1.5 rounded-lg text-[10px] font-bold border bg-amber-100 text-amber-800 border-amber-300 shadow-sm whitespace-nowrap">
                            👀 VU !
                        </div>
                        <form action="/carnet/{id_participant}/observer" method="POST" class="flex-1">
                            <input type="hidden" name="id_espece" value="{esp['id_espece']}">
                            <input type="hidden" name="type_preuve" value="PHOTO">
                            <button type="submit" class="w-full bg-emerald-600 hover:bg-emerald-700 active:scale-95 text-white text-[10px] font-bold py-1.5 rounded-lg shadow-sm transition">
                                📸 Photo ! (+{pts_diff} pts)
                            </button>
                        </form>
                        <form action="/carnet/{id_participant}/annuler" method="POST" class="flex-none">
                            <input type="hidden" name="id_espece" value="{esp['id_espece']}">
                            <button type="submit" class="text-stone-400 hover:text-red-500 px-2 py-1 transition" title="Annuler">❌</button>
                        </form>
                    </div>
                """
            else:
                actions_html = f"""
                    <div class="flex space-x-2 mt-2">
                        <form action="/carnet/{id_participant}/observer" method="POST" class="w-1/2">
                            <input type="hidden" name="id_espece" value="{esp['id_espece']}">
                            <input type="hidden" name="type_preuve" value="VU">
                            <button type="submit" class="w-full bg-amber-500 hover:bg-amber-600 active:scale-95 text-white text-xs font-bold py-2 rounded-lg shadow-sm transition">👀 Vu ({esp['points_vu']})</button>
                        </form>
                        <form action="/carnet/{id_participant}/observer" method="POST" class="w-1/2">
                            <input type="hidden" name="id_espece" value="{esp['id_espece']}">
                            <input type="hidden" name="type_preuve" value="PHOTO">
                            <button type="submit" class="w-full bg-emerald-600 hover:bg-emerald-700 active:scale-95 text-white text-xs font-bold py-2 rounded-lg shadow-sm transition">📸 Photo ({esp['points_photo']})</button>
                        </form>
                    </div>
                """

            html_groupes += f"""
            <div class="bg-white p-3 rounded-xl shadow-sm border border-stone-200 animal-card" data-nom="{esp['nom_courant'].lower()} {esp['nom_scientifique'].lower() if esp['nom_scientifique'] else ''}">
                <div class="flex space-x-3">
                    {img_html}
                    <div class="flex-1">
                        <h4 class="font-bold text-stone-800 leading-tight">{esp['nom_courant']}</h4>
                        <p class="text-[10px] italic text-stone-500 mb-1">{esp['nom_scientifique'] or ''}</p>
                        {actions_html}
                    </div>
                </div>
            </div>
            """
        html_groupes += '</div>'

    script_recherche = """
    <script>
    function rechercherAnimal() {
        let texte = document.getElementById('searchBar').value.toLowerCase();
        let cartes = document.querySelectorAll('.animal-card');
        cartes.forEach(carte => {
            let nom = carte.getAttribute('data-nom');
            carte.style.display = nom.includes(texte) ? 'block' : 'none';
        });
        document.querySelectorAll('.categorie-titre').forEach(titre => {
            let container = titre.nextElementSibling;
            let hasVisible = Array.from(container.querySelectorAll('.animal-card')).some(c => c.style.display !== 'none');
            titre.style.display = hasVisible ? 'block' : 'none';
        });
    }
    </script>
    """

    header_links = '<a href="/classement" class="text-xs bg-lime-800 hover:bg-lime-900 px-3 py-1.5 rounded-lg transition font-medium shadow-sm">🏆 Classement</a>'
    
    contenu = f"""
    <div class="mb-5 flex justify-between items-end">
        <div>
            <p class="text-sm text-stone-500">Carnet de bord</p>
            <h2 class="text-2xl font-bold text-stone-800">{joueur['prenom']}</h2>
        </div>
    </div>
    <div class="sticky top-[58px] z-40 bg-stone-100 py-2 pb-4">
        <input type="text" id="searchBar" onkeyup="rechercherAnimal()" placeholder="🔍 Rechercher un animal..." class="w-full px-4 py-3 rounded-xl border border-stone-300 shadow-sm focus:outline-lime-500 text-sm">
    </div>
    {html_groupes}
    {script_recherche}
    """
    
    return layout_jeu(f"Carnet - {joueur['prenom']}", contenu, header_links)

# --- ACTIONS : OBSERVER ET ANNULER ---
@router.post("/carnet/{id_participant}/observer")
def enregistrer_observation(id_participant: str, id_espece: str = Form(...), type_preuve: str = Form(...)):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT id_observation, type_preuve FROM Observation WHERE id_participant = ? AND id_espece = ?", (id_participant, id_espece))
        obs_existante = cursor.fetchone()
        
        cursor.execute("SELECT points_vu, points_photo FROM Espece WHERE id_espece = ?", (id_espece,))
        esp = cursor.fetchone()
        pts_vu, pts_photo = esp[0], esp[1]
        
        if obs_existante:
            if obs_existante[1] == 'VU' and type_preuve == 'PHOTO':
                cursor.execute("UPDATE Observation SET type_preuve = 'PHOTO' WHERE id_observation = ?", (obs_existante[0],))
                points_supplementaires = pts_photo - pts_vu
                cursor.execute("UPDATE Participant SET score_total = score_total + ? WHERE id_participant = ?", (points_supplementaires, id_participant))
        else:
            id_observation = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO Observation (id_observation, id_participant, id_espece, type_preuve)
                VALUES (?, ?, ?, ?)
            """, (id_observation, id_participant, id_espece, type_preuve))
            
            points_gagnes = pts_photo if type_preuve == 'PHOTO' else pts_vu
            cursor.execute("UPDATE Participant SET score_total = score_total + ? WHERE id_participant = ?", (points_gagnes, id_participant))
            
        conn.commit()
    return RedirectResponse(url=f"/carnet/{id_participant}", status_code=303)

@router.post("/carnet/{id_participant}/annuler")
def annuler_observation(id_participant: str, id_espece: str = Form(...)):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id_observation, type_preuve FROM Observation WHERE id_participant = ? AND id_espece = ?", (id_participant, id_espece))
        obs = cursor.fetchone()
        
        if obs:
            type_preuve = obs[1]
            cursor.execute("SELECT points_vu, points_photo FROM Espece WHERE id_espece = ?", (id_espece,))
            esp = cursor.fetchone()
            points_a_retirer = esp[1] if type_preuve == 'PHOTO' else esp[0]
            
            cursor.execute("UPDATE Participant SET score_total = score_total - ? WHERE id_participant = ?", (points_a_retirer, id_participant))
            cursor.execute("DELETE FROM Observation WHERE id_observation = ?", (obs[0],))
            conn.commit()

    return RedirectResponse(url=f"/carnet/{id_participant}", status_code=303)


# --- PAGE 3 : LE CLASSEMENT EN DIRECT ---
@router.get("/classement", response_class=HTMLResponse)
def page_classement():
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # On calcule le score total, le nombre d'animaux vus, et le nombre de photos
        cursor.execute("""
            SELECT p.id_participant, p.prenom, p.score_total,
                   COUNT(o.id_observation) as total_obs,
                   SUM(CASE WHEN o.type_preuve = 'PHOTO' THEN 1 ELSE 0 END) as total_photos
            FROM Participant p
            LEFT JOIN Observation o ON p.id_participant = o.id_participant
            GROUP BY p.id_participant
            ORDER BY p.score_total DESC, total_obs DESC
        """)
        classement = cursor.fetchall()

    html_lignes = ""
    for index, joueur in enumerate(classement):
        position = index + 1
        
        # Attribution des couleurs et médailles selon la place sur le podium
        if position == 1:
            medaille = "🥇"
            bg_color = "bg-amber-100 border-amber-300"
            text_color = "text-amber-800"
        elif position == 2:
            medaille = "🥈"
            bg_color = "bg-slate-200 border-slate-400"
            text_color = "text-slate-800"
        elif position == 3:
            medaille = "🥉"
            bg_color = "bg-orange-100 border-orange-300"
            text_color = "text-orange-800"
        else:
            medaille = f"<span class='text-xl text-stone-400 font-black'>{position}</span>"
            bg_color = "bg-white border-stone-200"
            text_color = "text-stone-700"
            
        total_obs = joueur['total_obs']
        total_photos = joueur['total_photos'] or 0

        html_lignes += f"""
        <div class="{bg_color} border p-4 rounded-2xl shadow-sm mb-3 flex items-center justify-between transition">
            <div class="flex items-center space-x-4">
                <div class="text-3xl w-10 text-center">{medaille}</div>
                <div>
                    <h3 class="text-lg font-bold {text_color} leading-tight">{joueur['prenom']}</h3>
                    <p class="text-[11px] text-stone-500 mt-1 uppercase tracking-wide font-medium">
                        {total_obs} Espèces • {total_photos} Photos
                    </p>
                </div>
            </div>
            <div class="text-right">
                <div class="text-3xl font-black {text_color} leading-none">{joueur['score_total']}</div>
                <div class="text-[10px] uppercase font-bold text-stone-400 tracking-wider mt-1">Points</div>
            </div>
        </div>
        """

    header_links = '<a href="/" class="text-xs bg-lime-800 hover:bg-lime-900 px-3 py-1.5 rounded-lg transition font-medium shadow-sm flex items-center">🏠 Retour</a>'

    contenu = f"""
    <div class="mb-8 text-center mt-4">
        <h2 class="text-3xl font-black text-stone-800 mb-2 tracking-tight">Le Podium</h2>
        <p class="text-stone-500 text-sm">Qui a le meilleur œil de la famille ?</p>
    </div>
    
    <div class="space-y-2">
        {html_lignes if html_lignes else '<p class="text-center text-stone-400">Aucun participant n\'est inscrit.</p>'}
    </div>
    """
    
    return layout_jeu("Classement - FaunaBingo", contenu, header_links)