# Madkalorie Estimator with Manual Hand Crop

Dette er en Streamlit-app, der estimerer kalorier i mad ved at bruge en manuel hånd-crop til kalibrering.

## Kom godt i gang

1. Clone dette repo.
2. Installer dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Læg din finetunede model i `models/food_model.pt`.
4. Kør:
   ```
   streamlit run app.py
   ```

## Workflow

1. Upload billede.
2. Marker din hånd via cropper.
3. App genkender mad-beholdere automatisk.
4. Beregner volumen og kalorier.
