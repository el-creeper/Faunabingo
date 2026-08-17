# 🌴 FaunaBingo 

FaunaBingo est une application web mobile-first développée pour pimenter un voyage en famille au Costa Rica. Il s'agit d'un carnet de bord interactif sous forme de jeu, où chaque participant accumule des points en observant la faune locale.

L'application a été conçue pour être ultra-légère, rapide sur smartphone, et capable de tourner 24h/24 pour saisir une observation d'animal à n'importe quel moment de la journée (ou de la nuit).

## 🎯 Le principe du jeu

Chaque joueur dispose de son propre carnet de bord avec une liste d'animaux. Les points sont attribués selon la difficulté et la qualité de l'observation :
- 🎧 **Entendu** : L'animal a été identifié au son.
- 👀 **Vu** : L'animal a été observé visuellement.
- 📸 **Photo** : L'animal a été immortalisé (parfait pour rentabiliser le Fujifilm X-M5 !).

*Si une observation est améliorée (ex: on entend un singe, puis on arrive à le prendre en photo), le score s'ajuste automatiquement.*

## 🛠️ Technologies utilisées

- **Backend** : Python 3, FastAPI, Uvicorn
- **Base de données** : SQLite3 (légère et portable, parfaite pour ce cas d'usage)
- **Frontend** : HTML5, JavaScript vanilla, Tailwind CSS (via CDN)



## FUTUR UPDATE

1. Pouvoir appuyer sur les images
2. Avoir une meilleur classification des especes 
3. Avoir des missions quotidiennes pour marquer des points supplémentaires
4. Rajouter un système d'ami
4. Faire un tableau pour comparer les points entre amis