import streamlit as st
import pandas as pd
import pickle
import os
from datetime import datetime

# Ruta local para guardar archivo
database_file = os.path.join(os.path.expanduser("~"), "Downloads", "base_datos.pkl")

# Funciones para guardar/cargar
def guardar_datos(data):
    with open(database_file, 'wb') as f:
        pickle.dump(data, f)

def cargar_datos():
    if os.path.exists(database_file):
        with open(database_file, 'rb') as f:
            return pickle.load(f)
    return None

st.set_page_config(page_title="Control de Vencimiento", layout="wide")
st.title("📦 Control de Vida Útil de Materiales")

# Cargar base si existe
if 'data' not in st.session_state:
    st.session_state['data'] = cargar_datos()

# Subida de archivo
st.header("📤 Cargar archivo Excel")
archivo = st.file_uploader("Selecciona tu archivo Excel (.xlsx)", type="xlsx")

if archivo:
    try:
        df = pd.read_excel(archivo, engine="openpyxl")
        df.columns = df.columns.str.strip()
        df['Material'] = df['Material'].astype(str).str.lower()
        df = df.dropna(subset=['Material', 'vida util minima', 'vida util máxima'])
        df['vida util minima'] = pd.to_numeric(df['vida util minima'], errors='coerce')
        df['vida util máxima'] = pd.to_numeric(df['vida util máxima'], errors='coerce')
        df = df.set_index('Material')
        st.session_state['data'] = df
        guardar_datos(df)
        st.success("✅ Datos cargados y guardados.")
    except Exception as e:
        st.error(f"❌ Error al leer el archivo: {e}")

# Verificación de vencimiento
st.header("🔍 Verificar vida útil del material")
with st.form("verificar_form"):
    material = st.text_input("🔢 Ingresar código de Material").strip().lower()
    fecha_vencimiento = st.date_input("📅 Fecha de vencimiento")
    submit = st.form_submit_button("Verificar")

if submit:
    df = st.session_state.get('data')
    if df is None:
        st.warning("Primero debes cargar un archivo válido.")
    elif material not in df.index:
        st.error("❗ Material no encontrado.")
    else:
        fila = df.loc[material]
        vida_actual = (fecha_vencimiento - datetime.today().date()).days
        minimo = int(fila['vida util minima'])
        maximo = int(fila['vida util máxima'])
        cumple = "✅ Sí" if minimo <= vida_actual <= maximo else "❌ No"

        resultado = pd.DataFrame([{
            "Material": material,
            "Descripción": fila.get("Textobrevedematerial", ""),
            "Cliente": fila.get("Cliente", ""),
            "Vida útil actual (días)": vida_actual,
            "Mínimo permitido": minimo,
            "Máximo permitido": maximo,
            "¿Cumple?": cumple
        }])

        st.dataframe(resultado, use_container_width=True)

# Eliminar datos guardados
st.header("🧹 Eliminar datos guardados")
if st.button("Borrar datos locales"):
    if os.path.exists(database_file):
        os.remove(database_file)
        st.session_state['data'] = None
        st.success("Datos eliminados.")
    else:
        st.info("No hay datos guardados para eliminar.")


