# Madkalorie Estimator med Stort Kaloriedatabase

Denne Streamlit-app estimerer kalorier i mad på et billede ved hjælp af en manuel håndmarkering som reference og en omfattende fødevaredatabase.

## Kom godt i gang

1. Clone eller download dette repo.
2. Installer dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Kør databasenedlaster:
   ```
   python download_db.py
   ```
4. Læg din finetunede model i `models/food_model.pt`.
5. Kør appen:
   ```
   streamlit run app.py
   ```
