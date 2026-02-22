import requests
import pandas as pd

# --------------------------
# Paramètres
# --------------------------

countries = {
    "Morocco": "MAR"
}

indicators = {
    "fdi_usd": "BX.KLT.DINV.CD.WD",
    "fdi_percent_gdp": "BX.KLT.DINV.WD.GD.ZS"
}

start_year = 2010
end_year = 2025

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
    fdi_usd_df = fetch_worldbank_data(country_code, indicators["fdi_usd"])
    fdi_percent_df = fetch_worldbank_data(country_code, indicators["fdi_percent_gdp"])

    merged = fdi_usd_df.merge(fdi_percent_df, on="year", suffixes=("_usd", "_percent_gdp"))
    merged["country"] = country_name

    # Calcul variation annuelle %
    merged["fdi_growth_rate"] = merged["value_usd"].pct_change() * 100

    all_data.append(merged)

final_df = pd.concat(all_data)

# Sauvegarde
final_df.to_csv("data/raw/maroc/investissement_etrangers(ide)/ide_global_data_2010_2025.csv", index=False)

print("✅ Données IDE téléchargées et sauvegardées.")