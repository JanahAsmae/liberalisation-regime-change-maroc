import os
import re
import pandas as pd
import pdfplumber
from pathlib import Path

# Dossier contenant les PDF
INPUT_DIR = "data\\raw\\maroc\\inflation\\IPC\\pdfs\\structure1"
# Dossier de sortie pour les CSV individuels
INTERIM_DIR = "data\\interim\\maroc\\inflation"
os.makedirs(INTERIM_DIR, exist_ok=True)

# Expression régulière pour extraire année et mois du nom de fichier (format: ipc_AAAA_MM.pdf)
FILENAME_PATTERN = re.compile(r"ipc_(\d{4})_(\d{2})", re.IGNORECASE)

def extraire_annee_mois(nom_fichier):
    """Extrait l'année et le mois depuis le nom de fichier."""
    match = FILENAME_PATTERN.search(nom_fichier)
    if match:
        annee = match.group(1)
        mois_num = match.group(2)
        mois_noms = {
            "01": "janvier", "02": "février", "03": "mars", "04": "avril",
            "05": "mai", "06": "juin", "07": "juillet", "08": "août",
            "09": "septembre", "10": "octobre", "11": "novembre", "12": "décembre"
        }
        mois = mois_noms.get(mois_num, mois_num)
        return annee, mois
    return None, None

def traiter_pdf(chemin_pdf):
    """
    Extrait les données du tableau des divisions de produits (page 2).
    Retourne une liste de dictionnaires ou None si échec.
    """
    annee, mois = extraire_annee_mois(chemin_pdf.name)
    if not annee or not mois:
        print(f"⚠️  Impossible d'extraire année/mois de {chemin_pdf.name} – ignoré.")
        return None

    with pdfplumber.open(chemin_pdf) as pdf:
        if len(pdf.pages) < 2:
            print(f"⚠️  {chemin_pdf.name} : moins de 2 pages, ignoré.")
            return None
        page = pdf.pages[1]
        tables = page.extract_tables()
        if not tables:
            print(f"⚠️  {chemin_pdf.name} : aucun tableau trouvé page 2.")
            return None

        # Parcourir tous les tableaux pour trouver celui contenant "Produits alimentaires"
        for raw_table in tables:
            # Chercher la ligne de début des données
            start_index = None
            for i, ligne in enumerate(raw_table):
                if ligne and len(ligne) > 0 and ligne[0] and "Produits alimentaires" in ligne[0]:
                    start_index = i
                    break
            if start_index is None:
                continue

            # Extraire les lignes à partir de start_index
            data_rows = raw_table[start_index:]
            resultats = []
            for ligne in data_rows:
                # Vérifier que la ligne a au moins 3 colonnes et une première colonne non vide
                if len(ligne) < 3 or not ligne[0] or not ligne[0].strip():
                    continue
                produit = ligne[0].strip()
                # La troisième colonne (index 2) contient l'indice du mois courant
                ipc_str = ligne[2] if len(ligne) > 2 else None
                if not ipc_str:
                    continue
                # Nettoyage : remplacer la virgule par un point
                ipc_str = ipc_str.replace(",", ".").strip()
                try:
                    ipc = float(ipc_str)
                except ValueError:
                    print(f"   Valeur non numérique ignorée pour {produit} : {ipc_str}")
                    continue
                resultats.append({
                    "Division par produits": produit,
                    "ipc": ipc,
                    "annee": annee,
                    "mois": mois
                })
                # On s'arrête après "Ensemble" (dernière ligne du tableau)
                if produit == "Ensemble":
                    break
            if resultats:
                return resultats

        print(f"⚠️  {chemin_pdf.name} : aucune table avec 'Produits alimentaires' trouvée.")
        return None

def main():
    fichiers_pdf = sorted(Path(INPUT_DIR).glob("*.pdf"))
    print(f"🔍 {len(fichiers_pdf)} fichiers PDF trouvés dans {INPUT_DIR}\n")
    for chemin in fichiers_pdf:
        print(f"Traitement de {chemin.name}...")
        resultats = traiter_pdf(chemin)
        if resultats:
            df = pd.DataFrame(resultats)
            # Tri optionnel par produit (pour garder l'ordre habituel)
            # On peut aussi laisser l'ordre d'apparition
            df = df.sort_values("Division par produits")
            nom_csv = chemin.stem + ".csv"
            chemin_csv = Path(INTERIM_DIR) / nom_csv
            df.to_csv(chemin_csv, index=False, encoding='utf-8-sig')
            print(f"   → {len(resultats)} lignes extraites et sauvegardées dans {chemin_csv}")
        else:
            print(f"   → 0 lignes extraites.")
    print(f"\n✅ Traitement terminé. Les fichiers CSV sont dans le dossier '{INTERIM_DIR}'.")

if __name__ == "__main__":
    main()