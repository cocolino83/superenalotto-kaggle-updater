import pandas as pd
import requests
from bs4 import BeautifulSoup
from kaggle.api.kaggle_api_extended import KaggleApi
import datetime
import os

# === Scarica HTML dal sito ufficiale ===
url = "http://www.estrazionilottooggi.it/superenalotto/Archivio-superenalotto-2025"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

table = soup.find("table")
df_html = pd.read_html(str(table))[0]
df_html.columns = ["N. conc.", "Data estr.", "1°", "2°", "3°", "4°", "5°", "6°", "J", "SS"]
df_html["Data estr."] = pd.to_datetime(df_html["Data estr."], dayfirst=True)

# === Carica dataset esistente ===
if os.path.exists("estrazioni.csv"):
    df_existing = pd.read_csv("estrazioni.csv")
    df_existing["Data estr."] = pd.to_datetime(df_existing["Data estr."], dayfirst=True)
else:
    df_existing = pd.DataFrame(columns=df_html.columns)

# === Confronta e aggiorna ===
ultima_data = df_existing["Data estr."].max() if not df_existing.empty else pd.to_datetime("1997-01-01")
df_nuove = df_html[df_html["Data estr."] > ultima_data]

if not df_nuove.empty:
    df_updated = pd.concat([df_existing, df_nuove], ignore_index=True)
    df_updated.to_html("estrazioni.html", index=False)

    print(f"✅ Aggiornato con {len(df_nuove)} nuove righe")

    # === Aggiorna Kaggle ===
    api = KaggleApi()
    api.authenticate()
    api.dataset_create_version(
        folder=".",
        version_notes=f"Aggiornamento automatico {datetime.datetime.now().strftime('%Y-%m-%d')}",
        dataset="salta1/estrazionedal1997adoggi",
        convert_to_csv=True
    )
else:
    print("⏳ Nessuna nuova estrazione trovata.")
