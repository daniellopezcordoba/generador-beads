import streamlit as st
import xml.etree.ElementTree as ET

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Generador de Patrones Beads", layout="wide")

# --- REGLA 3: CARGA COMPLETA DEL XML (Sin omitir ni optimizar) ---
@st.cache_data
def cargar_paletas():
    try:
        tree = ET.parse('PALETA DE COLORES.xml')
        root = tree.getroot()
        paletas = {}
        
        # Leemos cada color del XML con toda su información original
        for color in root.findall('Color'):
            tipo = color.get('type')
            if tipo not in paletas:
                paletas[tipo] = []
            
            paletas[tipo].append({
                'name': color.get('name'),
                'r': int(color.get('red')),
                'g': int(color.get('green')),
                'b': int(color.get('blue'))
            })
        return paletas
    except Exception as e:
        return {}

datos_paletas = cargar_paletas()

# --- ESTILO VISUAL (Color Crema y UI) ---
st.markdown(f"""
    <style>
    /* Color de fondo crema para toda la aplicación */
    .stApp {{
        background-color: #F5F5DC;
    }}
    
    /* Estilo de los círculos de la barra de progreso */
    .step-circle {{
        width: 45px;
        height: 45px;
        border-radius: 50%;
        background-color: #d1d1b8;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 18px;
        color: white;
        margin: 0 auto;
        border: 2px solid #b5b59a;
    }}
    .step-active {{
        background-color: #4CAF50;
        border-color: #388E3C;
        box-shadow: 0 0 10px rgba(76, 175, 80, 0.6);
    }}
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE NAVEGACIÓN ---
if 'paso' not in st.session_state:
    st.session_state.paso = 1

def siguiente():
    if st.session_state.paso < 5:
        st.session_state.paso += 1

def atras():
    if st.session_state.paso > 1:
        st.session_state.paso -= 1

# --- BARRA DE PROGRESO SUPERIOR ---
cols_progreso = st.columns(5)
for i in range(1, 6):
    with cols_progreso[i-1]:
        # Si el paso actual es mayor o igual al círculo, se pone verde
        clase = "step-active" if st.session_state.paso >= i else ""
        st.markdown(f'<div class="step-circle {clase}">{i}</div>', unsafe_allow_html=True)

st.divider()

# --- DISEÑO PRINCIPAL (Menú Lateral y Previsualización) ---
col_menu, col_previa = st.columns([1, 2])

# IZQUIERDA: Menú de opciones
with col_menu:
    st.header(f"PASO {st.session_state.paso}")
    
    if st.session_state.paso == 1:
        st.subheader("Carga de Imagen")
        st.file_uploader("Sube tu imagen", type=['png', 'jpg', 'jpeg'])
        
    elif st.session_state.paso == 2:
        st.subheader("Configuración de Placas")
        st.number_input("Placas Horizontales (29x29)", min_value=1, value=1)
        st.number_input("Placas Verticales (29x29)", min_value=1, value=1)
        
    elif st.session_state.paso == 3:
        st.subheader("Selección de Colores")
        if datos_paletas:
            st.selectbox("Elige tu paleta", list(datos_paletas.keys()))
        
    elif st.session_state.paso == 4:
        st.subheader("Limpieza y Ajustes")
        st.slider("Tolerancia de color (%)", 0.0, 5.0, 0.3)
        
    elif st.session_state.paso == 5:
        st.subheader("Generar PDF")
        st.text_input("Título del patrón", value="Mi Proyecto")

    # Ventana de Resumen de Parámetros
    st.info("**Resumen de parámetros:**\n\nAquí aparecerá la configuración seleccionada.")

    # Botones de navegación (Atrás y Siguiente)
    nav_c1, nav_c2 = st.columns(2)
    with nav_c1:
        st.button("⬅️ Atrás", on_click=atras, disabled=(st.session_state.paso == 1), use_container_width=True)
    with nav_c2:
        st.button("Siguiente ➡️", on_click=siguiente, disabled=(st.session_state.paso == 5), use_container_width=True)

# DERECHA: Ventana de Previsualización
with col_previa:
    st.subheader("Previsualización del Patrón")
    
    # Cuadro gris que representa la imagen
    st.markdown("""
        <div style="width:100%; height:450px; background-color:#cccccc; border: 2px solid #999; display:flex; align-items:center; justify-content:center; border-radius:8px;">
            <p style="color:#555; font-weight:bold;">LA IMAGEN SE MOSTRARÁ AQUÍ</p>
        </div>
    """, unsafe_allow_html=True)
    
    # BOTONES DE CONTROL (Zoom, Pan, Ajustar) alineados y centrados debajo
    st.write("") # Pequeño espacio
    # Creamos 5 columnas para que las 3 del centro contengan los botones y queden centradas
    b_col1, b_col2, b_col3, b_col4, b_col5 = st.columns([1.5, 1, 1, 1, 1.5])
    
    with b_col2:
        st.button("🔍 Zoom", use_container_width=True)
    with b_col3:
        st.button("🖐️ Pan", use_container_width=True)
    with b_col4:
        st.button("🖼️ Ajustar", use_container_width=True)
