import streamlit as st
import xml.etree.ElementTree as ET

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Generador de Patrones Beads", layout="wide")

# --- REGLA 3: CARGA COMPLETA DEL XML ---
@st.cache_data
def cargar_paletas():
    tree = ET.parse('PALETA DE COLORES.xml')
    root = tree.getroot()
    paletas = {}
    
    for color in root.findall('Color'):
        tipo = color.get('type')
        if tipo not in paletas:
            paletas[tipo] = []
        
        # Guardamos toda la info del XML
        paletas[tipo].append({
            'name': color.get('name'),
            'r': int(color.get('red')),
            'g': int(color.get('green')),
            'b': int(color.get('blue'))
        })
    return paletas

datos_paletas = cargar_paletas()

# --- ESTILO VISUAL (Color Crema y UI) ---
st.markdown(f"""
    <style>
    .stApp {{
        background-color: #F5F5DC;
    }}
    .sidebar .sidebar-content {{
        background-color: #f0f0d8;
    }}
    /* Estilo para la barra de progreso */
    .progress-container {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 30px;
        padding: 0 50px;
    }}
    .step-circle {{
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background-color: #ccc;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        color: white;
    }}
    .step-active {{
        background-color: #4CAF50;
        box-shadow: 0 0 10px #4CAF50;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE NAVEGACIÓN (PASOS) ---
if 'paso' not in st.session_state:
    st.session_state.paso = 1

def siguiente():
    if st.session_state.paso < 5:
        st.session_state.paso += 1

def atras():
    if st.session_state.paso > 1:
        st.session_state.paso -= 1

# --- BARRA DE PROGRESO SUPERIOR ---
cols = st.columns(5)
for i in range(1, 6):
    with cols[i-1]:
        clase = "step-active" if st.session_state.paso >= i else ""
        st.markdown(f'<div class="step-circle {clase}">{i}</div>', unsafe_allow_html=True)

st.divider()

# --- DISEÑO DE DOS COLUMNAS (Menú lateral y Previsualización) ---
col_menu, col_previa = st.columns([1, 2])

with col_menu:
    st.header(f"Paso {st.session_state.paso}")
    
    # Contenido según el paso
    if st.session_state.paso == 1:
        st.subheader("Carga de Imagen")
        st.file_uploader("Sube tu imagen aquí", type=['png', 'jpg', 'jpeg'])
        
    elif st.session_state.paso == 2:
        st.subheader("Configuración de Placas")
        st.number_input("Número de placas horizontales", min_value=1, value=1)
        st.number_input("Número de placas verticales", min_value=1, value=1)
        
    elif st.session_state.paso == 3:
        st.subheader("Selección de Colores")
        opcion_paleta = st.selectbox("Elige tu paleta", list(datos_paletas.keys()))
        
    elif st.session_state.paso == 4:
        st.subheader("Limpieza y Ajustes")
        st.slider("Tolerancia de color (%)", 0.0, 5.0, 0.3)
        
    elif st.session_state.paso == 5:
        st.subheader("Generar PDF")
        st.button("Descargar Patrón PDF")

    # Resumen de parámetros (Ventana de texto)
    st.info("**Resumen de parámetros:**\n\nAquí aparecerá la configuración que vayas eligiendo.")

    # Botones de navegación
    c1, c2 = st.columns(2)
    with c1:
        st.button("Atrás", on_click=atras, disabled=(st.session_state.paso == 1))
    with c2:
        st.button("Siguiente", on_click=siguiente, disabled=(st.session_state.paso == 5))

with col_previa:
    st.subheader("Ventana de Previsualización")
    st.write("Aquí verás los cambios en tiempo real.")
    # Espacio para las herramientas de Zoom/Pan
    st.button("🔍 Zoom")
    st.button("🖐️ Pan")
    st.button("🖼️ Ajustar")
    
    # Cuadro gris que simula la imagen
    st.markdown('<div style="width:100%; height:400px; background-color:#ddd; display:flex; align-items:center; justify-content:center;">La imagen aparecerá aquí</div>', unsafe_allow_html=True)
