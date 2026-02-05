import streamlit as st
import xml.etree.ElementTree as ET
from PIL import Image, ImageEnhance
from streamlit_cropper import st_cropper

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Generador de Patrones Beads", layout="wide")

# --- ESTILOS CSS PARA INTERFAZ FIJA Y LÍNEA DE PROGRESO ---
st.markdown("""
    <style>
    .stApp { background-color: #F5F5DC; }
    
    /* Contenedor fijo para la derecha (Previsualización) */
    [data-testid="stVerticalBlock"] > div:nth-child(2) [data-testid="stVerticalBlock"] {
        position: sticky;
        top: 2rem;
    }

    /* Línea de progreso con unión */
    .progress-wrapper {
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: relative;
        margin-bottom: 2rem;
        padding: 0 10%;
    }
    .progress-line {
        position: absolute;
        top: 50%;
        left: 10%;
        right: 10%;
        height: 4px;
        background-color: #d1d1b8;
        z-index: 1;
    }
    .progress-line-fill {
        position: absolute;
        top: 50%;
        left: 10%;
        height: 4px;
        background-color: #4CAF50;
        z-index: 2;
        transition: width 0.3s;
    }
    .step-circle {
        width: 45px; height: 45px; border-radius: 50%;
        background-color: #d1d1b8; display: flex;
        align-items: center; justify-content: center;
        font-weight: bold; color: white;
        position: relative; z-index: 3;
        border: 2px solid #b5b59a;
    }
    .step-active { background-color: #4CAF50; border-color: #388E3C; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN DE VARIABLES ---
if 'paso' not in st.session_state: st.session_state.paso = 1
if 'img_original' not in st.session_state: st.session_state.img_original = None
if 'img_editada' not in st.session_state: st.session_state.img_editada = None
if 'modo_recorte' not in st.session_state: st.session_state.modo_recorte = False

# Parámetros iniciales
if 'brillo' not in st.session_state: st.session_state.brillo = 0
if 'contraste' not in st.session_state: st.session_state.contraste = 0
if 'saturacion' not in st.session_state: st.session_state.saturacion = 0
if 'giro' not in st.session_state: st.session_state.giro = 0

# --- FUNCIONES DE ACCIÓN ---
def restaurar_parametros():
    st.session_state.brillo = 0
    st.session_state.contraste = 0
    st.session_state.saturacion = 0

def aplicar_recorte():
    if 'temp_crop' in st.session_state:
        st.session_state.img_editada = st.session_state.temp_crop
        st.session_state.modo_recorte = False

# --- BARRA DE PROGRESO SUPERIOR ---
fill_width = (st.session_state.paso - 1) * 20  # Calcula el llenado de la línea
st.markdown(f"""
    <div class="progress-wrapper">
        <div class="progress-line"></div>
        <div class="progress-line-fill" style="width: {fill_width + 10}%;"></div>
        <div class="step-circle {'step-active' if st.session_state.paso >= 1 else ''}">1</div>
        <div class="step-circle {'step-active' if st.session_state.paso >= 2 else ''}">2</div>
        <div class="step-circle {'step-active' if st.session_state.paso >= 3 else ''}">3</div>
        <div class="step-circle {'step-active' if st.session_state.paso >= 4 else ''}">4</div>
        <div class="step-circle {'step-active' if st.session_state.paso >= 5 else ''}">5</div>
    </div>
    """, unsafe_allow_html=True)

col_menu, col_previa = st.columns([1, 2])

# --- COLUMNA IZQUIERDA (MENÚ) ---
with col_menu:
    # Pestaña desplegable (Persiana) del Paso 1
    with st.expander("PASO 1. CARGA DE IMAGEN", expanded=(st.session_state.paso == 1)):
        
        # 1. Botón de carga
        archivo = st.file_uploader("Cargar imagen", type=['png', 'jpg', 'jpeg'])
        if archivo and st.session_state.img_original is None:
            st.session_state.img_original = Image.open(archivo)
            st.session_state.img_editada = st.session_state.img_original

        st.divider()

        # 2. Parámetros de imagen
        st.write("**Parámetros de imagen**")
        st.session_state.brillo = st.slider("Brillo", -100, 100, st.session_state.brillo, key="sld_brillo")
        st.session_state.contraste = st.slider("Contraste", -100, 100, st.session_state.contraste, key="sld_contraste")
        st.session_state.saturacion = st.slider("Saturación", -100, 100, st.session_state.saturacion, key="sld_saturacion")
        
        st.button("Restaurar valores", on_click=restaurar_parametros)
        
        st.divider()

        # 3. Giro y Recorte
        st.write("**Giro y Recorte**")
        st.session_state.giro = st.slider("Giro (grados)", -180, 180, st.session_state.giro)
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("Recorte"):
                st.session_state.modo_recorte = True
        with col_btn2:
            if st.button("Restaurar Imagen"):
                st.session_state.img_editada = st.session_state.img_original
                st.session_state.giro = 0
                st.session_state.modo_recorte = False

        if st.session_state.modo_recorte:
            st.button("✅ Aplicar recorte", on_click=aplicar_recorte, type="primary")

    # VENTANA FIJA DE RESUMEN (Abajo del menú)
    st.markdown("<br><br>", unsafe_allow_html=True)
    with st.container():
        st.info("**Resumen de parámetros utilizados:**\n\nImagen cargada")
        
        c_at, c_sig = st.columns(2)
        with c_sig:
            st.button("Siguiente ➡️", on_click=lambda: setattr(st.session_state, 'paso', st.session_state.paso + 1), 
                      disabled=(st.session_state.img_original is None))

# --- COLUMNA DERECHA (PREVISUALIZACIÓN FIJA) ---
with col_previa:
    st.subheader("Ventana de Previsualización")
    
    if st.session_state.img_editada:
        # Procesar imagen con brillo/contraste/saturación/giro en tiempo real
        img_temp = st.session_state.img_editada
        
        # Aplicar giro en tiempo real
        if st.session_state.giro != 0:
            img_temp = img_temp.rotate(st.session_state.giro, expand=True)
            
        # Aplicar parámetros de imagen
        b = (st.session_state.brillo + 100) / 100
        c = (st.session_state.contraste + 100) / 100
        s = (st.session_state.saturacion + 100) / 100
        img_temp = ImageEnhance.Brightness(img_temp).enhance(b)
        img_temp = ImageEnhance.Contrast(img_temp).enhance(c)
        img_temp = ImageEnhance.Color(img_temp).enhance(s)

        if st.session_state.modo_recorte:
            # Mostrar herramienta de recorte
            cropped_img = st_cropper(img_temp, realtime_update=True, box_color='#FF0000', aspect_ratio=None)
            st.session_state.temp_crop = cropped_img
        else:
            # Mostrar imagen final procesada
            st.image(img_temp, use_container_width=True)
    else:
        st.markdown('<div style="width:100%; height:450px; background-color:#ccc; border-radius:8px; display:flex; align-items:center; justify-content:center;">Imagen no cargada</div>', unsafe_allow_html=True)

    # Botones de Zoom/Pan (Visuales)
    st.write("")
    b_col1, b_col2, b_col3, b_col4, b_col5 = st.columns([1.5, 1, 1, 1, 1.5])
    with b_col2: st.button("🔍 Zoom")
    with b_col3: st.button("🖐️ Pan")
    with b_col4: st.button("🖼️ Ajustar")
