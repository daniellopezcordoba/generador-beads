import streamlit as st
import xml.etree.ElementTree as ET
from PIL import Image, ImageEnhance
from streamlit_cropper import st_cropper

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Generador de Patrones Beads", layout="wide")

# --- ESTILOS CSS (Interfaz fija, Barra de progreso y Menú con Scroll) ---
st.markdown("""
    <style>
    .stApp { background-color: #F5F5DC; }
    
    /* Línea de progreso superior */
    .progress-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: relative;
        margin: 20px 10% 40px 10%;
    }
    .progress-line {
        position: absolute;
        top: 50%; left: 0; right: 0;
        height: 4px; background-color: #d1d1b8;
        z-index: 1; transform: translateY(-50%);
    }
    .progress-line-fill {
        position: absolute;
        top: 50%; left: 0;
        height: 4px; background-color: #4CAF50;
        z-index: 2; transform: translateY(-50%);
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

    /* Layout Fijo (Sticky) */
    .sticky-container {
        position: -webkit-sticky;
        position: sticky;
        top: 20px;
    }
    
    /* Scroll para el menú lateral si crece mucho */
    .scrollable-menu {
        max-height: 70vh;
        overflow-y: auto;
        padding-right: 10px;
        border-right: 1px solid #e6e6e6;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN DE ESTADOS ---
if 'paso' not in st.session_state: st.session_state.paso = 1
if 'img_original' not in st.session_state: st.session_state.img_original = None
if 'img_recortada' not in st.session_state: st.session_state.img_recortada = None
if 'modo_recorte' not in st.session_state: st.session_state.modo_recorte = False

# Parámetros (Cajones separados)
if 'brillo' not in st.session_state: st.session_state.brillo = 0
if 'contraste' not in st.session_state: st.session_state.contraste = 0
if 'saturacion' not in st.session_state: st.session_state.saturacion = 0
if 'giro' not in st.session_state: st.session_state.giro = 0

# --- FUNCIONES DE RESTAURACIÓN INDEPENDIENTE ---
def restaurar_slides():
    st.session_state.brillo = 0
    st.session_state.contraste = 0
    st.session_state.saturacion = 0

def restaurar_giro():
    st.session_state.giro = 0

def restaurar_recorte():
    st.session_state.img_recortada = None
    st.session_state.modo_recorte = False

# --- BARRA DE PROGRESO ---
progreso = (st.session_state.paso - 1) * 25 # 0, 25, 50, 75, 100
st.markdown(f"""
    <div class="progress-container">
        <div class="progress-line"></div>
        <div class="progress-line-fill" style="width: {progreso}%;"></div>
        <div class="step-circle {'step-active' if st.session_state.paso >= 1 else ''}">1</div>
        <div class="step-circle {'step-active' if st.session_state.paso >= 2 else ''}">2</div>
        <div class="step-circle {'step-active' if st.session_state.paso >= 3 else ''}">3</div>
        <div class="step-circle {'step-active' if st.session_state.paso >= 4 else ''}">4</div>
        <div class="step-circle {'step-active' if st.session_state.paso >= 5 else ''}">5</div>
    </div>
    """, unsafe_allow_html=True)

col_menu, col_previa = st.columns([1, 2])

# --- COLUMNA IZQUIERDA: MENÚ ---
with col_menu:
    st.markdown('<div class="scrollable-menu">', unsafe_allow_html=True)
    
    with st.expander("PASO 1. CARGA DE IMAGEN", expanded=(st.session_state.paso == 1)):
        # 1. Carga
        archivo = st.file_uploader("Cargar imagen", type=['png', 'jpg', 'jpeg'])
        if archivo:
            st.session_state.img_original = Image.open(archivo)
        
        st.divider()
        
        # 2. Parámetros
        st.write("**Parámetros de imagen**")
        st.session_state.brillo = st.slider("Brillo", -100, 100, st.session_state.brillo)
        st.session_state.contraste = st.slider("Contraste", -100, 100, st.session_state.contraste)
        st.session_state.saturacion = st.slider("Saturación", -100, 100, st.session_state.saturacion)
        st.button("Restaurar valores", on_click=restaurar_slides, key="res_slides")
        
        if st.checkbox("Opciones avanzadas"):
            st.write("Canales RGB (Próximamente)")
            
        st.divider()
        
        # 3. Giro y Recorte
        st.write("**Giro y Recorte**")
        st.session_state.giro = st.slider("Giro (grados)", -180, 180, st.session_state.giro)
        st.button("Restaurar Giro", on_click=restaurar_giro)
        
        st.write("")
        c_rec1, c_rec2 = st.columns(2)
        with c_rec1:
            if st.button("Recorte", use_container_width=True):
                st.session_state.modo_recorte = True
        with c_rec2:
            st.button("Restaurar Recorte", on_click=restaurar_recorte, use_container_width=True)
            
        if st.session_state.modo_recorte:
            if st.button("✅ Aplicar recorte", type="primary", use_container_width=True):
                st.session_state.img_recortada = st.session_state.temp_crop
                st.session_state.modo_recorte = False
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # Ventana de Resumen y Navegación (Sticky inferior del menú)
    st.markdown('<div class="sticky-container">', unsafe_allow_html=True)
    st.info("**Resumen de parámetros utilizados:**\n\nImagen cargada")
    st.button("Siguiente ➡️", on_click=lambda: setattr(st.session_state, 'paso', 2), 
              disabled=(st.session_state.img_original is None), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- COLUMNA DERECHA: PREVISUALIZACIÓN ---
with col_previa:
    st.markdown('<div class="sticky-container">', unsafe_allow_html=True)
    st.subheader("Ventana de Previsualización")
    
    if st.session_state.img_original:
        # 1. Partimos de la imagen (recortada o original)
        base = st.session_state.img_recortada if st.session_state.img_recortada else st.session_state.img_original
        
        # 2. Aplicamos Giro
        if st.session_state.giro != 0:
            base = base.rotate(st.session_state.giro, expand=True)
            
        # 3. Aplicamos Sliders
        b = (st.session_state.brillo + 100) / 100
        c = (st.session_state.contraste + 100) / 100
        s = (st.session_state.saturacion + 100) / 100
        img_final = ImageEnhance.Brightness(base).enhance(b)
        img_final = ImageEnhance.Contrast(img_final).enhance(c)
        img_final = ImageEnhance.Color(img_final).enhance(s)

        if st.session_state.modo_recorte:
            # En modo recorte usamos la imagen con filtros y giro para ver qué recortamos
            st.session_state.temp_crop = st_cropper(img_final, realtime_update=True, box_color='#FF0000', aspect_ratio=None)
        else:
            st.image(img_final, use_container_width=True)
            
        # Botones de control inferiores
        st.write("")
        b_col1, b_col2, b_col3, b_col4, b_col5 = st.columns([1, 1, 1, 1, 1])
        with b_col2: st.button("🔍 Zoom")
        with b_col3: st.button("🖐️ Pan")
        with b_col4: st.button("🖼️ Ajustar")
    else:
        st.markdown('<div style="width:100%; height:400px; background-color:#ccc; display:flex; align-items:center; justify-content:center; border-radius:8px;">Sin imagen</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
