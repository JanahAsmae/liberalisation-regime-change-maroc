import requests
import pandas as pd

countries = {
    "Morocco": "MAR"
}

indicators = {
    "reserves_usd": "FI.RES.TOTL.CD",
    "reserves_months": "FI.RES.TOTL.MO"
}

start_year = 2010
end_year = 2025

def fetch_data(country_code, indicator):
    url = f"http://api.worldbank.org/v2/country/{country_code}/indicator/{indicator}?format=json&per_page=1000"
    response = requests.get(url)
    data = response.json()

    if len(data) > 1:
        df = pd.DataFrame(data[1])
        df = df[["date", "value"]]
        df = df.rename(columns={"date": "year"})
        df["year"] = df["year"].astype(int)
        df = df[(df["year"] >= start_year) & (df["year"] <= end_year)]
        return df
    return pd.DataFrame()

all_data = []

for name, code in countries.items():
    reserves = fetch_data(code, indicators["reserves_usd"])
    months = fetch_data(code, indicators["reserves_months"])

    merged = reserves.merge(months, on="year", how="left", suffixes=("_usd", "_months"))
    merged["country"] = name

    all_data.append(merged)

final_df = pd.concat(all_data)
final_df.to_csv("data/raw/maroc/Réserves de change/reserves_data_2010_2025.csv", index=False)

print("✅ Réserves téléchargées.")