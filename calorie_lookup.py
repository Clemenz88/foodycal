import pandas as pd

df_cal = pd.read_csv('data/food_calories.csv').set_index('food')

def lookup_calories(food_name: str, volume_ml: float, density_g_per_ml=1.0):
    mass_g = volume_ml * density_g_per_ml
    try:
        kcal_per_100g = df_cal.loc[food_name, 'kcal_per_100g']
    except KeyError:
        return None
    return mass_g * kcal_per_100g / 100
