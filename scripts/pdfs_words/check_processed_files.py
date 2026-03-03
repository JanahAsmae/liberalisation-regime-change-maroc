"""
Script de vérification récursif : compare les fichiers sources (dans une arborescence)
avec les fichiers de sortie (dans un dossier de destination).
Utile pour s'assurer que tous les fichiers ont été traités.
"""

import os

# Configuration - À MODIFIER SELON VOTRE ARBORESCENCE
DOSSIER_SOURCE = "data/raw/maroc/inflation/IPC"          # racine des sources
DOSSIER_DESTINATION = "data/interim/maroc/inflation"     # dossier contenant les CSV générés
EXTENSIONS_SOURCE = ['.pdf', '.doc', '.docx']            # extensions des fichiers sources
EXTENSIONS_DEST = ['.csv']                               # extensions des fichiers de sortie
RECHERCHE_RECURSIVE_SOURCE = True                        # parcourir récursivement la source
RECHERCHE_RECURSIVE_DEST = False                         # les CSV sont dans un seul dossier (False)

def obtenir_fichiers(dossier, extensions, recursif):
    """
    Retourne un ensemble des noms de base (sans extension) des fichiers
    du dossier ayant les extensions données.
    Si recursif est True, parcourt tous les sous-dossiers.
    """
    fichiers = set()
    if not os.path.isdir(dossier):
        return fichiers
    if recursif:
        for racine, sous_dossiers, fichiers_liste in os.walk(dossier):
            for f in fichiers_liste:
                nom, ext = os.path.splitext(f)
                if ext.lower() in [e.lower() for e in extensions]:
                    fichiers.add(nom)
    else:
        for f in os.listdir(dossier):
            chemin = os.path.join(dossier, f)
            if os.path.isfile(chemin):
                nom, ext = os.path.splitext(f)
                if ext.lower() in [e.lower() for e in extensions]:
                    fichiers.add(nom)
    return fichiers

def main():
    if not os.path.isdir(DOSSIER_SOURCE):
        print(f"Erreur : le dossier source '{DOSSIER_SOURCE}' n'existe pas.")
        return
    if not os.path.isdir(DOSSIER_DESTINATION):
        print(f"Erreur : le dossier destination '{DOSSIER_DESTINATION}' n'existe pas.")
        return

    fichiers_source = obtenir_fichiers(DOSSIER_SOURCE, EXTENSIONS_SOURCE, RECHERCHE_RECURSIVE_SOURCE)
    fichiers_dest = obtenir_fichiers(DOSSIER_DESTINATION, EXTENSIONS_DEST, RECHERCHE_RECURSIVE_DEST)

    print(f"Fichiers sources trouvés : {len(fichiers_source)}")
    print(f"Fichiers de destination trouvés : {len(fichiers_dest)}")

    manquants = fichiers_source - fichiers_dest
    en_trop = fichiers_dest - fichiers_source

    if manquants:
        print(f"\n⚠️  {len(manquants)} fichier(s) source(s) non trouvé(s) en destination :")
        for nom in sorted(manquants):
            print(f"   - {nom}")
    else:
        print("\n✅ Tous les fichiers sources ont un équivalent en destination.")

    if en_trop:
        print(f"\nℹ️  {len(en_trop)} fichier(s) en destination sans source correspondante :")
        for nom in sorted(en_trop):
            print(f"   - {nom}")
    else:
        print("✅ Aucun fichier inattendu en destination.")

if __name__ == "__main__":
    main()