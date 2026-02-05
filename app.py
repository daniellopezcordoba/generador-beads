import streamlit as st
import xml.etree.ElementTree as ET
from PIL import Image, ImageEnhance, ImageOps
from streamlit_cropper import st_cropper

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Generador de Patrones Beads", layout="wide")

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
    hr { margin-top: 1rem; margin-bottom: 1rem; border: 0; border-top: 1px solid rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN DE MEMORIA (Session State) ---
if 'paso' not in st.session_state: st.session_state.paso = 1
if 'img_original' not in st.session_state: st.session_state.img_original = None
if 'img_ajustada' not in st.session_state: st.session_state.img_ajustada = None
if 'img_final_paso1' not in st.session_state: st.session_state.img_final_paso1 = None

# Parámetros de imagen
if 'brillo' not in st.session_state: st.session_state.brillo = 0
if 'contraste' not in st.session_state: st.session_state.contraste = 0
if 'saturacion' not in st.session_state: st.session_state.saturacion = 0
if 'giro' not in st.session_state: st.session_state.giro = 0

# --- NAVEGACIÓN ---
def siguiente(): st.session_state.paso += 1

# --- LÓGICA DE PROCESAMIENTO ---
def procesar_parametros(img):
    if img is None: return None
    # Convertir rango -100/100 a factor de Pillow (0.0 a 2.0, siendo 1.0 el centro)
    b = (st.session_state.brillo + 100) / 100
    c = (st.session_state.contraste + 100) / 100
    s = (st.session_state.saturacion + 100) / 100
    
    img = ImageEnhance.Brightness(img).enhance(b)
    img = ImageEnhance.Contrast(img).enhance(c)
    img = ImageEnhance.Color(img).enhance(s)
    return img

# --- INTERFAZ SUPERIOR ---
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
        # 1. BOTÓN DE CARGA
        archivo = st.file_uploader("Cargar imagen", type=['png', 'jpg', 'jpeg'])
        if archivo:
            # Solo cargamos si es una imagen nueva para no machacar cambios
            img_cargada = Image.open(archivo)
            if st.session_state.img_original is None or archivo.name != st.session_state.get('last_file_name'):
                st.session_state.img_original = img_cargada
                st.session_state.img_ajustada = img_cargada
                st.session_state.img_final_paso1 = img_cargada
                st.session_state.last_file_name = archivo.name
        
        st.divider()
        
        # 2. PARÁMETROS DE IMAGEN
        st.subheader("Parámetros de imagen")
        st.session_state.brillo = st.slider("Brillo", -100, 100, st.session_state.brillo)
        st.session_state.contraste = st.slider("Contraste", -100, 100, st.session_state.contraste)
        st.session_state.saturacion = st.slider("Saturación", -100, 100, st.session_state.saturacion)
        
        if st.button("Restaurar valores"):
            st.session_state.brillo = 0
            st.session_state.contraste = 0
            st.session_state.saturacion = 0
            st.rerun()
            
        if st.checkbox("Opciones avanzadas"):
            st.info("Próximamente: Canales de color y transparencia")
            
        st.divider()
        
        # 3. HERRAMIENTAS DE GIRO Y RECORTE
        st.subheader("Giro y Recorte")
        
        # Giro
        st.session_state.giro = st.slider("Giro (grados)", -180, 180, st.session_state.giro)
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            if st.button("Aplicar Giro"):
                if st.session_state.img_final_paso1:
                    st.session_state.img_final_paso1 = st.session_state.img_final_paso1.rotate(st.session_state.giro, expand=True)
                    st.success("Giro aplicado")
        with col_g2:
            if st.button("Restaurar Giro"):
                st.session_state.giro = 0
                st.rerun()

        # Recorte (El botón de aplicar está implícito en la herramienta de la derecha)
        if st.button("Restaurar Recorte"):
             st.session_state.img_final_paso1 = st.session_state.img_original
             st.rerun()

    # RESUMEN Y NAVEGACIÓN
    st.info(f"**Resumen de parámetros:**\n\n{'Imagen cargada' if st.session_state.img_original else 'Esperando...'}")
    
    c_atras, c_sig = st.columns(2)
    with c_sig:
        st.button("Siguiente ➡️", on_click=siguiente, disabled=(st.session_state.img_original is None), use_container_width=True)

with col_previa:
    if st.session_state.img_original:
        # Aplicamos brillo/contraste/saturación a la imagen base que estamos editando
        img_para_mostrar = procesar_parametros(st.session_state.img_final_paso1)
        
        # Herramienta de recorte interactiva
        # aspect_ratio=None permite libertad total. El componente limita el dibujo a los bordes.
        img_recortada = st_cropper(img_para_mostrar, realtime_update=True, box_color='#FF0000', aspect_ratio=None)
        
        # Los botones de abajo son de control visual
        st.write("")
        b_col1, b_col2, b_col3, b_col4, b_col5 = st.columns([1.5, 1, 1, 1, 1.5])
        with b_col2: st.button("🔍 Zoom")
        with b_col3: st.button("🖐️ Pan")
        with b_col4: st.button("🖼️ Ajustar")
    else:
        st.markdown('<div style="width:100%; height:450px; background-color:#ccc; display:flex; align-items:center; justify-content:center; border-radius:8px;">Sube una imagen para comenzar</div>', unsafe_allow_html=True)
