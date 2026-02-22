import sqlite3
import chess
import random
import csv
import time

# Doc SQL --> https://www.w3schools.com/sql/default.asp
# Doc Python --> https://realpython.com/ref/stdlib/sqlite3/
# Infos joueurs --> https://www.chess.com/ratings

# ================================================================
# ==================== Mise en place relation ====================
# ================================================================

def connexion_base():
    # Mise en relation de la base base.db
    connexion = sqlite3.connect("base.db")
    # Ajout du pointeur
    curseur = connexion.cursor()
    return connexion, curseur

# ==========================================================
# ==================== Fonctions utiles ====================
# ==========================================================

#           ========== Ajouter un joueur ==========

def ajouter_joueur(nom, prenom, mail, elo=1000):
    connexion, curseur = connexion_base()
    while verif_mail(mail) == True:
        choix = int(input(f"(1) Annuler l'inscription de {prenom} {nom} | (2) Modifier le mail.\n"))
        if choix == 1:
            connexion.close()
            return f"Inscription de {prenom} {nom} annulée"
        elif choix == 2:
            mail = str(input(f"Entrez un nouveau mail pour le joueur {prenom} {nom} : "))
        else:
            print("Choix invalide : ")
    curseur.execute(f"INSERT INTO joueurs(Nom, Prenom, Mail, Elo) VALUES ('{nom}', '{prenom}', '{mail}', {elo})")
    ajouter_parties(0, 0, 0, 0, curseur)

    connexion.commit()
    connexion.close()

#           ========== Vérification du mail ==========

def verif_mail(mail):
    connexion, curseur = connexion_base()
    curseur.execute(f"SELECT COUNT(*) FROM joueurs WHERE Mail = '{mail}'")
    for ligne in curseur:
         nb = ligne[0]
         return nb > 0
    connexion.commit()
    connexion.close()
    return False

#           ========== Nombre de joueurs inscrits ==========

def nombre_inscrits():
    connexion, curseur = connexion_base()
    curseur.execute("SELECT COUNT(*) FROM joueurs")
    for ligne in curseur:
        nb_joueurs = ligne[0]
    connexion.commit()
    connexion.close()

    return nb_joueurs

#           ========== Ajouter les parties à l'inscription ==========

def ajouter_parties(jouees, gagnees, nulles, perdues, curseur):
    joueur = nombre_inscrits() + 1
    curseur.execute(f"INSERT INTO parties(ID, Jouées, Gagnées, Nulles, Perdues) VALUES ({(joueur)}, {jouees}, {gagnees}, {nulles}, {perdues})")
    curseur.execute(f"INSERT INTO gagnees(ID, Mat, Temps, Abandon) VALUES ({joueur}, 0, 0, 0)")
    curseur.execute(f"INSERT INTO nulles(ID, Pat, Demande) VALUES ({joueur}, 0, 0)")
    curseur.execute(f"INSERT INTO perdues(ID, Mat, Temps, Abandon) VALUES ({joueur}, 0, 0, 0)")

#           ========== Créer les tables ==========

def creer_tables(liste_tables, attributs_tables, types_attributs):
    connexion, curseur = connexion_base()
    for table in range(len(liste_tables)):
        nom_table = liste_tables[table]
        attributs = attributs_tables[table]
        types = types_attributs[table]
        colonnes = []

        for attribut in range(len(attributs)):
            attribut_final = attributs[attribut]
            type_final = types[attribut]
            colonnes.append(f"{attribut_final} {type_final}")
        
        colonnes_sql = ", ".join(colonnes)
        curseur.execute(f"CREATE TABLE IF NOT EXISTS {nom_table} ({colonnes_sql})")
    connexion.commit()
    connexion.close()

#           ========== Supprimer les tables ==========

def supp_tables(liste_tables):
    connexion, curseur = connexion_base()
    for i in liste_tables:
        curseur.execute(f"DROP TABLE {i}")
    connexion.commit()
    connexion.close()


# ======================================================
# ==================== Début du jeu ====================
# ======================================================

#           ========== S'inscrire ==========

def inscription():
    import time 

    print("Inscrivez-vous pour commencer !\n")
    nom = str(input("Nom : "))
    while type(nom) != str:
        nom = str(input("Nom : "))
    prenom = str(input("Prenom : "))
    while type(prenom) != str:
        prenom = str(input("Prenom : "))
    mail = str(input("Mail : "))
    while type(mail) != str:
        mail = str(input("Mail : "))
    while verif_mail(mail) == True:
        mail = str(input("Entrez un nouveau mail : "))
    elo = int(input("Elo : "))
    while type(elo) != int:
        elo = int(input("Entrez un nombre entier pour l'Elo : "))

    connexion, curseur = connexion_base()

    ajouter_joueur(nom, prenom, mail, elo)
    time.sleep(1)
    curseur.execute(f"SELECT * FROM joueurs WHERE ID = {nombre_inscrits()}")

    print(f"Inscription complétée, voici vos informations:\n{list(curseur)}")
    ajouter_parties(0, 0, 0, 0, curseur)

    connexion.commit()
    connexion.close()

#       ========== Fonction de lancement ==========

def commencer():
    connexion, curseur = connexion_base()
    
    joueur_a = int(input("Choisissez un joueur A : "))
    while joueur_a > nombre_inscrits() or joueur_a < 0:
        joueur_a = int(input(f"ID invalide (1-{nombre_inscrits()}) : "))

    joueur_b = int(input("Choisissez un joueur B : "))
    while joueur_b > nombre_inscrits() or joueur_b < 0:
        joueur_b = int(input(f"ID invalide (1-{nombre_inscrits()}) : "))
    while joueur_b == joueur_a:
        joueur_b = int(input(f"ID invalide (1-{nombre_inscrits()}) : "))

    curseur.execute(f"SELECT * from joueurs WHERE ID = {joueur_a}")
    infos_joueur_a = list(curseur)
    curseur.execute(f"SELECT * from joueurs WHERE ID = {joueur_b}")
    infos_joueur_b = list(curseur)

    connexion.close()
    return infos_joueur_a, infos_joueur_b

def inserer_joueur():
    connexion, curseur = connexion_base()
    reponse = 0
    while reponse not in(1,2, 3):
        reponse = int(input("(1) Jouer | (2) Inserer les données d'une partie jouée | (3) Interactions de joueurs\n"))
        
    while reponse == 2:
        inserer_joueur_a = int(input("Qui était le joueur A (ID) : "))
        while inserer_joueur_a > nombre_inscrits() or inserer_joueur_a < 0:
            inserer_joueur_a = int(input(f"ID invalide (1-{nombre_inscrits()}) : "))
        
        inserer_joueur_b = int(input("Qui était le joueur B (ID) : "))
        while inserer_joueur_b > nombre_inscrits() or inserer_joueur_b < 0:
            inserer_joueur_b = int(input(f"ID invalide (1-{nombre_inscrits()}) : "))
        
        resultat_partie = input("Quel était le résultat de la partie ?\n1-0 = A gagne | 0-1 = B gagne | 1/2-1/2 = Nulle : ")
        while resultat_partie not in("1-0", "0-1", "1/2-1/2"):
            resultat_partie = input("Resultat incorrect.\n 1-0 = A gagne | 0-1 = B gagne | 1/2-1/2 = Nulle : ")
            
        curseur.execute(f"SELECT * from joueurs WHERE ID = {inserer_joueur_a}")
        infos_inserer_joueur_a = list(curseur)
        curseur.execute(f"SELECT * from joueurs WHERE ID = {inserer_joueur_b}")
        infos_inserer_joueur_b = list(curseur)
        
        modifications_donnees(infos_inserer_joueur_a, infos_inserer_joueur_b, resultat_partie)
        reponse = 0
        connexion.close()
        inserer_joueur()
    
    if reponse == 1:
        return
    
    if reponse == 3:
        reponse_interaction = int(input("(1) Ajouter un joueur | (2) Supprimer un joueur | (3) Obtenir le classement\n"))
        while reponse_interaction not in(1,2,3):
            reponse_interaction = int(input("Réponse invalide\n(1) Ajouter un joueur | (2) Supprimer un joueur | (3) Obtenir le classement\n"))

        if reponse_interaction == 1:
            inscription()
         
        if reponse_interaction == 2:
            reponse_suppression = int(input("Quel joueur voulez-vous supprimer (ID) ? : "))
            while reponse_suppression > nombre_inscrits():
                reponse_suppression = int(input(f"ID invalide (1-{nombre_inscrits()}) ? : "))
            curseur.execute(f"DELETE FROM joueurs WHERE ID = {reponse_suppression}")
            print(f"Le joueur a bien été supprimé.")
            connexion.commit()
            connexion.close()
            inserer_joueur()

        if reponse == 3:
            reponse_classement = int(input("(1) Obtenir le classement croissant | (2) décroissant\n"))
            while reponse_classement not in(1,2):
                reponse_classement = int(input("Réponse invalide\n(1) Obtenir le classement croissant | (2) décroissant\n"))

            if reponse_classement == 1:
                curseur.execute("SELECT * FROM joueurs ORDER BY Elo DESC")
                classement_croissant = list(curseur)
                print(classement_croissant)
                connexion.close()
                inserer_joueur()
            
            else:
                curseur.execute("SELECT * FROM joueurs ORDER BY Elo DESC")
                classement_decroissant = list(curseur)
                print(classement_decroissant)
                connexion.close()
                inserer_joueur()        

# =================================================
# ==================== Parties ====================
# =================================================

def simuler_partie():
    board = chess.Board()
    coups = []

    while not board.is_game_over():
        coups_legaux = list(board.legal_moves)
        coup = random.choice(coups_legaux)   # coup aléatoire parmis les coups légaux (donc n'importe quoi)
        coups.append(board.san(coup))        # language échec (KQRBNP, ABCDEFGH, 12345678, #+= )
        board.push(coup)

    print(f"Voici l'échiquier final\n\n{board}\n")
    resultat = board.result()  # "1-0", "0-1", "1/2-1/2" --> blancs, noirs gagnent | nulle

    return coups, resultat

# ============================================================================

def jouer(joueur_a, joueur_b):
    board = chess.Board()
    coups = []
    print(f"Le joueur {joueur_b[0][2]} {joueur_b[0][1]} ({joueur_b[0][4]}) est désormais le votre.")

    while not board.is_game_over():
        coups_legaux = list(board.legal_moves)
        
        coup = random.choice(coups_legaux)
        coups.append(board.san(coup))
        board.push(coup)
        print(f"{joueur_a[0][2]} {joueur_a[0][1]} joue {coup}")
        if board.is_game_over():
            break

# =======================

        coups_legaux = list(board.legal_moves)

        san_legaux = {board.san(coup_legal): coup_legal for coup_legal in coups_legaux}
        uci_legaux = {coup_legal.uci(): coup_legal for coup_legal in coups_legaux}

        reponse = int(input(f"{board}\nVoici l'échiquier actuel, vous avez les noirs.\n(1) Voir la liste des coups légaux |  (2) Jouer | (3) Abandonner\n"))
        while reponse not in(1,2,3):
            reponse = int(input(f"Reponse invalide : "))
        if reponse == 1:
            coup_perso_str = input(f"{coups_legaux}\nQue voulez-vous jouer ? : ")
        elif reponse == 2:
            coup_perso_str = input(f"Que voulez-vous jouer ? : ")
        else:
            connexion, curseur = connexion_base()
            curseur.execute(f"UPDATE gagnees SET Abandon = Abandon + 1 WHERE ID = {joueur_a[0][0]}")
            curseur.execute(f"UPDATE perdues SET Abandon = Abandon + 1 WHERE ID = {joueur_b[0][0]}")
            connexion.commit()
            connexion.close()
            return coups, "1-0"
            

        while coup_perso_str not in san_legaux and coup_perso_str not in uci_legaux:
            coup_perso_str = input("Coup illégal, réessayez : ")
        # Sélection,e le bon coup
        if coup_perso_str in san_legaux:
            coup_noir = san_legaux[coup_perso_str]
        else:
            coup_noir = uci_legaux[coup_perso_str]

        coups.append(board.san(coup_noir))
        board.push(coup_noir)

        resultat = board.result()
    return coups, resultat

# ==================================================================
# ==================== Modifications des tables ====================
# ==================================================================

def modifications_donnees(joueur_A, joueur_B, resultat):
    connexion, curseur = connexion_base()

    if resultat == "1-0":
      print(f"{joueur_A[0][2]} {joueur_A[0][1]} ({joueur_A[0][4]}) gagne")

      elo_add, elo_retrait = systeme_elo(joueur_A[0][4], joueur_B[0][4], resultat)
      curseur.execute(f"UPDATE joueurs SET Elo = Elo + {elo_add} WHERE ID = {joueur_A[0][0]}")
      curseur.execute(f"UPDATE joueurs SET Elo = Elo + {elo_retrait} WHERE ID = {joueur_B[0][0]}")
      print(f"Elo mis à jour --> {joueur_A[0][2]} {joueur_A[0][1]} ({joueur_A[0][4]}) ({elo_add}) | {joueur_B[0][2]} {joueur_B[0][1]} ({joueur_B[0][4]}) ({elo_retrait})")

      curseur.execute(f"UPDATE parties SET Gagnées = Gagnées + 1 WHERE ID = {joueur_A[0][0]}")
      curseur.execute(f"UPDATE parties SET Perdues = Perdues + 1 WHERE ID = {joueur_B[0][0]}")

    elif resultat == "0-1":
        print(f"{joueur_B[0][2]} {joueur_B[0][1]} ({joueur_B[0][4]}) gagne")

        elo_add, elo_retrait = systeme_elo(joueur_A[0][4], joueur_B[0][4], resultat)
        curseur.execute(f"UPDATE joueurs SET Elo = Elo + {elo_add} WHERE ID = {joueur_B[0][0]}")
        curseur.execute(f"UPDATE joueurs SET Elo = Elo + {elo_retrait} WHERE ID = {joueur_A[0][0]}")
        print(f"Elo mis à jour\n{joueur_A[0][2]} {joueur_A[0][1]} ({joueur_A[0][4]}) ({elo_retrait}) | {joueur_B[0][2]} {joueur_B[0][1]} ({joueur_B[0][4]}) ({elo_add})")

        curseur.execute(f"UPDATE parties SET Gagnées = Gagnées + 1 WHERE ID = {joueur_B[0][0]}")
        curseur.execute(f"UPDATE parties SET Perdues = Perdues + 1 WHERE ID = {joueur_A[0][0]}")
    else:
        print(f"{joueur_A[0][2]} {joueur_A[0][1]} ({joueur_A[0][4]}) et {joueur_B[0][2]} {joueur_B[0][1]} ({joueur_B[0][4]}) ont fait nulle")

        elo_add, elo_retrait = systeme_elo(joueur_A[0][4], joueur_B[0][4], resultat)
        curseur.execute(f"UPDATE joueurs SET Elo = Elo + {elo_add} WHERE ID = {joueur_A[0][0]}")
        curseur.execute(f"UPDATE joueurs SET Elo = Elo + {elo_retrait} WHERE ID = {joueur_B[0][0]}")
        print(f"Elo mis à jour\n{joueur_A[0][2]} {joueur_A[0][1]} ({joueur_A[0][4]}) ({elo_add}) | {joueur_B[0][2]} {joueur_B[0][1]} ({joueur_B[0][4]}) ({elo_retrait})")

        curseur.execute(f"UPDATE parties SET Nulles = Nulles + 1 WHERE ID = {joueur_A[0][0]}")
        curseur.execute(f"UPDATE parties SET Nulles = Nulles + 1 WHERE ID = {joueur_B[0][0]}")

    curseur.execute(f"UPDATE parties SET Jouées = Jouées + 1 WHERE ID = {joueur_A[0][0]}")
    curseur.execute(f"UPDATE parties SET Jouées = Jouées + 1 WHERE ID = {joueur_B[0][0]}")

    connexion.commit()
    connexion.close()

def systeme_elo(elo_A, elo_B, resultat):
    if elo_A >= elo_B:
        elo_haut, elo_bas = elo_A, elo_B
        A_est_haut = True
    else:
        elo_haut, elo_bas = elo_B, elo_A
        A_est_haut = False

    diff = elo_haut - elo_bas

    if resultat != "1/2-1/2":
        if resultat != "1-0":
            if elo_A == elo_haut:
                if diff <= 25:
                    return 8, -8
                elif diff >= 26 and diff <=50:
                    return 9, -9
                elif diff >= 51 and diff <= 100:
                    return 10, -10
                elif diff >= 101 and diff <= 400:
                    return 11, -11
                else:
                    return 12, -12
            else:
                if diff <= 25:
                    return 8, -8
                elif diff >= 26 and diff <=50:
                    return 7, -7
                elif diff >= 51 and diff <= 100:
                    return 6, -6
                elif diff >= 101 and diff <= 400:
                    return 5, -5
                else:
                    return 4, -4
        else:
            if elo_A == elo_haut:
                if diff <= 25:
                    return 8, -8
                elif diff >= 26 and diff <=50:
                    return 7, -7
                elif diff >= 51 and diff <= 100:
                    return 6, -6
                elif diff >= 101 and diff <= 400:
                    return 5, -5
                else:
                    return 4, -4
            else:
                if diff <= 25:
                    return 8, -8
                elif diff >= 26 and diff <=50:
                    return 9, -9
                elif diff >= 51 and diff <= 100:
                    return 10, -10
                elif diff >= 101 and diff <= 400:
                    return 11, -11
                else:
                    return 12, -12
    else:
        if A_est_haut:
            if diff <= 25:
                return 0, 0
            elif diff <= 50:
                return -1, 1
            elif diff <= 100:
                return -2, 2
            elif diff <= 400:
                return -3, 3
            else:
                return -4, 4

        else:
            if diff <= 25:
                return 0, 0
            elif diff <= 50:
                return 1, -1
            elif diff <= 100:
                return 2, -2
            elif diff <= 400:
                return 3, -3
            else:
                return 4, -4





# ============================================================================





# ============================================================
# ==================== Gestion des tables ====================
# ============================================================

# Pour faire les test:
#supp_tables(("joueurs",  "parties", "gagnees", "nulles", "perdues"))

creer_tables(
    ("joueurs", "parties", "gagnees", "nulles", "perdues"),
    [
        ("ID", "Nom", "Prenom", "Mail", "Elo"),
        ("ID", "Jouées", "Gagnées", "Nulles", "Perdues"),
        ("ID", "Mat", "Temps", "Abandon"),
        ("ID", "Pat", "Demande"),
        ("ID", "Mat", "Temps", "Abandon")
    ],[
        ("INTEGER PRIMARY KEY", "TEXT", "TEXT", "TEXT", "INT"),
        ("INT", "INT", "INT", "INT", "INT"),
        ("INT", "INT", "INT", "INT"),
        ("INT", "INT", "INT"),
        ("INT", "INT", "INT", "INT")
    ])

# =================== Ajout des joueurs ===================
"""
ajouter_joueur("Carlsen", "Magnus", "magnus@test.com", 2840)
ajouter_joueur("Nakamura", "Hikaru", "hikaru@test.com", 2810)
ajouter_joueur("Carruana", "Fabiano", "fabiano@test.com", 2795)
ajouter_joueur("Keymer", "Vincent", "vincent@test.com", 2776)
ajouter_joueur("Erigaisi", "Arjun", "arjun@test.com", 2775)
ajouter_joueur("Firouzja", "Alireza", "alireza@test.com", 2762)
ajouter_joueur("Rameshbabu", "Praggnanandhaa", "praggnanandhaa@test.com", 2761)
ajouter_joueur("Giri", "Anish", "anish@test.com", 2760)
ajouter_joueur("Yi", "Wei", "wei@test.com", 2754)
ajouter_joueur("Dommaraju", "Gukesh", "gukesh@test.com", 2754)"""

#           ========== A partir du csv ==========

fichier=open("joueurs.csv")
infos_joueurs=list(csv.DictReader(fichier,delimiter=","))
fichier.close()

for info in range(len(infos_joueurs)):
    infos_joueurs[info]=dict(infos_joueurs[info])

for joueur in range(len(infos_joueurs)):
    ajouter_joueur(infos_joueurs[joueur]["nom"], infos_joueurs[joueur]["prenom"], infos_joueurs[joueur]["mail"], infos_joueurs[joueur]["elo"])



# ===========================================================
# ==================== Définition du jeu ====================
# ===========================================================

def jeu():

    inserer_joueur()

    jA , jB = commencer()
    print(f"{jA[0][2]} {jA[0][1]} ({jA[0][4]}) vs {jB[0][2]} {jB[0][1]} ({jB[0][4]})\n")
    time.sleep(2)

    reponse = int(input("(1) Jouer une vraie partie contre une IA | (2) Simuler une partie\n"))
    while reponse not in(1,2):
        reponse = int(input("Choix invalide\n(1) Jouer une vraie partie contre une IA | (2) Simuler une partie\n"))
    
    if reponse == 2:
        print("=== Partie simulée ===")
        time.sleep(1)
        coups, resultat = simuler_partie()
        modifications_donnees(jA, jB, resultat)
        # print(list(coups))
        continuer()

    if reponse == 1:
        coups, resultat = jouer(jA, jB)
        modifications_donnees(jA, jB, resultat)
        continuer()

def continuer():
    reponse = int(input("(1) Relancer une partie | (2) Quitter le jeu\n"))
    if reponse == 1:
        jeu()
    elif reponse==2:
        return
    else:
        reponse = int(input("Choix invalide : "))
    

inscription()
jeu()