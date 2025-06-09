import pandas as pd

df = pd.read_csv('data/food_calories.csv').set_index('food')

def lookup_calories(food, volume_ml):
    g = volume_ml  # assume density=1
    try:
        kcal100 = df.loc[food, 'kcal_per_100g']
    except KeyError:
        return None
    return g * kcal100 / 100
