import sqlite3
import uuid
import os
import shutil
from fastapi import APIRouter, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse

router = APIRouter(prefix="/admin", tags=["Administration"])
DB_NAME = "database/bingo_faune.db"

def layout_html(titre: str, contenu: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{titre}</title>
        <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    </head>
    <body class="bg-slate-50 text-slate-800 font-sans min-h-screen pb-12">
        <nav class="bg-emerald-600 text-white shadow-md mb-6">
            <div class="max-w-4xl mx-auto px-4 py-3 flex justify-between items-center">
                <h1 class="text-xl font-bold">FaunaBingo - Admin</h1>
                <a href="/admin" class="text-sm bg-emerald-700 hover:bg-emerald-800 px-3 py-1.5 rounded-lg transition">Liste Espèces</a>
            </div>
        </nav>
        <main class="max-w-4xl mx-auto px-4">
            {contenu}
        </main>
    </body>
    </html>
    """

@router.get("/", response_class=HTMLResponse)
def admin_liste():
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Espece ORDER BY nom_courant")
        especes = cursor.fetchall()
    
    rows = ""
    for esp in especes:
        img_html = f'<img src="/{esp["image_reference"]}" class="w-12 h-12 object-cover rounded-lg shadow-sm border border-slate-200">' if esp['image_reference'] else '<div class="w-12 h-12 bg-slate-200 rounded-lg flex items-center justify-center text-[10px] text-slate-500 text-center leading-tight">Pas de photo</div>'
        
        rows += f"""
        <tr class="border-b border-slate-200 hover:bg-slate-100 transition">
            <td class="p-3">{img_html}</td>
            <td class="p-3 font-semibold text-emerald-700">{esp['nom_courant']}</td>
            <td class="p-3 text-sm">{esp['classe'] or ''}</td>
            <td class="p-3 text-center text-sm"><span class="font-bold text-indigo-600">{esp['points_entendu']}</span> / <span class="font-bold text-amber-600">{esp['points_vu']}</span> / <span class="font-bold text-emerald-600">{esp['points_photo']}</span></td>
            <td class="p-3 text-center">
                <a href="/admin/modifier/{esp['id_espece']}" class="text-indigo-600 hover:text-indigo-900 text-sm font-medium">Modifier</a>
            </td>
        </tr>
        """

    contenu = f"""
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="bg-white p-6 rounded-xl shadow-sm border border-slate-200 md:col-span-1 h-fit">
            <h2 class="text-lg font-bold text-slate-900 mb-4">Ajouter une espèce</h2>
            <form action="/admin/ajouter" method="POST" enctype="multipart/form-data" class="space-y-3">
                
                <div class="mb-4 bg-slate-50 p-3 rounded-lg border border-slate-200 border-dashed">
                    <label class="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-2">📸 Photo de référence</label>
                    <input type="file" name="image_reference" accept="image/*" class="w-full text-xs text-slate-500 file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100">
                </div>

                <div><label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Nom courant</label><input type="text" name="nom_courant" required class="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"></div>
                <div><label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Nom scientifique</label><input type="text" name="nom_scientifique" class="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"></div>
                <div class="grid grid-cols-2 gap-2">
                    <div><label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Classe</label><input type="text" name="classe" class="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"></div>
                    <div><label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Famille</label><input type="text" name="famille" class="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"></div>
                </div>
                
                <div class="grid grid-cols-3 gap-2 border-t border-slate-100 pt-2 mt-2">
                    <div><label class="block text-[10px] font-semibold text-indigo-600 uppercase tracking-wider mb-1">Pts Son</label><input type="number" name="points_entendu" value="5" class="w-full px-2 py-2 border border-slate-300 rounded-lg text-sm focus:outline-indigo-500"></div>
                    <div><label class="block text-[10px] font-semibold text-amber-600 uppercase tracking-wider mb-1">Pts Vu</label><input type="number" name="points_vu" value="10" class="w-full px-2 py-2 border border-slate-300 rounded-lg text-sm focus:outline-amber-500"></div>
                    <div><label class="block text-[10px] font-semibold text-emerald-600 uppercase tracking-wider mb-1">Pts Photo</label><input type="number" name="points_photo" value="20" class="w-full px-2 py-2 border border-slate-300 rounded-lg text-sm focus:outline-emerald-500"></div>
                </div>
                <button type="submit" class="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-medium py-2 rounded-lg transition text-sm shadow-sm mt-4">Enregistrer l'espèce</button>
            </form>
        </div>
        <div class="bg-white p-6 rounded-xl shadow-sm border border-slate-200 md:col-span-2 overflow-x-auto">
            <h2 class="text-lg font-bold text-slate-900 mb-4">Espèces enregistrées ({len(especes)})</h2>
            <table class="w-full text-left border-collapse">
                <thead>
                    <tr class="border-b-2 border-slate-200 text-slate-400 text-xs font-semibold uppercase">
                        <th class="p-3">Photo</th><th class="p-3">Nom</th><th class="p-3">Classe</th><th class="p-3 text-center">Pts (Son/Vu/Photo)</th><th class="p-3 text-center">Action</th>
                    </tr>
                </thead>
                <tbody>{rows if rows else '<tr><td colspan="5" class="p-4 text-center text-slate-400">Aucune espèce.</td></tr>'}</tbody>
            </table>
        </div>
    </div>
    """
    return layout_html("Gestion des Espèces", contenu)

@router.post("/ajouter")
def admin_ajouter(
    nom_courant: str = Form(...), nom_scientifique: str = Form(None),
    classe: str = Form(None), famille: str = Form(None),
    points_entendu: int = Form(5), points_vu: int = Form(10), points_photo: int = Form(20),
    image_reference: UploadFile = File(None)
):
    chemin_image_db = None
    if image_reference and image_reference.filename:
        nom_fichier = f"{uuid.uuid4()}_{image_reference.filename.replace(' ', '_')}"
        chemin_physique = f"static/images/{nom_fichier}"
        
        with open(chemin_physique, "wb") as buffer:
            shutil.copyfileobj(image_reference.file, buffer)
        
        chemin_image_db = chemin_physique

    id_nouveau = str(uuid.uuid4())
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Espece (id_espece, nom_courant, nom_scientifique, classe, famille, points_entendu, points_vu, points_photo, image_reference)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (id_nouveau, nom_courant, nom_scientifique, classe, famille, points_entendu, points_vu, points_photo, chemin_image_db))
        conn.commit()
    return RedirectResponse(url="/admin", status_code=303)

@router.get("/modifier/{id_espece}", response_class=HTMLResponse)
def admin_form_modifier(id_espece: str):
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Espece WHERE id_espece = ?", (id_espece,))
        esp = cursor.fetchone()
    
    if not esp:
        return RedirectResponse(url="/admin")

    img_actuelle = f'<div class="mb-4 text-center"><img src="/{esp["image_reference"]}" class="w-32 h-32 object-cover rounded-xl mx-auto shadow-sm border border-slate-200"></div>' if esp['image_reference'] else ''

    contenu = f"""
    <div class="max-w-md mx-auto bg-white p-6 rounded-xl shadow-sm border border-slate-200">
        <h2 class="text-lg font-bold text-slate-900 mb-4 text-center">Modifier : {esp['nom_courant']}</h2>
        {img_actuelle}
        <form action="/admin/modifier/{id_espece}" method="POST" enctype="multipart/form-data" class="space-y-4">
            
            <div class="bg-slate-50 p-3 rounded-lg border border-slate-200 border-dashed">
                <label class="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-2">📸 Changer la photo</label>
                <input type="file" name="image_reference" accept="image/*" class="w-full text-xs text-slate-500 file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100">
            </div>

            <div><label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Nom courant</label><input type="text" name="nom_courant" value="{esp['nom_courant']}" required class="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"></div>
            <div><label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Nom scientifique</label><input type="text" name="nom_scientifique" value="{esp['nom_scientifique'] or ''}" class="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"></div>
            
            <div class="grid grid-cols-3 gap-2 border-t border-slate-100 pt-2 mt-2">
                <div><label class="block text-[10px] font-semibold text-indigo-600 uppercase tracking-wider mb-1">Points Son</label><input type="number" name="points_entendu" value="{esp['points_entendu']}" class="w-full px-2 py-2 border border-slate-300 rounded-lg text-sm focus:outline-indigo-500"></div>
                <div><label class="block text-[10px] font-semibold text-amber-600 uppercase tracking-wider mb-1">Points Vu</label><input type="number" name="points_vu" value="{esp['points_vu']}" class="w-full px-2 py-2 border border-slate-300 rounded-lg text-sm focus:outline-amber-500"></div>
                <div><label class="block text-[10px] font-semibold text-emerald-600 uppercase tracking-wider mb-1">Points Photo</label><input type="number" name="points_photo" value="{esp['points_photo']}" class="w-full px-2 py-2 border border-slate-300 rounded-lg text-sm focus:outline-emerald-500"></div>
            </div>
            
            <div class="flex space-x-2 pt-4">
                <a href="/admin" class="w-1/2 bg-slate-200 hover:bg-slate-300 text-slate-700 text-center font-medium py-2 rounded-lg transition text-sm">Annuler</a>
                <button type="submit" class="w-1/2 bg-emerald-600 hover:bg-emerald-700 text-white font-medium py-2 rounded-lg transition text-sm shadow-sm">Mettre à jour</button>
            </div>
        </form>
    </div>
    """
    return layout_html("Modifier une espèce", contenu)

@router.post("/modifier/{id_espece}")
def admin_modifier(
    id_espece: str,
    nom_courant: str = Form(...), nom_scientifique: str = Form(None),
    points_entendu: int = Form(...), points_vu: int = Form(...), points_photo: int = Form(...),
    image_reference: UploadFile = File(None)
):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        
        if image_reference and image_reference.filename:
            nom_fichier = f"{uuid.uuid4()}_{image_reference.filename.replace(' ', '_')}"
            chemin_physique = f"static/images/{nom_fichier}"
            with open(chemin_physique, "wb") as buffer:
                shutil.copyfileobj(image_reference.file, buffer)
            
            cursor.execute("""
                UPDATE Espece 
                SET nom_courant=?, nom_scientifique=?, points_entendu=?, points_vu=?, points_photo=?, image_reference=?
                WHERE id_espece=?
            """, (nom_courant, nom_scientifique, points_entendu, points_vu, points_photo, chemin_physique, id_espece))
        else:
            cursor.execute("""
                UPDATE Espece 
                SET nom_courant=?, nom_scientifique=?, points_entendu=?, points_vu=?, points_photo=?
                WHERE id_espece=?
            """, (nom_courant, nom_scientifique, points_entendu, points_vu, points_photo, id_espece))
            
        conn.commit()
    return RedirectResponse(url="/admin", status_code=303)