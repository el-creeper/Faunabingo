import sqlite3
import uuid
import os

os.makedirs("database", exist_ok=True)
os.makedirs("static/images", exist_ok=True)
DB_NAME = "database/bingo_faune.db"

def initialiser_bdd():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        
        cursor.executescript("""
        CREATE TABLE IF NOT EXISTS Espece (
            id_espece TEXT PRIMARY KEY,
            nom_courant TEXT NOT NULL,
            nom_scientifique TEXT,
            classe TEXT,   
            famille TEXT,  
            longevite_annees INTEGER,
            reproduction_jours INTEGER, 
            taille_cm INTEGER, 
            couleurs_principales TEXT,
            points_entendu INTEGER DEFAULT 5, -- NOUVEAU
            points_vu INTEGER DEFAULT 10,
            points_photo INTEGER DEFAULT 20,
            image_reference TEXT
        );

        CREATE TABLE IF NOT EXISTS Participant (
            id_participant TEXT PRIMARY KEY,
            prenom TEXT NOT NULL,
            email_hash TEXT UNIQUE,
            mot_de_passe_hash TEXT,
            score_total INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS Observation (
            id_observation TEXT PRIMARY KEY,
            id_participant TEXT NOT NULL,
            id_espece TEXT NOT NULL,
            type_preuve TEXT CHECK(type_preuve IN ('ENTENDU', 'VU', 'PHOTO')) DEFAULT 'ENTENDU', -- NOUVEAU
            chemin_photo TEXT,
            sexe TEXT CHECK(sexe IN ('MALE', 'FEMELLE', 'INCONNU')) DEFAULT 'INCONNU',
            stade TEXT CHECK(stade IN ('ADULTE', 'JUVENILE', 'INCONNU')) DEFAULT 'ADULTE',
            remarques TEXT,
            date_heure DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_participant) REFERENCES Participant(id_participant),
            FOREIGN KEY (id_espece) REFERENCES Espece(id_espece)
        );
        """)
        
        cursor.execute("SELECT COUNT(*) FROM Espece")
        if cursor.fetchone()[0] == 0:
            especes_costa_rica = [
                # --- MAMMIFÈRES TERRESTRES ---
                # Format : (id, nom_courant, nom_scientifique, classe, famille, longevite, repro, taille, couleurs, pts_entendu, pts_vu, pts_photo, image)
                (str(uuid.uuid4()), "Singe hurleur à manteau", "Alouatta palliata", "Mammifère", "Atelidae", None, None, None, None, 2, 10, 20,"static/images/Singe_hurleur_a_manteau.png"),
                (str(uuid.uuid4()), "Singe capucin moine", "Cebus capucinus", "Mammifère", "Cebidae", None, None, None, None, 5, 10, 25, "static/images/Singe_capucin_moine.jpeg"),
                (str(uuid.uuid4()), "Singe-araignée de Geoffroy", "Ateles geoffroyi", "Mammifère", "Atelidae", None, None, None, None, 10, 20, 40, "static/images/Singe-araignee_de_Geoffroy.jpg"),
                (str(uuid.uuid4()), "Singe-écureuil à dos rouge", "Saimiri oerstedii", "Mammifère", "Cebidae", None, None, None, None, 10, 25, 50, "static/images/Singe-ecureuil_a_dos_rouge.jpeg"),
                (str(uuid.uuid4()), "Paresseux à gorge brune", "Bradypus variegatus", "Mammifère", "Bradypodidae", None, None, None, None, 0, 20, 40, "static/images/Paresseux_a_gorge_brune.jpg"),
                (str(uuid.uuid4()), "Paresseux d'Hoffmann", "Choloepus hoffmanni", "Mammifère", "Choloepodidae", None, None, None, None, 0, 25, 50, "static/images/Paresseux_d'Hoffmann.jpg"),
                (str(uuid.uuid4()), "Coati à nez blanc", "Nasua narica", "Mammifère", "Procyonidae", None, None, None, None, 5, 10, 20, "static/images/Coati_a_nez blanc.jpeg"),
                (str(uuid.uuid4()), "Raton laveur", "Procyon lotor", "Mammifère", "Procyonidae", None, None, None, None, 0, 10, 20, "static/images/Raton_laveur.jpg"),
                (str(uuid.uuid4()), "Tapir de Baird", "Tapirus bairdii", "Mammifère", "Tapiridae", None, None, None, None, 10, 50, 150, "static/images/Tapir_de_Baird.jpg"),
                (str(uuid.uuid4()), "Pécari à collier", "Pecari tajacu", "Mammifère", "Tayassuidae", None, None, None, None, 10, 30, 60, "static/images/Pecar_a_collier.jpg"),
                (str(uuid.uuid4()), "Agouti ponctué", "Dasyprocta punctata", "Mammifère", "Dasyproctidae", None, None, None, None, 5, 15, 30, "static/images/Agouti_ponctue.jpg"),
                (str(uuid.uuid4()), "Jaguar", "Panthera onca", "Mammifère", "Felidae", None, None, None, None, 50, 200, 500, "static/images/Jaguar.jpg"),
                (str(uuid.uuid4()), "Puma", "Puma concolor", "Mammifère", "Felidae", None, None, None, None, 40, 150, 400, "static/images/Puma.jpg"),
                (str(uuid.uuid4()), "Ocelot", "Leopardus pardalis", "Mammifère", "Felidae", None, None, None, None, 20, 100, 250, "static/images/Ocelot.jpeg"),
                (str(uuid.uuid4()), "Margay", "Leopardus wiedii", "Mammifère", "Felidae", None, None, None, None, 20, 120, 300, "static/images/Margay.webp"),
                (str(uuid.uuid4()), "Kinkajou", "Potos flavus", "Mammifère", "Procyonidae", None, None, None, None, 15, 40, 80, "static/images/Kinkajou.jpg"),
                (str(uuid.uuid4()), "Tamandua du Nord", "Tamandua mexicana", "Mammifère", "Myrmecophagidae", None, None, None, None, 0, 40, 90, "static/images/Tamandua_du_Nord.jpg"),
                (str(uuid.uuid4()), "Tayra (Tolomuco)", "Eira barbara", "Mammifère", "Mustelidae", None, None, None, None, 5, 50, 100, "static/images/Tayra_(Tolomuco).webp"),
                (str(uuid.uuid4()), "Tatou à neuf bandes", "Dasypus novemcinctus", "Mammifère", "Dasypodidae", None, None, None, None, 10, 30, 70, "static/images/Tatou_a_neuf_bandes.jpg"),
                (str(uuid.uuid4()), "Chauve-souris blanche", "Ectophylla alba", "Mammifère", "Phyllostomidae", None, None, None, None, 0, 60, 120, "static/images/Chauve-souris_blanche.jpg"),
                # --- OISEAUX ---
                (str(uuid.uuid4()), "Toucan à carène", "Ramphastos sulfuratus", "Oiseau", "Ramphastidae", None, None, None, None, 15, 20, 50, "static/images/Toucan_a_carene.jpg"),
                (str(uuid.uuid4()), "Toucan de Swainson", "Ramphastos ambiguus", "Oiseau", "Ramphastidae", None, None, None, None, 15, 20, 50, "static/images/Toucan_de_Swainson.jpg"),
                (str(uuid.uuid4()), "Ara macao", "Ara macao", "Oiseau", "Psittacidae", None, None, None, None, 10, 20, 45, "static/images/Ara_macao.jpg"),
                (str(uuid.uuid4()), "Ara de Buffon", "Ara ambiguus", "Oiseau", "Psittacidae", None, None, None, None, 15, 40, 80, "static/images/Ara_de_Buffon.jpg"),
                (str(uuid.uuid4()), "Quetzal resplendissant", "Pharomachrus mocinno", "Oiseau", "Trogonidae", None, None, None, None, 20, 50, 150, "static/images/Quetzal_resplendissant.jpg"),
                (str(uuid.uuid4()), "Colibri thalassin", "Colibri thalassinus", "Oiseau", "Trochilidae", None, None, None, None, 5, 15, 60, "static/images/Colibri_thalassin.jpg"),
                (str(uuid.uuid4()), "Motmot à sourcils bleus", "Eumomota superciliosa", "Oiseau", "Momotidae", None, None, None, None, 10, 25, 60, "static/images/Motmot_a_sourcils_bleus.jpg"),
                (str(uuid.uuid4()), "Grand Hocco", "Crax rubra", "Oiseau", "Cracidae", None, None, None, None, 20, 35, 80, "static/images/Grand_Hocco.jpg"),
                (str(uuid.uuid4()), "Urubu noir", "Coragyps atratus", "Oiseau", "Cathartidae", None, None, None, None, 0, 5, 10, "static/images/Urubu_noir.jpg"),
                (str(uuid.uuid4()), "Urubu à tête rouge", "Cathartes aura", "Oiseau", "Cathartidae", None, None, None, None, 0, 5, 10, "static/images/Urubu_a_tete_rouge.jpg"),
                (str(uuid.uuid4()), "Balbuzard pêcheur", "Pandion haliaetus", "Oiseau", "Pandionidae", None, None, None, None, 10, 20, 45, "static/images/Balbuzard_pecheur.jpg"),
                (str(uuid.uuid4()), "Frégate superbe", "Fregata magnificens", "Oiseau", "Fregatidae", None, None, None, None, 0, 10, 25, "static/images/Fregate_superbe.jpg"),
                (str(uuid.uuid4()), "Pélican brun", "Pelecanus occidentalis", "Oiseau", "Pelecanidae", None, None, None, None, 0, 5, 15, "static/images/Pelican_brun.webp"),
                (str(uuid.uuid4()), "Martin-pêcheur vert", "Chloroceryle americana", "Oiseau", "Alcedinidae", None, None, None, None, 5, 20, 50, "static/images/Martin-pecheur_vert.jpg"),
                (str(uuid.uuid4()), "Martin-pêcheur d'Amazonie", "Chloroceryle amazona", "Oiseau", "Alcedinidae", None, None, None, None, 5, 20, 50, "static/images/Chloroceryle_amazona.jpg"),
                (str(uuid.uuid4()), "Héron tigre", "Tigrisoma mexicanum", "Oiseau", "Ardeidae", None, None, None, None, 10, 25, 50, "static/images/Heron_tigre.jpg"),
                (str(uuid.uuid4()), "Aigrette neigeuse", "Egretta thula", "Oiseau", "Ardeidae", None, None, None, None, 0, 10, 25, "static/images/Aigrette_neigeuse.jpg"),
                (str(uuid.uuid4()), "Jacana noir", "Jacana jacana", "Oiseau", "Jacanidae", None, None, None, None, 5, 15, 35, "static/images/Jacana_noir.jpg"),
                (str(uuid.uuid4()), "Trogon masséna", "Trogon massena", "Oiseau", "Trogonidae", None, None, None, None, 15, 30, 70, "static/images/Trogon_massena.webp"),
                (str(uuid.uuid4()), "Tangara évêque", "Thraupis episcopus", "Oiseau", "Thraupidae", None, None, None, None, 5, 10, 30, "static/images/Tangara_eveque.jpg"),
                (str(uuid.uuid4()), "Cassique de Montezuma", "Psarocolius montezuma", "Oiseau", "Icteridae", None, None, None, None, 10, 15, 40, "static/images/Cassique_de_Montezuma.jpg"),
                (str(uuid.uuid4()), "Toucanet émeraude", "Aulacorhynchus prasinus", "Oiseau", "Ramphastidae", None, None, None, None, 15, 30, 70, "static/images/Toucanet_emeraude.jpg"),
                (str(uuid.uuid4()), "Piaye écureuil", "Piaya cayana", "Oiseau", "Cuculidae", None, None, None, None, 10, 20, 50, "static/images/Piaye_ecureuil.jpg"),
                (str(uuid.uuid4()), "Manakin à col blanc", "Manacus candei", "Oiseau", "Pipridae", None, None, None, None, 15, 40, 100, "static/images/Manakin_a_col_blanc.jpg"),
                (str(uuid.uuid4()), "Caracara à tête jaune", "Milvago chimachima", "Oiseau", "Falconidae", None, None, None, None, 10, 20, 45, "static/images/Caracara_a_tete_jaune.jpg"),

                # --- REPTILES ---
                (str(uuid.uuid4()), "Crocodile américain", "Crocodylus acutus", "Reptile", "Crocodylidae", None, None, None, None, 0, 20, 40, "static/images/Crocodylus_acutus.jpg"),
                (str(uuid.uuid4()), "Caïman à lunettes", "Caiman crocodilus", "Reptile", "Alligatoridae", None, None, None, None, 0, 15, 30, "static/images/Caiman_a_lunettes.jpg"),
                (str(uuid.uuid4()), "Iguane vert", "Iguana iguana", "Reptile", "Iguanidae", None, None, None, None, 0, 10, 25, "static/images/Iguane_vert.webp"),
                (str(uuid.uuid4()), "Iguane noir (Garrobo)", "Ctenosaura similis", "Reptile", "Iguanidae", None, None, None, None, 0, 10, 25, "static/images/Iguane_noir_(Garrobo).jpg"),
                (str(uuid.uuid4()), "Basilic vert", "Basiliscus plumifrons", "Reptile", "Corytophanidae", None, None, None, None, 0, 20, 60, "static/images/Basilic_vert.webp"),
                (str(uuid.uuid4()), "Basilic brun", "Basiliscus vittatus", "Reptile", "Corytophanidae", None, None, None, None, 0, 15, 40, "static/images/Basilic_brun.jpg"),
                (str(uuid.uuid4()), "Boa constricteur", "Boa constrictor", "Reptile", "Boidae", None, None, None, None, 0, 40, 100, "static/images/Boa_constricteur.jpg"),
                (str(uuid.uuid4()), "Fer de lance (Terciopelo)", "Bothrops asper", "Reptile", "Viperidae", None, None, None, None, 0, 60, 150, "static/images/Bothrops_asper.jpg"),
                (str(uuid.uuid4()), "Vipère de Schlegel", "Bothriechis schlegelii", "Reptile", "Viperidae", None, None, None, None, 0, 70, 180, "static/images/Vipere_de_Schlegel.jpg"),
                (str(uuid.uuid4()), "Faux serpent corail", "Lampropeltis triangulum", "Reptile", "Colubridae", None, None, None, None, 0, 50, 120, "static/images/Faux_serpent_corail.png"),
                (str(uuid.uuid4()), "Serpent liane", "Oxybelis aeneus", "Reptile", "Colubridae", None, None, None, None, 0, 40, 90, "static/images/Serpent_liane.jpeg"),
                (str(uuid.uuid4()), "Tortue verte", "Chelonia mydas", "Reptile", "Cheloniidae", None, None, None, None, 0, 50, 100, "static/images/Tortue_verte.jpg"),
                (str(uuid.uuid4()), "Tortue luth", "Dermochelys coriacea", "Reptile", "Dermochelyidae", None, None, None, None, 0, 80, 200, "static/images/Tortue_luth.jpg"),
                (str(uuid.uuid4()), "Tortue imbriquée", "Eretmochelys imbricata", "Reptile", "Cheloniidae", None, None, None, None, 0, 70, 180, "static/images/Tortue_imbriquee.jpg"),
                (str(uuid.uuid4()), "Gecko casqué", "Corytophanes cristatus", "Reptile", "Corytophanidae", None, None, None, None, 0, 30, 70, "static/images/Gecko_casque.jpg"),

                # --- AMPHIBIENS ---
                (str(uuid.uuid4()), "Dendrobate fraise", "Oophaga pumilio", "Amphibien", "Dendrobatidae", None, None, None, None, 10, 25, 60, "static/images/Dendrobate fraise.webp"),
                (str(uuid.uuid4()), "Dendrobate doré", "Dendrobates auratus", "Amphibien", "Dendrobatidae", None, None, None, None, 10, 30, 70, "static/images/Dendrobate_dore.jpg"),
                (str(uuid.uuid4()), "Rainette aux yeux rouges", "Agalychnis callidryas", "Amphibien", "Phyllomedusidae", None, None, None, None, 15, 40, 100, "static/images/Rainette_aux_yeux_rouges.webp"),
                (str(uuid.uuid4()), "Rainette de verre", "Hyalinobatrachium spp.", "Amphibien", "Centrolenidae", None, None, None, None, 20, 50, 120, "static/images/Rainette_de_verre.jpg"),
                (str(uuid.uuid4()), "Crapaud géant", "Rhinella marina", "Amphibien", "Bufonidae", None, None, None, None, 5, 10, 20, "static/images/Crapaud_geant.jpg"),
                (str(uuid.uuid4()), "Phyllobate lugubre", "Phyllobates lugubris", "Amphibien", "Dendrobatidae", None, None, None, None, 10, 35, 80, "static/images/Phyllobate_lugubre.jpeg"),
                (str(uuid.uuid4()), "Grenouille masquée", "Smilisca phaeota", "Amphibien", "Hylidae", None, None, None, None, 10, 20, 50, "static/images/Grenouille_masquee.jpeg"),
                (str(uuid.uuid4()), "Grenouille de litière", "Craugastor spp.", "Amphibien", "Craugastoridae", None, None, None, None, 5, 15, 35, "static/images/Grenouille_de_litiere.jpg"),
                (str(uuid.uuid4()), "Salamandre tropicale", "Bolitoglossa spp.", "Amphibien", "Plethodontidae", None, None, None, None, 0, 60, 150, "static/images/Salamandre_tropicale.jpg"),
                (str(uuid.uuid4()), "Cécilie", "Gymnophiona", "Amphibien", "Caeciliidae", None, None, None, None, 0, 100, 300, "static/images/Cécilie.jpg"),

                # --- MARINS ET AQUATIQUES ---
                (str(uuid.uuid4()), "Baleine à bosse", "Megaptera novaeangliae", "Mammifère", "Balaenopteridae", None, None, None, None, 20, 60, 150, "static/images/Baleine_a_bosse.jpg"),
                (str(uuid.uuid4()), "Grand dauphin", "Tursiops truncatus", "Mammifère", "Delphinidae", None, None, None, None, 10, 30, 80, "static/images/Grand_dauphin.jpg"),
                (str(uuid.uuid4()), "Dauphin tacheté pantropical", "Stenella attenuata", "Mammifère", "Delphinidae", None, None, None, None, 10, 30, 80, "static/images/Dauphin_tachete_pantropical.png"),
                (str(uuid.uuid4()), "Orque", "Orcinus orca", "Mammifère", "Delphinidae", None, None, None, None, 50, 200, 500, "static/images/Orque.jpeg"),
                (str(uuid.uuid4()), "Lamantin des Caraïbes", "Trichechus manatus", "Mammifère", "Trichechidae", None, None, None, None, 0, 100, 250, "static/images/Lamantin_des_Caraibes.jpg"),
                (str(uuid.uuid4()), "Requin-bouledogue", "Carcharhinus leucas", "Poisson", "Carcharhinidae", None, None, None, None, 0, 50, 150, "static/images/Requin-bouledogue.jpeg"),
                (str(uuid.uuid4()), "Requin à pointes blanches", "Triaenodon obesus", "Poisson", "Carcharhinidae", None, None, None, None, 0, 40, 100, "static/images/Requin_a_pointes_blanches.webp"),
                (str(uuid.uuid4()), "Raie manta", "Manta birostris", "Poisson", "Mobulidae", None, None, None, None, 0, 50, 120, "static/images/Raie_manta.webp"),
                (str(uuid.uuid4()), "Poisson-ange français", "Pomacanthus paru", "Poisson", "Pomacanthidae", None, None, None, None, 0, 15, 40, "static/images/Poisson-ange_francais.jpeg"),
                (str(uuid.uuid4()), "Poisson-perroquet", "Scaridae spp.", "Poisson", "Scaridae", None, None, None, None, 0, 10, 30, "static/images/Poisson-perroquet.jpg"),

                # --- INSECTES ET ARACHNIDES ---
                (str(uuid.uuid4()), "Morpho bleu", "Morpho peleides", "Insecte", "Nymphalidae", None, None, None, None, 0, 5, 40, "static/images/Morpho_bleu.jpeg"),
                (str(uuid.uuid4()), "Papillon chouette", "Caligo eurilochus", "Insecte", "Nymphalidae", None, None, None, None, 0, 10, 30, "static/images/Papillon_chouette.jpeg"),
                (str(uuid.uuid4()), "Papillon Heliconius", "Heliconius melpomene", "Insecte", "Nymphalidae", None, None, None, None, 0, 10, 25, "static/images/Papillon_Heliconius.jpeg"),
                (str(uuid.uuid4()), "Fourmi coupe-feuille", "Atta cephalotes", "Insecte", "Formicidae", None, None, None, None, 0, 5, 15, "static/images/Fourmi_coupe-feuille.jpg"),
                (str(uuid.uuid4()), "Fourmi balle de fusil", "Paraponera clavata", "Insecte", "Paraponeridae", None, None, None, None, 0, 20, 50, "static/images/Fourmi_balle_de_fusil.jpg"),
                (str(uuid.uuid4()), "Abeille sans dard", "Meliponini", "Insecte", "Apidae", None, None, None, None, 5, 10, 30, "static/images/Abeille_sans_dard.jpg"),
                (str(uuid.uuid4()), "Scarabée rhinocéros", "Dynastes hercules", "Insecte", "Scarabaeidae", None, None, None, None, 0, 40, 90, "static/images/Scarabee_rhinoceros.jpeg"),
                (str(uuid.uuid4()), "Phasme", "Phasmatodea", "Insecte", "Phasmatidae", None, None, None, None, 0, 30, 70, "static/images/Phasme.jpeg"),
                (str(uuid.uuid4()), "Mygale à genoux rouges", "Aphonopelma seemanni", "Arachnide", "Theraphosidae", None, None, None, None, 0, 30, 80, "static/images/Mygale_a_genoux_rouges.jpg"),
                (str(uuid.uuid4()), "Araignée Néphile dorée", "Trichonephila clavipes", "Arachnide", "Araneidae", None, None, None, None, 0, 15, 40, "static/images/Araignee_Nephile_doree.jpeg"),

                # --- PLANTES ---
                (str(uuid.uuid4()), "Figuier étrangleur", "Ficus aurea", "Plante", "Moraceae", None, None, None, None, 0, 5, 15, "static/images/Figuier_etrangleur.webp"),
                (str(uuid.uuid4()), "Ceiba (Fromager géant)", "Ceiba pentandra", "Plante", "Malvaceae", None, None, None, None, 0, 10, 20, "static/images/Ceiba_(Fromager_geant).jpg"),
                (str(uuid.uuid4()), "Arbre de Guanacaste", "Enterolobium cyclocarpum", "Plante", "Fabaceae", None, None, None, None, 0, 10, 20, "static/images/Arbre_de_Guanacaste.jpg"),
                (str(uuid.uuid4()), "Palmier marcheur", "Socratea exorrhiza", "Plante", "Arecaceae", None, None, None, None, 0, 15, 30, "static/images/Palmier_marcheur.jpeg"),
                (str(uuid.uuid4()), "Fleur Héliconia rostrata", "Heliconia rostrata", "Plante", "Heliconiaceae", None, None, None, None, 0, 5, 15, "static/images/Fleur_Heliconia_rostrata.jpg"),
                (str(uuid.uuid4()), "Fleur Oiseau de paradis", "Strelitzia reginae", "Plante", "Strelitziaceae", None, None, None, None, 0, 5, 15, "static/images/Fleur_Oiseau_de_paradis.jpg"),
                (str(uuid.uuid4()), "Orchidée Guaria Morada", "Guarianthe skinneri", "Plante", "Orchidaceae", None, None, None, None, 0, 30, 60, "static/images/Orchidee _Guaria_Morada.jpg"),
                (str(uuid.uuid4()), "Cacaoyer (avec cabosses)", "Theobroma cacao", "Plante", "Malvaceae", None, None, None, None, 0, 10, 20, "static/images/Cacaoyer_(avec_cabosses).jpeg"),
                (str(uuid.uuid4()), "Arbre à pain", "Artocarpus altilis", "Plante", "Moraceae", None, None, None, None, 0, 10, 20, "static/images/Arbre_a_pain.jpeg"),
                (str(uuid.uuid4()), "Mimosa pudica (sensitive)", "Mimosa pudica", "Plante", "Fabaceae", None, None, None, None, 0, 15, 30, "static/images/Mimosa pudica.jpg")
            ]

            cursor.executemany("""
                INSERT INTO Espece (id_espece, nom_courant, nom_scientifique, classe, famille, 
                                    longevite_annees, reproduction_jours, taille_cm, couleurs_principales, points_entendu, points_vu, points_photo, image_reference)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, especes_costa_rica)

        cursor.execute("SELECT COUNT(*) FROM Participant")
        if cursor.fetchone()[0] == 0:
            participants_test = [
                (str(uuid.uuid4()), "Elliot", 0),
                (str(uuid.uuid4()), "Timothé", 0),
                (str(uuid.uuid4()), "Dominique", 0),
                (str(uuid.uuid4()), "Pascal", 0),
                (str(uuid.uuid4()), "Emily", 0)
            ]
            cursor.executemany("INSERT INTO Participant (id_participant, prenom, score_total) VALUES (?, ?, ?)", participants_test)
            
        conn.commit()
        print("Succès : La base de données a été initialisée !")

if __name__ == "__main__":
    initialiser_bdd()