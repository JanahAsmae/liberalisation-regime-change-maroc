"""
Extraction des données IPC (Indice des Prix à la Consommation)
depuis les fichiers PDF du HCP Maroc.

Structure de sortie : Division par produits | IPC | Annee | Mois (nom en français)
Seul le mois actuel (mois courant) est conservé.
"""

import pdfplumber
import pandas as pd
import os
import re

# Liste des divisions attendues (ordre fixe dans les tableaux)
DIVISIONS = [
    "Produits alimentaires",
    "01 - Produits alimentaires et boissons non alcoolisées",
    "02 - Boissons alcoolisées et tabac",
    "Produits non alimentaires",
    "03 - Articles d'habillements et chaussures",
    "04 - Logements, eau, électricité et autres combustibles",
    "05 - Meubles, articles de ménages et entretien courant du foyer",
    "06 - Santé",
    "07 - Transport",
    "08 - Communication",
    "09 - Loisirs et culture",
    "10 - Enseignement",
    "11 - Restaurants et hôtels",
    "12 - Biens et services divers",
    "Ensemble",
]

# Mapping mois (nom -> numéro)
MOIS_FR = {
    "janvier": 1, "février": 2, "mars": 3, "avril": 4,
    "mai": 5, "juin": 6, "juillet": 7, "août": 8,
    "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12,
}

# Mapping inverse (numéro -> nom) – utile pour le tri
NUM_TO_MOIS = {v: k for k, v in MOIS_FR.items()}


def parse_month_year(text: str):
    """Extrait (mois_num, annee, mois_nom) depuis une chaîne comme 'Mars 2010'."""
    text = text.strip().lower().replace("\n", " ")
    for nom, num in MOIS_FR.items():
        if nom in text:
            match = re.search(r"(\d{4})", text)
            if match:
                return num, int(match.group(1)), nom
    return None, None, None


def parse_float(val: str):
    """Convertit '112,3' ou '-0,1' en float."""
    if val is None:
        return None
    val = val.strip().replace(",", ".")
    try:
        return float(val)
    except ValueError:
        return None


def extract_from_table0_format_a(table):
    """
    Format A : ipc_2010_03 — toutes les lignes sont séparées (une division par ligne).
    Row 0 : labels dans la première cellule (multiline), premier label = 'Divisions de produits' à ignorer
    Row 1 : [None, mois_ref, mois_cur, 'Var %']
    Rows 2..N : [None, val_ref, val_cur, var]
    Seul le mois courant (mois_cur) est conservé.
    """
    header_row = table[1]
    mois_cur_str = header_row[2]  # deuxième mois = mois courant

    mois_cur_num, annee_cur, mois_cur_nom = parse_month_year(mois_cur_str)

    # Labels dans row 0, col 0 (multiline) — ignorer le premier ("Divisions de produits")
    labels_raw = table[0][0]
    all_labels = [l.strip() for l in labels_raw.split("\n") if l.strip()]
    # Sauter le header "Divisions de produits"
    labels = [l for l in all_labels if l != "Divisions de produits"]

    records = []
    data_rows = table[2:]  # skip 2 header rows
    for i, row in enumerate(data_rows):
        if i >= len(labels):
            break
        label = labels[i]
        val_cur = parse_float(row[2])  # colonne 2 = mois courant

        if val_cur is not None and mois_cur_nom:
            records.append({
                "Division par produits": label,
                "ipc": val_cur,
                "annee": annee_cur,
                "mois": mois_cur_nom,
            })
    return records


def extract_from_table0_format_b(table):
    """
    Format B : la plupart des fichiers — les valeurs sont compressées (multiline) dans 3 lignes.
    Row 0 : ['Divisions de produits', 'Indices mensuels', None, None]
    Row 1 : [None, mois_ref, mois_cur, 'Var.%']
    Row 2 : [labels_multiline, vals_ref_multiline, vals_cur_multiline, vars_multiline]
    Row 3 : ['Ensemble', val_ref, val_cur, var]
    Seul le mois courant (mois_cur) est conservé.
    """
    header_row = table[1]
    mois_cur_str = header_row[2]  # deuxième mois = mois courant

    mois_cur_num, annee_cur, mois_cur_nom = parse_month_year(mois_cur_str)

    data_row = table[2]
    labels_raw = data_row[0] or ""
    vals_cur_raw = data_row[2] or ""  # colonne 2 = mois courant

    labels_all = [l.strip() for l in labels_raw.split("\n") if l.strip()]
    labels = [l for l in labels_all if l != "Divisions de produits"]
    vals_cur = [v.strip() for v in vals_cur_raw.split("\n") if v.strip()]

    records = []
    for i, label in enumerate(labels):
        val_cur = parse_float(vals_cur[i]) if i < len(vals_cur) else None

        if val_cur is not None and mois_cur_nom:
            records.append({
                "Division par produits": label,
                "ipc": val_cur,
                "annee": annee_cur,
                "mois": mois_cur_nom,
            })

    # Dernière ligne = Ensemble
    ensemble_row = table[3]
    val_cur_e = parse_float(ensemble_row[2])  # colonne 2 = mois courant
    if val_cur_e is not None and mois_cur_nom:
        records.append({
            "Division par produits": "Ensemble",
            "ipc": val_cur_e,
            "annee": annee_cur,
            "mois": mois_cur_nom,
        })
    return records


def extract_ipc_from_pdf(filepath: str):
    """Extrait les données IPC du premier tableau (tableau mensuel) de la page 2."""
    with pdfplumber.open(filepath) as pdf:
        page = pdf.pages[1]  # page 2 (index 1)
        tables = page.extract_tables()

    if not tables:
        print(f"  [WARN] Aucun tableau trouvé dans {filepath}")
        return []

    table = tables[0]

    # Déterminer le format : Format A si row 1, col 0 est None et row 2, col 0 est None
    # Format B si row 2 contient des valeurs multiline dans col 0
    if len(table) >= 3 and table[2][0] and "\n" in str(table[2][0]):
        return extract_from_table0_format_b(table)
    else:
        return extract_from_table0_format_a(table)


def main():
    input_dir = "data\\raw\\maroc\\inflation\\IPC\\pdfs\\structure4"
    output_dir = "data\\interim\\maroc\\inflation"                     # dossier de sortie unique
    os.makedirs(output_dir, exist_ok=True)             # assure l'existence

    pdf_files = sorted([
        f for f in os.listdir(input_dir)
        if f.startswith("ipc_") and f.endswith(".pdf")
    ])

    all_records = []

    for fname in pdf_files:
        filepath = os.path.join(input_dir, fname)
        print(f"Traitement : {fname}")
        records = extract_ipc_from_pdf(filepath)

        # Sauvegarde individuelle en CSV
        if records:
            df_file = pd.DataFrame(records)
            # Supprimer doublons éventuels intra-fichier
            df_file = df_file.drop_duplicates(subset=["Division par produits", "annee", "mois"])
            # Trier par année et mois (en utilisant le numéro de mois temporaire)
            df_file["mois_num"] = df_file["mois"].map(MOIS_FR)
            df_file = df_file.sort_values(["annee", "mois_num"]).drop(columns=["mois_num"])
            csv_filename = f"{os.path.splitext(fname)[0]}.csv"
            csv_path = os.path.join(output_dir, csv_filename)
            df_file.to_csv(csv_path, index=False, encoding="utf-8-sig")
            print(f"  -> {len(df_file)} enregistrements sauvegardés dans {csv_filename}")

        all_records.extend(records)
        print(f"  -> total extrait : {len(records)} enregistrements")

    # Création du DataFrame consolidé (uniquement pour aperçu)
    if all_records:
        df = pd.DataFrame(all_records, columns=["Division par produits", "ipc", "annee", "mois"])
        # Supprimer les doublons (un même mois peut apparaître dans deux fichiers consécutifs)
        df = df.drop_duplicates(subset=["Division par produits", "annee", "mois"])
        # Trier : ajouter colonne temporaire mois_num pour tri, puis la retirer
        df["mois_num"] = df["mois"].map(MOIS_FR)
        df = df.sort_values(["annee", "mois_num", "Division par produits"]).drop(columns=["mois_num"])
        df = df.reset_index(drop=True)

        print(f"\nTotal lignes consolidées : {len(df)}")
        print(f"\nAperçu (20 premières lignes) :\n{df.head(20).to_string()}")
    else:
        print("Aucune donnée extraite.")

    print(f"\nFichiers CSV disponibles dans : {output_dir}")


if __name__ == "__main__":
    main()