import streamlit as st
from PIL import Image
import pandas as pd
from streamlit_cropper import st_cropper
from model_utils import detect_containers, detect_food_items
from volume_estimation import estimate_volume
from calorie_lookup import lookup_calories

st.set_page_config(page_title='Madkalorie Estimator', layout='centered')
st.title('📸 Madkalorie Estimator med Stort Kaloriedatabase')

if 'hand_px_w' not in st.session_state:
    st.session_state.hand_px_w = None
if 'manual_entries' not in st.session_state:
    st.session_state.manual_entries = []

uploaded = st.file_uploader('Upload billede (.jpg/.png)', type=['jpg','png'])
if uploaded:
    img = Image.open(uploaded).convert('RGB')
    st.image(img, use_container_width=True)
    st.write('**Step 1: Marker din hånd**')
    crop_img = st_cropper(img, realtime_update=True, box_color='#FF0000')
    if st.button('Bekræft håndmarkering'):
        st.session_state.hand_px_w = crop_img.width

if st.session_state.hand_px_w and uploaded:
    hand_px = st.session_state.hand_px_w
    st.success(f'Håndbredde: {hand_px}px')
    hand_cm = st.number_input('Håndbredde i cm', 5.0, 30.0, 8.5)

    containers = detect_containers(img)
    results = []
    confs = [c['confidence'] for c in containers]
    if containers:
        for c in containers:
            vol = estimate_volume(hand_px, c, hand_cm)
            foods = detect_food_items(img, [c])
            for f in foods:
                kcal = lookup_calories(f['name'], vol) or 0
                results.append({'food': f['name'], 'food_conf': f['confidence'],
                                'volume_ml': vol, 'volume_conf': c['confidence'],
                                'calories': kcal})
        st.header('Resultater')
        for r in results:
            st.write(f"- **{r['food']}**: {r['volume_ml']:.0f} ml "
                     f"(vol-sikkerhed: {r['volume_conf']*100:.0f}%, "
                     f"mad-sikkerhed: {r['food_conf']*100:.0f}%) → **{r['calories']:.0f} kcal**")
    if containers and min(confs) < 0.75 or not containers:
        st.warning('Lav genkendelse, brug fallback nedenfor.')

    if st.button('Gå til fallback'):
        st.write('---')
        df_cal = pd.read_csv('data/food_calories_full.csv')
        choice = st.selectbox('Søg eller vælg madvare', df_cal['food'].tolist())
        vol = st.number_input('Volume/vægt (ml/gram)', 1, 5000, 100)
        if st.button('Tilføj madvare til manuel liste'):
            kcal = lookup_calories(choice, vol) or 0
            st.session_state.manual_entries.append((choice, vol, kcal))
        if st.session_state.manual_entries:
            st.subheader('Manuelle indtastninger')
            for food, v, k in st.session_state.manual_entries:
                st.write(f"- **{food}**: {v} ml → **{k:.0f} kcal**")
