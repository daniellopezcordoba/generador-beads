import streamlit as st
import xml.etree.ElementTree as ET
from PIL import Image
from streamlit_cropper import st_cropper

# --- CONFIGURACIÓN Y CARGA (Igual que antes) ---
st.set_page_config(page_title="Generador de Patrones Beads", layout="wide")

@st.cache_data
def cargar_paletas():
    try:
        tree = ET.parse('PALETA DE COLORES.xml')
        root = tree.getroot()
        paletas = {}
        for color in root.findall('Color'):
            tipo = color.get('type')
            if tipo not in paletas: paletas[tipo] = []
            paletas[tipo].append({
                'name': color.get('name'),
                'r': int(color.get('red')), 'g': int(color.get('green')), 'b': int(color.get('blue'))
            })
        return paletas
    except: return {}

datos_paletas = cargar_paletas()

# --- ESTILOS ---
st.markdown("""
    <style>
    .stApp { background-color: #F5F5DC; }
    .step-circle {
        width: 45px; height: 45px; border-radius: 50%;
        background-color: #d1d1b8; display: flex;
        align-items: center; justify-content: center;
        font-weight: bold; font-size: 18px; color: white;
        margin: 0 auto; border: 2px solid #b5b59a;
    }
    .step-active { background-color: #4CAF50; border-color: #388E3C; }
    </style>
    """, unsafe_allow_html=True)

# --- NAVEGACIÓN ---
if 'paso' not in st.session_state: st.session_state.paso = 1
if 'imagen_original' not in st.session_state: st.session_state.imagen_original = None
if 'imagen_recortada' not in st.session_state: st.session_state.imagen_recortada = None

def siguiente(): st.session_state.paso += 1
def atras(): st.session_state.paso -= 1

# --- INTERFAZ ---
cols_progreso = st.columns(5)
for i in range(1, 6):
    with cols_progreso[i-1]:
        clase = "step-active" if st.session_state.paso >= i else ""
        st.markdown(f'<div class="step-circle {clase}">{i}</div>', unsafe_allow_html=True)

st.divider()

col_menu, col_previa = st.columns([1, 2])

with col_menu:
    st.header(f"PASO {st.session_state.paso}")
    
    if st.session_state.paso == 1:
        st.subheader("Carga de Imagen")
        archivo = st.file_uploader("Sube tu imagen", type=['png', 'jpg', 'jpeg'])
        if archivo:
            st.session_state.imagen_original = Image.open(archivo)
            st.success("Imagen cargada. Ajusta los bordes a la derecha.")
        
    elif st.session_state.paso == 2:
        st.subheader("Configuración de Placas")
        st.write("Aquí ajustaremos el tamaño final.")

    # Resumen y Botones
    st.info(f"**Resumen:** {'Imagen lista' if st.session_state.imagen_original else 'Esperando imagen...'}")
    
    c1, c2 = st.columns(2)
    with c1: st.button("⬅️ Atrás", on_click=atras, disabled=(st.session_state.paso == 1), use_container_width=True)
    with c2: st.button("Siguiente ➡️", on_click=siguiente, disabled=(st.session_state.paso == 5 or not st.session_state.imagen_original), use_container_width=True)

with col_previa:
    if st.session_state.paso == 1 and st.session_state.imagen_original:
        st.subheader("Recorta tu imagen")
        # Aquí aparece la herramienta de mover bordes
        img_recortada = st_cropper(st.session_state.imagen_original, realtime_update=True, box_color='#FF0000', aspect_ratio=None)
        st.session_state.imagen_recortada = img_recortada
    else:
        st.subheader("Previsualización")
        st.markdown('<div style="width:100%; height:400px; background-color:#ccc; border-radius:8px; display:flex; align-items:center; justify-content:center;">Sube una imagen para empezar</div>', unsafe_allow_html=True)
    
    # Botones de control
    st.write("")
    b_col1, b_col2, b_col3, b_col4, b_col5 = st.columns([1.5, 1, 1, 1, 1.5])
    with b_col2: st.button("🔍 Zoom")
    with b_col3: st.button("🖐️ Pan")
    with b_col4: st.button("🖼️ Ajustar")
