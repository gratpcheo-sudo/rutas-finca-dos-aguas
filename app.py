import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# 1. Configuración de la página
st.set_page_config(page_title="Gestión de Rutas - Finca dos Aguas", layout="wide", page_icon="🚛")
st.title("🚛 Panel Logístico y Gestión de Rutas")

# 2. Cargar los datos
@st.cache_data
def load_data():
    # Cargar el Excel que generamos previamente
    try:
        df = pd.read_excel("datos.xlsx", sheet_name="Base_Segmentada")
        return df
    except FileNotFoundError:
        st.error("No se encontró el archivo Excel. Asegúrate de que esté en la misma carpeta.")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # 3. Barra lateral para filtros
    st.sidebar.header("Filtros de Ruta")
    
    lista_rutas = ["Todas"] + list(df['Ruta Asignada'].dropna().unique())
    ruta_seleccionada = st.sidebar.selectbox("Selecciona una Ruta", lista_rutas)
    
    lista_segmentos = ["Todos"] + list(df['Nivel Socioeconómico (Gentrificación)'].dropna().unique())
    segmento_seleccionado = st.sidebar.selectbox("Filtro por Segmento", lista_segmentos)

    # Aplicar filtros
    df_filtrado = df.copy()
    if ruta_seleccionada != "Todas":
        df_filtrado = df_filtrado[df_filtrado['Ruta Asignada'] == ruta_seleccionada]
    if segmento_seleccionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado['Nivel Socioeconómico (Gentrificación)'] == segmento_seleccionado]

    # 4. Mostrar KPIs del Dashboard
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Clientes en Ruta", len(df_filtrado))
    col2.metric("Clientes Premium (Altos)", len(df_filtrado[df_filtrado['Nivel Socioeconómico (Gentrificación)'] == 'Alto (Premium / Gentrificado)']))
    col3.metric("Rutas Activas", df_filtrado['Ruta Asignada'].nunique())

    # 5. Geocodificación Básica (Convertir Dirección a Coordenadas si no existen)
    st.markdown("### 🗺️ Mapa de Entregas")
    st.info("Nota: Para mayor precisión, se recomienda capturar latitud y longitud directamente en la base de datos.")
    
    # Intentamos geolocalizar de forma sencilla (idealmente tener columnas 'Lat' y 'Lon' en el Excel)
    if 'Lat' not in df_filtrado.columns:
        df_filtrado['Lat'] = None
        df_filtrado['Lon'] = None
        
        # Geocodificador (Uso limitado, en producción es mejor tener las coordenadas en el Excel)
        geolocator = Nominatim(user_agent="finca_dos_aguas_rutas")
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

        # Solo geocodificamos los primeros 10 para no saturar la API en esta demo
        # Para Caracas, agregamos el contexto al string de búsqueda
        st.write("Calculando coordenadas para el mapa...")
        for index, row in df_filtrado.head(20).iterrows():
            if pd.notnull(row['Dirección']):
                try:
                    # Añadir Venezuela para mayor precisión
                    location = geolocator.geocode(f"{row['Dirección']}, Venezuela", timeout=5)
                    if location:
                        df_filtrado.at[index, 'Lat'] = location.latitude
                        df_filtrado.at[index, 'Lon'] = location.longitude
                except:
                    pass

    # 6. Crear el Mapa
    # Centrado en Caracas por defecto (Lat: 10.4806, Lon: -66.9036)
    m = folium.Map(location=[10.4806, -66.9036], zoom_start=12)

    # Definir colores por nivel socioeconómico
    colores = {
        'Alto (Premium / Gentrificado)': 'red',
        'Medio (Comercial / Residencial)': 'orange',
        'Estándar': 'blue'
    }

    # Agregar marcadores
    puntos_agregados = 0
    for idx, row in df_filtrado.dropna(subset=['Lat', 'Lon']).iterrows():
        color_pin = colores.get(row['Nivel Socioeconómico (Gentrificación)'], 'gray')
        folium.Marker(
            [row['Lat'], row['Lon']],
            popup=f"<b>{row['Razón social']}</b><br>{row['Dirección']}<br>Ruta: {row['Ruta Asignada']}",
            tooltip=row['Razón social'],
            icon=folium.Icon(color=color_pin, icon="info-sign"),
        ).add_to(m)
        puntos_agregados += 1

    if puntos_agregados > 0:
        # Mostrar mapa interactivo
        st_folium(m, width=1000, height=500)
    else:
        st.warning("No se pudieron determinar las coordenadas exactas de las direcciones filtradas. Es necesario actualizar el Excel con Lat/Lon.")

    # 7. Tabla de Manifiesto de Despacho
    st.markdown("### 📋 Manifiesto de Despacho (Para el Chofer)")
    st.dataframe(df_filtrado[['Razón social', 'Dirección', 'Phone', 'Ruta Asignada']])
