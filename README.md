# Madkalorie Estimator

Denne Streamlit-app estimerer kalorier i mad på et billede ved hjælp af din hånd som reference.

## Kom godt i gang

1. Download eller clone dette repository.
2. Sørg for at have Python 3.8+ installeret.
3. Installer dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Læg din finetunede YOLO-model i `models/food_model.pt`.
5. Start appen:
   ```
   streamlit run app.py
   ```

## Filoversigt

- `app.py`: Hoved-Streamlit-applikationen
- `model_utils.py`: Objekt- og hånddetektion
- `volume_estimation.py`: Volumenestimering
- `calorie_lookup.py`: Kalorieopslag
- `data/food_calories.csv`: Kaloriedatabase
- `models/food_model.pt`: Din tilpassede madgenkendelsesmodel
