import requests
import pandas as pd

countries = {
    "Morocco": "MAR"
}

indicators = {
    "gdp_usd": "NY.GDP.MKTP.CD",
    "gdp_growth": "NY.GDP.MKTP.KD.ZG",
    "gdp_per_capita": "NY.GDP.PCAP.CD",
    "current_account": "BN.CAB.XOKA.GD.ZS"
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
    dfs = []

    for key, indicator in indicators.items():
        df = fetch_data(code, indicator)
        df = df.rename(columns={"value": key})
        dfs.append(df)

    merged = dfs[0]
    for df in dfs[1:]:
        merged = merged.merge(df, on="year", how="left")

    merged["country"] = name
    all_data.append(merged)

final_df = pd.concat(all_data)
final_df.to_csv("data/raw/maroc/Macroeconomic control/macro_control_data_2010_2025.csv", index=False)

print("✅ Données macroéconomiques téléchargées.")