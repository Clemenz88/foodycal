import pandas as pd

df = pd.read_csv('data/food_calories_full.csv').set_index('food')

def lookup_calories(food, volume_ml):
    try:
        kcal100 = df.loc[food, 'kcal_per_100g']
    except KeyError:
        return None
    return volume_ml * kcal100 / 100
