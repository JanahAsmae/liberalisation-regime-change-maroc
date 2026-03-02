"""
Extraction des données IPC depuis ipc_2011_01.pdf
Tableau 1, Page 2 — colonne "Divisions de produits" + colonne "jan.2011"

Sortie CSV : division_par_produit | ipc | annee | mois
"""

import pdfplumber
import csv
import re

INPUT_PDF = "data\\raw\\maroc\\inflation\\IPC\\pdfs\\structure3\\ipc_2011_01.pdf"
OUTPUT_CSV = "data\\interim\\maroc\\inflation\\ipc_2011_01.csv"


def parse_float(val: str) -> float:
    """Convertit '114,6' ou '-0,1' en float."""
    return float(val.strip().replace(",", "."))


def extract_ipc_janvier_2011(pdf_path: str) -> list[dict]:
    """
    Extrait depuis le Tableau 0 de la page 2 :
      - Colonne 0 : Divisions de produits  (multiline dans row[2], + 'Ensemble' dans row[3])
      - Colonne 2 : Indice jan.2011         (colonne index 2 dans le tableau)
    Retourne une liste de dicts {division_par_produit, ipc, annee, mois}.
    """
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[1]          # page 2 (index 1)
        table = page.extract_tables()[0]   # premier tableau

    # ── Lire l'en-tête pour identifier l'année et le mois de la colonne cible ──
    # row[1] = [None, 'déc.2010', 'jan.2011', 'var.%', '2010', '2011', 'var.%']
    header = table[1]
    col_label = header[2]   # 'jan.2011'

    # Extraire mois et année depuis 'jan.2011'
    match = re.match(r"([a-zéûùô]+)\.?(\d{4})", col_label.strip().lower())
    if not match:
        raise ValueError(f"Impossible de parser l'en-tête de colonne : '{col_label}'")

    mois_abbr, annee_str = match.group(1), match.group(2)
    annee = int(annee_str)

    mois_map = {
        "jan": 'janvier', "fév": 2, "fev": 2, "mar": 3, "avr": 4,
        "mai": 5, "jun": 6, "jui": 6, "jul": 7, "aoû": 8, "aou": 8,
        "sep": 9, "oct": 10, "nov": 11, "déc": 12, "dec": 12,
    }
    mois = mois_map.get(mois_abbr[:3])
    if mois is None:
        raise ValueError(f"Mois non reconnu : '{mois_abbr}'")

    # ── Extraire les divisions et les valeurs ──
    # row[2] contient toutes les divisions + valeurs en multiline (sauf Ensemble)
    data_row  = table[2]
    total_row = table[3]   # ['Ensemble', val_dec, val_jan, ...]

    divisions = [d.strip() for d in data_row[0].split("\n") if d.strip()]
    valeurs   = [v.strip() for v in data_row[2].split("\n") if v.strip()]  # colonne jan.2011

    records = []

    for division, val_str in zip(divisions, valeurs):
        records.append({
            "division_par_produit": division,
            "ipc":   parse_float(val_str),
            "annee": annee,
            "mois":  mois,
        })

    # Ajouter la ligne Ensemble
    records.append({
        "division_par_produit": total_row[0],   # 'Ensemble'
        "ipc":   parse_float(total_row[2]),     # valeur jan.2011
        "annee": annee,
        "mois":  mois,
    })

    return records


def save_csv(records: list[dict], output_path: str) -> None:
    fieldnames = ["division_par_produit", "ipc", "annee", "mois"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


if __name__ == "__main__":
    records = extract_ipc_janvier_2011(INPUT_PDF)

    print(f"{'Division par produit':<60} {'IPC':>8}  {'Année':>6}  {'Mois':>5}")
    print("-" * 85)
    for r in records:
        print(f"{r['division_par_produit']:<60} {r['ipc']:>8.1f}  {r['annee']:>6}  {r['mois']:>5}")

    save_csv(records, OUTPUT_CSV)
    print(f"\n✓ {len(records)} lignes sauvegardées → {OUTPUT_CSV}")