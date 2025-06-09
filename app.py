import streamlit as st
from PIL import Image
import pandas as pd
from streamlit_cropper import st_cropper
from model_utils import detect_containers, detect_food_items
from volume_estimation import estimate_volume
from calorie_lookup import lookup_calories, get_food_list

st.set_page_config(page_title='Madkalorie Estimator', layout='centered')
st.title('📸 Madkalorie Estimator med Manuel Hand Crop')

# Initialize session state
if 'hand_px_w' not in st.session_state:
    st.session_state.hand_px_w = None
if 'manual_entries' not in st.session_state:
    st.session_state.manual_entries = []

# Upload image
uploaded = st.file_uploader('Upload billede (.jpg/.png)', type=['jpg','png'])
if uploaded:
    img = Image.open(uploaded).convert('RGB')
    st.image(img, caption='Original billede', use_container_width=True)
    st.write('**Step 1: Marker din hånd**')
    crop_img = st_cropper(img, realtime_update=True, box_color='#FF0000')
    if st.button('Bekræft håndmarkering'):
        st.session_state.hand_px_w = crop_img.width

# After hand confirmation
if st.session_state.hand_px_w and uploaded:
    hand_px = st.session_state.hand_px_w
    st.success(f'Håndbredde bekræftet: {hand_px}px')
    hand_cm = st.number_input('Håndbredde i cm', min_value=5.0, max_value=30.0, value=8.5)

    # Detect containers and foods
    containers = detect_containers(img)
    results = []
    container_confs = [c['confidence'] for c in containers] if containers else []

    for c in containers:
        vol = estimate_volume(hand_px, c, hand_cm)
        foods = detect_food_items(img, [c])
        for f in foods:
            kcal = lookup_calories(f['name'], vol) or 0
            results.append({
                'food': f['name'],
                'food_conf': f['confidence'],
                'volume_ml': vol,
                'volume_conf': c['confidence'],
                'calories': kcal
            })

    # Display model predictions regardless of confidence
    if results:
        st.header('Model Forudsigelser')
        for r in results:
            st.write(f"- **{r['food']}**: {r['volume_ml']:.0f} ml "
                     f"(container-sikkerhed: {r['volume_conf']*100:.0f}%, "
                     f"mad-sikkerhed: {r['food_conf']*100:.0f}%) → **{r['calories']:.0f} kcal**")
    else:
        st.warning('Ingen forudsigelser fra modellen.')

    # Show warning for low confidence
    if containers and container_confs and min(container_confs) < 0.75:
        st.warning('Lav sikkerhed i container-genkendelse (<75%).')

    # Fallback section: always available after predictions or low confidence
    if results or (containers and container_confs and min(container_confs) < 0.75):
        st.write('---')
        st.subheader('Fallback: Søg og vælg eller tilføj manuelt')

        # Get full list of foods
        all_foods = get_food_list()
        choice = st.selectbox('Søg eller vælg madvare', all_foods)
        vol = st.number_input('Volume/vægt (ml/gram)', min_value=1, max_value=5000, value=100, key='vol_fallback')
        if st.button('Tilføj madvare til manuel liste'):
            kcal = lookup_calories(choice, vol) or 0
            st.session_state.manual_entries.append((choice, vol, kcal))
            st.success(f'Tilføjet {choice}')

        if st.session_state.manual_entries:
            st.subheader('Manuelle indtastninger')
            for food, v, k in st.session_state.manual_entries:
                st.write(f"- **{food}**: {v} ml → **{k:.0f} kcal**")
