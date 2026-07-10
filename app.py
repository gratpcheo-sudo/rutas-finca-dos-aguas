import streamlit as st
import pandas as pd
import os

# 1. Configuración de la página
st.set_page_config(page_title="Gestión de Rutas - Finca dos Aguas", layout="centered")
st.title("🚛 Panel Logístico y Gestión de Rutas")

# 2. Cargar y limpiar datos
@st.cache_data
def load_data():
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_archivo = os.path.join(directorio_actual, "datos.xlsx")
    
    # Leemos el Excel
    df = pd.read_excel(ruta_archivo, sheet_name="Base_Segmentada")
    
    # Limpiamos espacios en los nombres de las columnas para evitar errores
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# 3. Administración (Editor de Rutas)
st.sidebar.header("Administración")
password = st.sidebar.text_input("Clave de Administrador", type="password")

if password == "1234":  # Cambia '1234' por tu clave
    st.sidebar.success("Modo Edición Activado")
    st.subheader("Editor de Base de Datos")
    df_editado = st.data_editor(df, num_rows="dynamic")
    
    if st.button("Guardar Cambios en Excel"):
        df_editado.to_excel("datos.xlsx", index=False, sheet_name="Base_Segmentada")
        st.success("¡Base de datos actualizada!")
        st.rerun()
else:
    # 4. Vista para el Usuario (Chofer/Vendedor)
    st.subheader("Selección de Ruta")
    lista_rutas = ["Todas"] + list(df['Ruta Asignada'].unique())
    ruta_seleccionada = st.selectbox("Selecciona la Ruta a trabajar:", lista_rutas)
    
    if ruta_seleccionada == "Todas":
        df_filtrado = df
    else:
        df_filtrado = df[df['Ruta Asignada'] == ruta_seleccionada]
    
    st.write(f"### Clientes en ruta: {len(df_filtrado)}")
    
    # 5. Visualización de clientes
    for index, row in df_filtrado.iterrows():
        with st.expander(f"{row['Razón social']}"):
            st.write(f"📍 **Dirección:** {row['Dirección']}")
            st.write(f"🚚 **Ruta:** {row['Ruta Asignada']}")
            st.write(f"👤 **Vendedor:** {row['Usuario / Vendedor Asignado']}")
            st.write(f"🌍 **Zonificación:** {row['Zonificación Geográfica']}")
