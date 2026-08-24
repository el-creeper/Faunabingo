import sqlite3
import os
import re

DB_NAME = "database/bingo_faune.db"

def generer_id_stable(nom_scientifique):
    """Crée un ID unique et définitif basé sur le nom scientifique (ex: panthera-onca)"""
    if not nom_scientifique:
        return "espece-inconnue"
    # Transforme "Panthera onca" en "panthera-onca"
    return re.sub(r'[^a-z0-9]+', '-', nom_scientifique.lower()).strip('-')

def init_db():
    # Crée le dossier si nécessaire
    os.makedirs(os.path.dirname(DB_NAME), exist_ok=True)
    
    # On se connecte à la base de données (elle est créée automatiquement si elle n'existe pas)
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        # 1. CRÉATION DES TABLES (IF NOT EXISTS protège tes données existantes)
        cursor.executescript("""
        CREATE TABLE IF NOT EXISTS Participant (
            id_participant TEXT PRIMARY KEY,
            prenom TEXT NOT NULL,
            email_hash TEXT UNIQUE,
            mot_de_passe_hash TEXT,
            score_total INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS Espece (
            id_espece TEXT PRIMARY KEY,
            nom_courant TEXT NOT NULL,
            nom_scientifique TEXT,
            classe TEXT,
            famille TEXT,
            longevite_annees INTEGER,
            reproduction_jours INTEGER,
            taille_cm REAL,
            couleurs_principales TEXT,
            points_entendu INTEGER DEFAULT 5,
            points_vu INTEGER DEFAULT 10,
            points_photo INTEGER DEFAULT 20,
            image_reference TEXT
        );

        CREATE TABLE IF NOT EXISTS Observation (
            id_observation TEXT PRIMARY KEY,
            id_participant TEXT,
            id_espece TEXT,
            type_preuve TEXT,
            UNIQUE(id_participant, id_espece)
        );
        
        
        CREATE TABLE IF NOT EXISTS Amitie (
            id_demandeur TEXT,
            id_receveur TEXT,
            statut TEXT DEFAULT 'EN_ATTENTE',
            PRIMARY KEY (id_demandeur, id_receveur),
            FOREIGN KEY (id_demandeur) REFERENCES Participant(id_participant),
            FOREIGN KEY (id_receveur) REFERENCES Participant(id_participant)
        );
        """)

        # 2. LISTE DES ESPÈCES AVEC IDs STABLES
        especes_costa_rica = [
            # --- MAMMIFÈRES TERRESTRES ---
            (generer_id_stable("Alouatta palliata"), "Singe hurleur à manteau", "Alouatta palliata", "Mammifères terrestres", "Atelidae", None, None, None, None, 2, 10, 20,"static/images/Singe_hurleur_a_manteau.png"),
            (generer_id_stable("Cebus capucinus"), "Singe capucin moine", "Cebus capucinus", "Mammifères terrestres", "Cebidae", None, None, None, None, 5, 10, 25, "static/images/Singe_capucin_moine.jpeg"),
            (generer_id_stable("Ateles geoffroyi"), "Singe-araignée de Geoffroy", "Ateles geoffroyi", "Mammifères terrestres", "Atelidae", None, None, None, None, 10, 20, 40, "static/images/Singe-araignee_de_Geoffroy.jpg"),
            (generer_id_stable("Saimiri oerstedii"), "Singe-écureuil à dos rouge", "Saimiri oerstedii", "Mammifères terrestres", "Cebidae", None, None, None, None, 10, 25, 50, "static/images/Singe-ecureuil_a_dos_rouge.jpeg"),
            (generer_id_stable("Bradypus variegatus"), "Paresseux à gorge brune", "Bradypus variegatus", "Mammifères terrestres", "Bradypodidae", None, None, None, None, 0, 20, 40, "static/images/Paresseux_a_gorge_brune.jpg"),
            (generer_id_stable("Choloepus hoffmanni"), "Paresseux d'Hoffmann", "Choloepus hoffmanni", "Mammifères terrestres", "Choloepodidae", None, None, None, None, 0, 25, 50, "static/images/Paresseux_d'Hoffmann.jpg"),
            (generer_id_stable("Nasua narica"), "Coati à nez blanc", "Nasua narica", "Mammifères terrestres", "Procyonidae", None, None, None, None, 5, 10, 20, "static/images/Coati_a_nez blanc.jpeg"),
            (generer_id_stable("Procyon lotor"), "Raton laveur", "Procyon lotor", "Mammifères terrestres", "Procyonidae", None, None, None, None, 0, 10, 20, "static/images/Raton_laveur.jpg"),
            (generer_id_stable("Tapirus bairdii"), "Tapir de Baird", "Tapirus bairdii", "Mammifères terrestres", "Tapiridae", None, None, None, None, 10, 50, 150, "static/images/Tapir_de_Baird.jpg"),
            (generer_id_stable("Pecari tajacu"), "Pécari à collier", "Pecari tajacu", "Mammifères terrestres", "Tayassuidae", None, None, None, None, 10, 30, 60, "static/images/Pecar_a_collier.jpg"),
            (generer_id_stable("Dasyprocta punctata"), "Agouti ponctué", "Dasyprocta punctata", "Mammifères terrestres", "Dasyproctidae", None, None, None, None, 5, 15, 30, "static/images/Agouti_ponctue.jpg"),
            (generer_id_stable("Panthera onca"), "Jaguar", "Panthera onca", "Mammifères terrestres", "Felidae", None, None, None, None, 50, 200, 500, "static/images/Jaguar.jpg"),
            (generer_id_stable("Puma concolor"), "Puma", "Puma concolor", "Mammifères terrestres", "Felidae", None, None, None, None, 40, 150, 400, "static/images/Puma.jpg"),
            (generer_id_stable("Leopardus pardalis"), "Ocelot", "Leopardus pardalis", "Mammifères terrestres", "Felidae", None, None, None, None, 20, 100, 250, "static/images/Ocelot.jpeg"),
            (generer_id_stable("Leopardus wiedii"), "Margay", "Leopardus wiedii", "Mammifères terrestres", "Felidae", None, None, None, None, 20, 120, 300, "static/images/Margay.webp"),
            (generer_id_stable("Potos flavus"), "Kinkajou", "Potos flavus", "Mammifères terrestres", "Procyonidae", None, None, None, None, 15, 40, 80, "static/images/Kinkajou.jpg"),
            (generer_id_stable("Tamandua mexicana"), "Tamandua du Nord", "Tamandua mexicana", "Mammifères terrestres", "Myrmecophagidae", None, None, None, None, 0, 40, 90, "static/images/Tamandua_du_Nord.jpg"),
            (generer_id_stable("Eira barbara"), "Tayra (Tolomuco)", "Eira barbara", "Mammifères terrestres", "Mustelidae", None, None, None, None, 5, 50, 100, "static/images/Tayra_(Tolomuco).webp"),
            (generer_id_stable("Dasypus novemcinctus"), "Tatou à neuf bandes", "Dasypus novemcinctus", "Mammifères terrestres", "Dasypodidae", None, None, None, None, 10, 30, 70, "static/images/Tatou_a_neuf_bandes.jpg"),
            (generer_id_stable("Ectophylla alba"), "Chauve-souris blanche", "Ectophylla alba", "Mammifères terrestres", "Phyllostomidae", None, None, None, None, 0, 60, 120, "static/images/Chauve-souris_blanche.jpg"),
            
            # --- OISEAUX ---
            (generer_id_stable("Ramphastos sulfuratus"), "Toucan à carène", "Ramphastos sulfuratus", "Oiseaux - Toucans & Aras", "Ramphastidae", None, None, None, None, 15, 20, 50, "static/images/Toucan_a_carene.jpg"),
            (generer_id_stable("Ramphastos ambiguus"), "Toucan de Swainson", "Ramphastos ambiguus", "Oiseaux - Toucans & Aras", "Ramphastidae", None, None, None, None, 15, 20, 50, "static/images/Toucan_de_Swainson.jpg"),
            (generer_id_stable("Ara macao"), "Ara macao", "Ara macao", "Oiseaux - Toucans & Aras", "Psittacidae", None, None, None, None, 10, 20, 45, "static/images/Ara_macao.jpg"),
            (generer_id_stable("Ara ambiguus"), "Ara de Buffon", "Ara ambiguus", "Oiseaux - Toucans & Aras", "Psittacidae", None, None, None, None, 15, 40, 80, "static/images/Ara_de_Buffon.jpg"),
            (generer_id_stable("Pharomachrus mocinno"), "Quetzal resplendissant", "Pharomachrus mocinno", "Oiseaux - Trogons & Colibris", "Trogonidae", None, None, None, None, 20, 50, 150, "static/images/Quetzal_resplendissant.jpg"),
            (generer_id_stable("Colibri thalassinus"), "Colibri thalassin", "Colibri thalassinus", "Oiseaux - Trogons & Colibris", "Trochilidae", None, None, None, None, 5, 15, 60, "static/images/Colibri_thalassin.jpg"),
            (generer_id_stable("Trogon massena"), "Trogon masséna", "Trogon massena", "Oiseaux - Trogons & Colibris", "Trogonidae", None, None, None, None, 15, 30, 70, "static/images/Trogon_massena.webp"),
            (generer_id_stable("Eumomota superciliosa"), "Motmot à sourcils bleus", "Eumomota superciliosa", "Oiseaux - Coraciiformes", "Momotidae", None, None, None, None, 10, 25, 60, "static/images/Motmot_a_sourcils_bleus.jpg"),
            (generer_id_stable("Chloroceryle americana"), "Martin-pêcheur vert", "Chloroceryle americana", "Oiseaux - Coraciiformes", "Alcedinidae", None, None, None, None, 5, 20, 50, "static/images/Martin-pecheur_vert.jpg"),
            (generer_id_stable("Chloroceryle amazona"), "Martin-pêcheur d'Amazonie", "Chloroceryle amazona", "Oiseaux - Coraciiformes", "Alcedinidae", None, None, None, None, 5, 20, 50, "static/images/Chloroceryle_amazona.jpg"),
            (generer_id_stable("Crax rubra"), "Grand Hocco", "Crax rubra", "Oiseaux - Galliformes", "Cracidae", None, None, None, None, 20, 35, 80, "static/images/Grand_Hocco.jpg"),
            (generer_id_stable("Coragyps atratus"), "Urubu noir", "Coragyps atratus", "Oiseaux - Rapaces", "Cathartidae", None, None, None, None, 0, 5, 10, "static/images/Urubu_noir.jpg"),
            (generer_id_stable("Cathartes aura"), "Urubu à tête rouge", "Cathartes aura", "Oiseaux - Rapaces", "Cathartidae", None, None, None, None, 0, 5, 10, "static/images/Urubu_a_tete_rouge.jpg"),
            (generer_id_stable("Pandion haliaetus"), "Balbuzard pêcheur", "Pandion haliaetus", "Oiseaux - Rapaces", "Pandionidae", None, None, None, None, 10, 20, 45, "static/images/Balbuzard_pecheur.jpg"),
            (generer_id_stable("Milvago chimachima"), "Caracara à tête jaune", "Milvago chimachima", "Oiseaux - Rapaces", "Falconidae", None, None, None, None, 10, 20, 45, "static/images/Caracara_a_tete_jaune.jpg"),
            (generer_id_stable("Fregata magnificens"), "Frégate superbe", "Fregata magnificens", "Oiseaux - Marins", "Fregatidae", None, None, None, None, 0, 10, 25, "static/images/Fregate_superbe.jpg"),
            (generer_id_stable("Pelecanus occidentalis"), "Pélican brun", "Pelecanus occidentalis", "Oiseaux - Marins", "Pelecanidae", None, None, None, None, 0, 5, 15, "static/images/Pelican_brun.webp"),
            (generer_id_stable("Tigrisoma mexicanum"), "Héron tigre", "Tigrisoma mexicanum", "Oiseaux - Échassiers", "Ardeidae", None, None, None, None, 10, 25, 50, "static/images/Heron_tigre.jpg"),
            (generer_id_stable("Egretta thula"), "Aigrette neigeuse", "Egretta thula", "Oiseaux - Échassiers", "Ardeidae", None, None, None, None, 0, 10, 25, "static/images/Aigrette_neigeuse.jpg"),
            (generer_id_stable("Jacana jacana"), "Jacana noir", "Jacana jacana", "Oiseaux - Échassiers", "Jacanidae", None, None, None, None, 5, 15, 35, "static/images/Jacana_noir.jpg"),
            (generer_id_stable("Thraupis episcopus"), "Tangara évêque", "Thraupis episcopus", "Oiseaux - Passereaux", "Thraupidae", None, None, None, None, 5, 10, 30, "static/images/Tangara_eveque.jpg"),
            (generer_id_stable("Psarocolius montezuma"), "Cassique de Montezuma", "Psarocolius montezuma", "Oiseaux - Passereaux", "Icteridae", None, None, None, None, 10, 15, 40, "static/images/Cassique_de_Montezuma.jpg"),
            (generer_id_stable("Manacus candei"), "Manakin à col blanc", "Manacus candei", "Oiseaux - Passereaux", "Pipridae", None, None, None, None, 15, 40, 100, "static/images/Manakin_a_col_blanc.jpg"),
            (generer_id_stable("Aulacorhynchus prasinus"), "Toucanet émeraude", "Aulacorhynchus prasinus", "Oiseaux - Toucans & Aras", "Ramphastidae", None, None, None, None, 15, 30, 70, "static/images/Toucanet_emeraude.jpg"),
            (generer_id_stable("Piaya cayana"), "Piaye écureuil", "Piaya cayana", "Oiseaux - Autres", "Cuculidae", None, None, None, None, 10, 20, 50, "static/images/Piaye_ecureuil.jpg"),

            # --- REPTILES ---
            (generer_id_stable("Crocodylus acutus"), "Crocodile américain", "Crocodylus acutus", "Reptiles - Crocodiliens", "Crocodylidae", None, None, None, None, 0, 20, 40, "static/images/Crocodylus_acutus.jpg"),
            (generer_id_stable("Caiman crocodilus"), "Caïman à lunettes", "Caiman crocodilus", "Reptiles - Crocodiliens", "Alligatoridae", None, None, None, None, 0, 15, 30, "static/images/Caiman_a_lunettes.jpg"),
            (generer_id_stable("Iguana iguana"), "Iguane vert", "Iguana iguana", "Reptiles - Sauriens", "Iguanidae", None, None, None, None, 0, 10, 25, "static/images/Iguane_vert.webp"),
            (generer_id_stable("Ctenosaura similis"), "Iguane noir (Garrobo)", "Ctenosaura similis", "Reptiles - Sauriens", "Iguanidae", None, None, None, None, 0, 10, 25, "static/images/Iguane_noir_(Garrobo).jpg"),
            (generer_id_stable("Basiliscus plumifrons"), "Basilic vert", "Basiliscus plumifrons", "Reptiles - Sauriens", "Corytophanidae", None, None, None, None, 0, 20, 60, "static/images/Basilic_vert.webp"),
            (generer_id_stable("Basiliscus vittatus"), "Basilic brun", "Basiliscus vittatus", "Reptiles - Sauriens", "Corytophanidae", None, None, None, None, 0, 15, 40, "static/images/Basilic_brun.jpg"),
            (generer_id_stable("Corytophanes cristatus"), "Iguane casqué", "Corytophanes cristatus", "Reptiles - Sauriens", "Corytophanidae", None, None, None, None, 0, 30, 70, "static/images/Gecko_casque.jpg"),
            (generer_id_stable("Boa constrictor"), "Boa constricteur", "Boa constrictor", "Reptiles - Serpents", "Boidae", None, None, None, None, 0, 40, 100, "static/images/Boa_constricteur.jpg"),
            (generer_id_stable("Bothrops asper"), "Fer de lance (Terciopelo)", "Bothrops asper", "Reptiles - Serpents", "Viperidae", None, None, None, None, 0, 60, 150, "static/images/Bothrops_asper.jpg"),
            (generer_id_stable("Bothriechis schlegelii"), "Vipère de Schlegel", "Bothriechis schlegelii", "Reptiles - Serpents", "Viperidae", None, None, None, None, 0, 70, 180, "static/images/Vipere_de_Schlegel.jpg"),
            (generer_id_stable("Lampropeltis triangulum"), "Faux serpent corail", "Lampropeltis triangulum", "Reptiles - Serpents", "Colubridae", None, None, None, None, 0, 50, 120, "static/images/Faux_serpent_corail.png"),
            (generer_id_stable("Oxybelis aeneus"), "Serpent liane", "Oxybelis aeneus", "Reptiles - Serpents", "Colubridae", None, None, None, None, 0, 40, 90, "static/images/Serpent_liane.jpeg"),
            (generer_id_stable("Chelonia mydas"), "Tortue verte", "Chelonia mydas", "Reptiles - Tortues", "Cheloniidae", None, None, None, None, 0, 50, 100, "static/images/Tortue_verte.jpg"),
            (generer_id_stable("Dermochelys coriacea"), "Tortue luth", "Dermochelys coriacea", "Reptiles - Tortues", "Dermochelyidae", None, None, None, None, 0, 80, 200, "static/images/Tortue_luth.jpg"),
            (generer_id_stable("Eretmochelys imbricata"), "Tortue imbriquée", "Eretmochelys imbricata", "Reptiles - Tortues", "Cheloniidae", None, None, None, None, 0, 70, 180, "static/images/Tortue_imbriquee.jpg"),

            # --- AMPHIBIENS ---
            (generer_id_stable("Oophaga pumilio"), "Dendrobate fraise", "Oophaga pumilio", "Amphibiens - Anoures", "Dendrobatidae", None, None, None, None, 10, 25, 60, "static/images/Dendrobate fraise.webp"),
            (generer_id_stable("Dendrobates auratus"), "Dendrobate doré", "Dendrobates auratus", "Amphibiens - Anoures", "Dendrobatidae", None, None, None, None, 10, 30, 70, "static/images/Dendrobate_dore.jpg"),
            (generer_id_stable("Agalychnis callidryas"), "Rainette aux yeux rouges", "Agalychnis callidryas", "Amphibiens - Anoures", "Phyllomedusidae", None, None, None, None, 15, 40, 100, "static/images/Rainette_aux_yeux_rouges.webp"),
            (generer_id_stable("Hyalinobatrachium spp."), "Rainette de verre", "Hyalinobatrachium spp.", "Amphibiens - Anoures", "Centrolenidae", None, None, None, None, 20, 50, 120, "static/images/Rainette_de_verre.jpg"),
            (generer_id_stable("Rhinella marina"), "Crapaud géant", "Rhinella marina", "Amphibiens - Anoures", "Bufonidae", None, None, None, None, 5, 10, 20, "static/images/Crapaud_geant.jpg"),
            (generer_id_stable("Phyllobates lugubris"), "Phyllobate lugubre", "Phyllobates lugubris", "Amphibiens - Anoures", "Dendrobatidae", None, None, None, None, 10, 35, 80, "static/images/Phyllobate_lugubre.jpeg"),
            (generer_id_stable("Smilisca phaeota"), "Grenouille masquée", "Smilisca phaeota", "Amphibiens - Anoures", "Hylidae", None, None, None, None, 10, 20, 50, "static/images/Grenouille_masquee.jpeg"),
            (generer_id_stable("Craugastor spp."), "Grenouille de litière", "Craugastor spp.", "Amphibiens - Anoures", "Craugastoridae", None, None, None, None, 5, 15, 35, "static/images/Grenouille_de_litiere.jpg"),
            (generer_id_stable("Bolitoglossa spp."), "Salamandre tropicale", "Bolitoglossa spp.", "Amphibiens - Urodèles", "Plethodontidae", None, None, None, None, 0, 60, 150, "static/images/Salamandre_tropicale.jpg"),
            (generer_id_stable("Gymnophiona"), "Cécilie", "Gymnophiona", "Amphibiens - Gymnophiones", "Caeciliidae", None, None, None, None, 0, 100, 300, "static/images/Cécilie.jpg"),

            # --- MARINS ET AQUATIQUES ---
            (generer_id_stable("Megaptera novaeangliae"), "Baleine à bosse", "Megaptera novaeangliae", "Mammifères marins", "Balaenopteridae", None, None, None, None, 20, 60, 150, "static/images/Baleine_a_bosse.jpg"),
            (generer_id_stable("Tursiops truncatus"), "Grand dauphin", "Tursiops truncatus", "Mammifères marins", "Delphinidae", None, None, None, None, 10, 30, 80, "static/images/Grand_dauphin.jpg"),
            (generer_id_stable("Stenella attenuata"), "Dauphin tacheté pantropical", "Stenella attenuata", "Mammifères marins", "Delphinidae", None, None, None, None, 10, 30, 80, "static/images/Dauphin_tachete_pantropical.png"),
            (generer_id_stable("Orcinus orca"), "Orque", "Orcinus orca", "Mammifères marins", "Delphinidae", None, None, None, None, 50, 200, 500, "static/images/Orque.jpeg"),
            (generer_id_stable("Trichechus manatus"), "Lamantin des Caraïbes", "Trichechus manatus", "Mammifères marins", "Trichechidae", None, None, None, None, 0, 100, 250, "static/images/Lamantin_des_Caraibes.jpg"),
            (generer_id_stable("Carcharhinus leucas"), "Requin-bouledogue", "Carcharhinus leucas", "Poissons - Cartilagineux", "Carcharhinidae", None, None, None, None, 0, 50, 150, "static/images/Requin-bouledogue.jpeg"),
            (generer_id_stable("Triaenodon obesus"), "Requin à pointes blanches", "Triaenodon obesus", "Poissons - Cartilagineux", "Carcharhinidae", None, None, None, None, 0, 40, 100, "static/images/Requin_a_pointes_blanches.webp"),
            (generer_id_stable("Manta birostris"), "Raie manta", "Manta birostris", "Poissons - Cartilagineux", "Mobulidae", None, None, None, None, 0, 50, 120, "static/images/Raie_manta.webp"),
            (generer_id_stable("Pomacanthus paru"), "Poisson-ange français", "Pomacanthus paru", "Poissons - Osseux", "Pomacanthidae", None, None, None, None, 0, 15, 40, "static/images/Poisson-ange_francais.jpeg"),
            (generer_id_stable("Scaridae spp."), "Poisson-perroquet", "Scaridae spp.", "Poissons - Osseux", "Scaridae", None, None, None, None, 0, 10, 30, "static/images/Poisson-perroquet.jpg"),

            # --- INSECTES ET ARACHNIDES ---
            (generer_id_stable("Morpho peleides"), "Morpho bleu", "Morpho peleides", "Insectes - Lépidoptères", "Nymphalidae", None, None, None, None, 0, 5, 40, "static/images/Morpho_bleu.jpeg"),
            (generer_id_stable("Caligo eurilochus"), "Papillon chouette", "Caligo eurilochus", "Insectes - Lépidoptères", "Nymphalidae", None, None, None, None, 0, 10, 30, "static/images/Papillon_chouette.jpeg"),
            (generer_id_stable("Heliconius melpomene"), "Papillon Heliconius", "Heliconius melpomene", "Insectes - Lépidoptères", "Nymphalidae", None, None, None, None, 0, 10, 25, "static/images/Papillon_Heliconius.jpeg"),
            (generer_id_stable("Atta cephalotes"), "Fourmi coupe-feuille", "Atta cephalotes", "Insectes - Hyménoptères", "Formicidae", None, None, None, None, 0, 5, 15, "static/images/Fourmi_coupe-feuille.jpg"),
            (generer_id_stable("Paraponera clavata"), "Fourmi balle de fusil", "Paraponera clavata", "Insectes - Hyménoptères", "Paraponeridae", None, None, None, None, 0, 20, 50, "static/images/Fourmi_balle_de_fusil.jpg"),
            (generer_id_stable("Meliponini"), "Abeille sans dard", "Meliponini", "Insectes - Hyménoptères", "Apidae", None, None, None, None, 5, 10, 30, "static/images/Abeille_sans_dard.jpg"),
            (generer_id_stable("Dynastes hercules"), "Scarabée rhinocéros", "Dynastes hercules", "Insectes - Coléoptères", "Scarabaeidae", None, None, None, None, 0, 40, 90, "static/images/Scarabee_rhinoceros.jpeg"),
            (generer_id_stable("Phasmatodea"), "Phasme", "Phasmatodea", "Insectes - Autres", "Phasmatidae", None, None, None, None, 0, 30, 70, "static/images/Phasme.jpeg"),
            (generer_id_stable("Aphonopelma seemanni"), "Mygale à genoux rouges", "Aphonopelma seemanni", "Arachnides", "Theraphosidae", None, None, None, None, 0, 30, 80, "static/images/Mygale_a_genoux_rouges.jpg"),
            (generer_id_stable("Trichonephila clavipes"), "Araignée Néphile dorée", "Trichonephila clavipes", "Arachnides", "Araneidae", None, None, None, None, 0, 15, 40, "static/images/Araignee_Nephile_doree.jpeg"),

            # --- PLANTES ---
            (generer_id_stable("Ficus aurea"), "Figuier étrangleur", "Ficus aurea", "Plantes - Arbres & Palmiers", "Moraceae", None, None, None, None, 0, 5, 15, "static/images/Figuier_etrangleur.webp"),
            (generer_id_stable("Ceiba pentandra"), "Ceiba (Fromager géant)", "Ceiba pentandra", "Plantes - Arbres & Palmiers", "Malvaceae", None, None, None, None, 0, 10, 20, "static/images/Ceiba_(Fromager_geant).jpg"),
            (generer_id_stable("Enterolobium cyclocarpum"), "Arbre de Guanacaste", "Enterolobium cyclocarpum", "Plantes - Arbres & Palmiers", "Fabaceae", None, None, None, None, 0, 10, 20, "static/images/Arbre_de_Guanacaste.jpg"),
            (generer_id_stable("Socratea exorrhiza"), "Palmier marcheur", "Socratea exorrhiza", "Plantes - Arbres & Palmiers", "Arecaceae", None, None, None, None, 0, 15, 30, "static/images/Palmier_marcheur.jpeg"),
            (generer_id_stable("Artocarpus altilis"), "Arbre à pain", "Artocarpus altilis", "Plantes - Arbres & Palmiers", "Moraceae", None, None, None, None, 0, 10, 20, "static/images/Arbre_a_pain.jpeg"),
            (generer_id_stable("Theobroma cacao"), "Cacaoyer (avec cabosses)", "Theobroma cacao", "Plantes - Arbres & Palmiers", "Malvaceae", None, None, None, None, 0, 10, 20, "static/images/Cacaoyer_(avec_cabosses).jpeg"),
            (generer_id_stable("Heliconia rostrata"), "Fleur Héliconia rostrata", "Heliconia rostrata", "Plantes - Fleurs & Herbacées", "Heliconiaceae", None, None, None, None, 0, 5, 15, "static/images/Fleur_Heliconia_rostrata.jpg"),
            (generer_id_stable("Strelitzia reginae"), "Fleur Oiseau de paradis", "Strelitzia reginae", "Plantes - Fleurs & Herbacées", "Strelitziaceae", None, None, None, None, 0, 5, 15, "static/images/Fleur_Oiseau_de_paradis.jpg"),
            (generer_id_stable("Guarianthe skinneri"), "Orchidée Guaria Morada", "Guarianthe skinneri", "Plantes - Fleurs & Herbacées", "Orchidaceae", None, None, None, None, 0, 30, 60, "static/images/Orchidee _Guaria_Morada.jpg"),
            (generer_id_stable("Mimosa pudica"), "Mimosa pudica (sensitive)", "Mimosa pudica", "Plantes - Fleurs & Herbacées", "Fabaceae", None, None, None, None, 0, 15, 30, "static/images/Mimosa pudica.jpg")
        ]

        # La commande magique : INSERT OR IGNORE
        # Elle insère les nouvelles espèces, mais ne touche PAS à celles qui existent déjà !
        cursor.executemany("""
            INSERT OR IGNORE INTO Espece (id_espece, nom_courant, nom_scientifique, classe, famille, 
                                longevite_annees, reproduction_jours, taille_cm, couleurs_principales, points_entendu, points_vu, points_photo, image_reference)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, especes_costa_rica)
        
        conn.commit()
        print("✅ Base de données initialisée/mise à jour avec succès (Utilisateurs et Observations préservés).")

if __name__ == "__main__":
    init_db()