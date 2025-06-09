import streamlit as st
from PIL import Image
import pandas as pd
from model_utils import detect_objects, detect_food_items
from volume_estimation import estimate_volume
from calorie_lookup import lookup_calories

st.set_page_config(page_title="Madkalorie Estimator", layout="centered")
st.title("📸 Madkalorie‐estimator med hånd‐reference")

uploaded_file = st.file_uploader("Upload et billede (.jpg/.png) med din hånd som reference", type=["jpg","png"])
hand_size = st.number_input("Håndbredde i cm (mål tværs over knoerne)", min_value=5.0, max_value=30.0, value=8.5, step=0.1)

df_cal = pd.read_csv("data/food_calories.csv")
fallback_opts = ["-- Ingenting --"] + df_cal["food"].tolist()
fallback = st.selectbox("Fallback: vælg madvare manuelt", fallback_opts)
fallback_vol = st.slider("Volume/vægt for fallback (ml/gram)", min_value=10, max_value=1000, value=100)

if uploaded_file:
    img = Image.open(uploaded_file).convert("RGB")
    st.image(img, caption="Uploaded billede", use_column_width=True)

    detections = detect_objects(img)
    hand_boxes = [d for d in detections if d["name"] == "hand"]
    if not hand_boxes:
        st.error("Kunne ikke genkende hånden. Sørg for, at hånden er synlig.")
    else:
        hand_box = hand_boxes[0]
        container_boxes = [d for d in detections if d["name"] in ["bowl","cup","plate"]]
        results = []
        for box in container_boxes:
            vol = estimate_volume(hand_box, box, hand_size)
            foods = detect_food_items(img, [box])
            for food in foods:
                kcal = lookup_calories(food, vol)
                results.append((food, vol, kcal))
        if results:
            st.header("Resultater")
            for food, vol, kcal in results:
                st.write(f"- **{food}**: {vol:.0f} ml → ca. **{kcal:.0f} kcal**")
        else:
            st.warning("Ingen mad genkendt. Brug fallback nedenfor.")

if fallback != "-- Ingenting --":
    kcal_fb = lookup_calories(fallback, fallback_vol)
    st.info(f"Fallback: **{fallback}** ({fallback_vol} ml) → ca. **{kcal_fb:.0f} kcal**")
