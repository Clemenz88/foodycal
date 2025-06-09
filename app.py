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

# Efter håndbekræftelse
if st.session_state.hand_px_w:
    hand_px = st.session_state.hand_px_w
    st.success(f"Håndbredde bekræftet: {hand_px}px")
    hand_cm = st.number_input('Håndbredde i cm', min_value=5.0, max_value=30.0, value=8.5)

    # Detect containers
    containers = detect_containers(img)
    results = []
    container_confs = [c['confidence'] for c in containers]

    # Beregn resultater for each container
    for c in containers:
        vol = estimate_volume(hand_px, c, hand_cm)
        foods = detect_food_items(img, [c])
        for f in foods:
            kcal = lookup_calories(f['name'], vol)
            results.append({
                'food': f['name'],
                'food_conf': f['confidence'],
                'volume_ml': vol,
                'volume_conf': c['confidence'],
                'calories': kcal or 0
            })

    # Vis resultater
    if results:
        st.header('Resultater')
        for r in results:
            st.write(f"- **{r['food']}**: {r['volume_ml']:.0f} ml (sikkerhed: {r['volume_conf']*100:.0f}%), "
                     f"madgenkendelse: {r['food_conf']*100:.0f}% → **{r['calories']:.0f} kcal**")
    elif containers and min(container_confs) < 0.75:
        st.warning('Lav sikkerhed i genkendelse (<75%). Overvej at bruge fallback nedenfor.')
    else:
        st.error('Ingen beholdere fundet.')

    # Fallback: kun vis hvis resultater eller lav sikkerhed
    if results or (containers and min(container_confs) < 0.75):
        st.write('---')
        df = pd.read_csv('data/food_calories.csv')
        options = df['food'].tolist()
        manual = st.multiselect('Fallback: søg eller vælg madvarer manuelt', options)
        manual_entries = []
        for food in manual:
            vol = st.number_input(f'Volume/vægt for {food} (ml/gram)', min_value=1, max_value=5000, value=100, key=f'vol_{food}')
            kcal = lookup_calories(food, vol)
            manual_entries.append((food, vol, kcal))
        if manual_entries:
            st.subheader('Manuelle indtastninger')
            for food, vol, kcal in manual_entries:
                st.write(f"- **{food}**: {vol} ml → **{kcal:.0f} kcal**")
