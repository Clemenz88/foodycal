import pandas as pd
import requests
import os

DOB_URL = 'https://static.openfoodfacts.org/data/en.openfoodfacts.org.products.csv'

os.makedirs('data', exist_ok=True)
print("Downloader Open Food Facts-database (kan tage mange minutter)...")
r = requests.get(DOB_URL, stream=True)
path_raw = 'data/full_food_db.csv'
with open(path_raw, 'wb') as f:
    for chunk in r.iter_content(chunk_size=10_000_000):
        f.write(chunk)
print("Download færdig, behandler fil...")

df = pd.read_csv(path_raw, usecols=['product_name','energy-kcal_100g'], 
                 dtype={'product_name': str, 'energy-kcal_100g': float})
df = df.dropna().drop_duplicates(subset='product_name')
df.rename(columns={'product_name':'food','energy-kcal_100g':'kcal_per_100g'}, inplace=True)
out = 'data/food_calories_full.csv'
df.to_csv(out, index=False)
print(f"Færdig! Fil gemt som {out} (n={len(df)} entries)")

