import requests
import pandas as pd

# --------------------------
# Paramètres
# --------------------------

countries = {
    "Morocco": "MAR"
}

indicators = {
    "exports": "NE.EXP.GNFS.CD",
    "imports": "NE.IMP.GNFS.CD"
}

start_year = 2010
end_year = 2024

# --------------------------
# Fonction extraction
# --------------------------

def fetch_worldbank_data(country_code, indicator_code):
    url = f"http://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_code}?format=json&per_page=1000"
    response = requests.get(url)
    data = response.json()

    if len(data) > 1:
        records = data[1]
        df = pd.DataFrame(records)
        df = df[["date", "value"]]
        df = df.rename(columns={"date": "year"})
        df["year"] = df["year"].astype(int)
        df = df[(df["year"] >= start_year) & (df["year"] <= end_year)]
        return df
    else:
        return pd.DataFrame()

# --------------------------
# Extraction complète
# --------------------------

all_data = []

for country_name, country_code in countries.items():
    exports_df = fetch_worldbank_data(country_code, indicators["exports"])
    imports_df = fetch_worldbank_data(country_code, indicators["imports"])

    merged = exports_df.merge(imports_df, on="year", suffixes=("_exports", "_imports"))
    merged["country"] = country_name

    # # Calculs
    # merged["trade_balance"] = merged["value_exports"] - merged["value_imports"]
    # merged["coverage_rate"] = merged["value_exports"] / merged["value_imports"]

    all_data.append(merged)

final_df = pd.concat(all_data)

# Sauvegarde
final_df.to_csv("data/raw/maroc/import et export(ice)/ice_data_2010_2024.csv", index=False)

print("✅ Données commerce extérieur téléchargées et sauvegardées.")