import os
import re
import pandas as pd
import pdfplumber
from pathlib import Path

# Dossier contenant les PDF
INPUT_DIR = "data\\raw\\maroc\\inflation\\IPC\\pdfs\\structure2"
# Dossier de sortie pour les CSV individuels
INTERIM_DIR = "data\\interim\\maroc\\inflation"

# Créer le dossier interim s'il n'existe pas
os.makedirs(INTERIM_DIR, exist_ok=True)

# Expression régulière pour extraire année et mois du nom de fichier (format: ipc_AAAA_MM.pdf)
FILENAME_PATTERN = re.compile(r"ipc_(\d{4})_(\d{2})", re.IGNORECASE)

def extraire_annee_mois(nom_fichier):
    """Extrait l'année et le mois depuis le nom de fichier."""
    match = FILENAME_PATTERN.search(nom_fichier)
    if match:
        annee = match.group(1)
        mois_num = match.group(2)
        # Convertir le numéro en nom de mois
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
    Extrait les données du tableau de la page 2 du PDF.
    Retourne une liste de dictionnaires : [{"produit":..., "ipc":..., "annee":..., "mois":...}, ...]
    """
    annee, mois = extraire_annee_mois(chemin_pdf.name)
    if not annee or not mois:
        print(f"⚠️  Impossible d'extraire année/mois de {chemin_pdf.name} – ignoré.")
        return []

    with pdfplumber.open(chemin_pdf) as pdf:
        if len(pdf.pages) < 2:
            print(f"⚠️  {chemin_pdf.name} : moins de 2 pages, ignoré.")
            return []
        page = pdf.pages[1]
        tables = page.extract_tables()
        if not tables:
            print(f"⚠️  {chemin_pdf.name} : aucun tableau trouvé page 2.")
            return []
        raw_table = tables[0]

    # Les deux premières lignes sont les en-têtes composites, ignorées.
    # Les données commencent à la ligne 2 (index 2)
    data_rows = raw_table[2:]

    resultats = []
    for ligne in data_rows:
        if len(ligne) < 3 or not ligne[0] or not ligne[0].strip():
            continue
        produit = ligne[0].strip()
        ipc_str = ligne[2]
        if not ipc_str:
            continue
        ipc_str = ipc_str.replace(",", ".").strip()
        try:
            ipc = float(ipc_str)
        except ValueError:
            print(f"   Valeur non numérique ignorée pour {produit} : {ipc_str}")
            continue

        resultats.append({
            "Division par produit": produit,
            "ipc": ipc,
            "annee": annee,
            "mois": mois
        })
    return resultats

def main():
    fichiers_pdf = Path(INPUT_DIR).glob("*.pdf")
    for chemin in fichiers_pdf:
        print(f"Traitement de {chemin.name}...")
        resultats = traiter_pdf(chemin)
        if resultats:
            # Créer un DataFrame pour ce fichier
            df = pd.DataFrame(resultats)
            # Trier par produit (optionnel)
            df = df.sort_values("Division par produit")
            # Définir le nom du fichier de sortie (même nom que le PDF, mais .csv)
            nom_csv = chemin.stem + ".csv"
            chemin_csv = Path(INTERIM_DIR) / nom_csv
            df.to_csv(chemin_csv, index=False, encoding='utf-8-sig')
            print(f"   → {len(resultats)} lignes extraites et sauvegardées dans {chemin_csv}")
        else:
            print(f"   → 0 lignes extraites.")

if __name__ == "__main__":
    main()