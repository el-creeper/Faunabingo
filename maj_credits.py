import pandas as pd
import json

def generer_json():
    fichier_excel = "database/sources_image.xlsx"
    fichier_json = "database/credits.json"
    
    print(f"Lecture du fichier {fichier_excel}...")
    try:
        # Lecture de l'Excel
        df = pd.read_excel(fichier_excel)
        
        # Remplacer les cases vides (NaN) par "Auteur inconnu" ou "Lien inconnu"
        df.fillna("Inconnu", inplace=True)
        
        credits_list = []
        for index, row in df.iterrows():
            # On nettoie le nom : on remplace les _ par des espaces et on met une majuscule
            nom_propre = str(row['Nom image']).replace('_', ' ').capitalize()
            
            credits_list.append({
                "nom": nom_propre,
                "auteur": str(row['Auteur']),
                "licence": str(row['Licence']),
                "source": str(row['Source'])
            })
            
        # Écriture dans le fichier JSON
        with open(fichier_json, 'w', encoding='utf-8') as f:
            json.dump(credits_list, f, indent=4, ensure_ascii=False)
            
        print(f"Succès ! {len(credits_list)} animaux ont été exportés dans {fichier_json}.")
        
    except Exception as e:
        print(f"Une erreur est survenue : {e}")

if __name__ == "__main__":
    generer_json()