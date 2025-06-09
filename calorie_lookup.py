import pandas as pd
import os

_full_db = None

def _load_db():
    """
    Indlæs én gang:
    - hvis full_db findes i data/, brug den
    - ellers brug den lille fallback CSV
    """
    global _full_db
    if _full_db is None:
        full_path = 'data/food_calories_full.csv'
        if os.path.exists(full_path):
            _full_db = pd.read_csv(full_path).set_index('food')
        else:
            # Fallback til lille DB
            small_path = 'data/food_calories.csv'
            _full_db = pd.read_csv(small_path).set_index('food')
    return _full_db

def lookup_calories(food: str, volume_ml: float) -> float | None:
    """
    Giver kalorier for 'food' givet volume_ml (ml ~ gram).
    Returnerer None, hvis fødevaren ikke findes i DB.
    """
    df = _load_db()
    try:
        # Antager at kolonnen med kcal/100g hedder den første kolonne
        kcal_per_100g = df.iloc[:, 0].loc[food]
    except KeyError:
        return None
    # volume_ml * (kcal_per_100g / 100g)
    return volume_ml * kcal_per_100g / 100
