import pandas as pd
import os

_full_db = None

def _load_db():
    global _full_db
    if _full_db is None:
        full_path = 'data/food_calories_full.csv'
        if os.path.exists(full_path):
            df = pd.read_csv(full_path)
        else:
            df = pd.read_csv('data/food_calories.csv')
        df.set_index('food', inplace=True)
        _full_db = df
    return _full_db

def lookup_calories(food: str, volume_ml: float) -> float | None:
    """
    Returnerer kalorier for en given fødevare ved volumen i ml (ml ~ gram).
    """
    df = _load_db()
    try:
        kcal_per_100g = df.loc[food, 'kcal_per_100g']
    except KeyError:
        return None
    return volume_ml * kcal_per_100g / 100

def get_food_list() -> list:
    """
    Returnerer en liste af alle fødevarer i databasen.
    """
    df = _load_db()
    return df.index.tolist()
