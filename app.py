import streamlit as st
from PIL import Image
import pandas as pd
from streamlit_cropper import st_cropper
from model_utils import detect_containers, detect_food_items
from volume_estimation import estimate_volume
from calorie_lookup import lookup_calories

st.set_page_config(page_title='Madkalorie Estimator', layout='centered')
st.title('📸 Madkalorie Estimator med Manuel Hand Crop')

# Session state for hand confirmation
if 'hand_px_w' not in st.session_state:
    st.session_state.hand_px_w = None

uploaded = st.file_uploader('Upload billede (.jpg/.png)', type=['jpg','png'])
if uploaded:
    img = Image.open(uploaded).convert('RGB')
    st.image(img, caption='Original billede', use_column_width=True)

    st.write('**Step 1:** Marker din hånd i billedet.')
    box_img = st_cropper(img, realtime_update=True, box_color='#FF0000', aspect_ratio=None)
    if st.button('Bekræft håndmarkering'):
        st.session_state.hand_px_w = box_img.width

if st.session_state.hand_px_w:
    st.success(f"Håndbredde bekræftet: {st.session_state.hand_px_w}px")

    # Detekter containers
    containers = detect_containers(img)
    # Beregn resultater
    results = []
    confidences = []
    for c in containers:
        confidences.append(c['confidence'])
        vol = estimate_volume(st.session_state.hand_px_w, c, st.number_input('Håndbredde i cm', min_value=5.0, max_value=30.0, value=8.5, key='hand_cm'))
        foods = detect_food_items(img, [c])
        for f in foods:
            kcal = lookup_calories(f, vol)
            results.append((f, vol, kcal))

    # Vis resultater om nogen
    if results:
        st.header('Resultater')
        for f, vol, kcal in results:
            st.write(f'- **{f}**: {vol:.0f}ml → **{kcal:.0f}kcal**')
    elif containers and min(confidences) < 0.75:
        st.warning('Lav sikkerhed i genkendelse. Vælg venligst manuelt herunder.')
    else:
        st.error('Ingen beholdere fundet.')

    # Fallback vises kun efter resultater eller lav sikkerhed
    if results or (containers and min(confidences) < 0.75):
        st.write('---')
        df = pd.read_csv('data/food_calories.csv')
        fallback = st.selectbox('Fallback: vælg mad:', ['-- Ingenting --'] + df['food'].tolist())
        fallback_vol = st.slider('Fallback volumen', 10, 1000, 100, key='fallback_vol')
        if fallback != '-- Ingenting --':
            kcal_fb = lookup_calories(fallback, fallback_vol)
            st.info(f'Fallback: {fallback} ({fallback_vol}ml) → ~{kcal_fb:.0f}kcal')
