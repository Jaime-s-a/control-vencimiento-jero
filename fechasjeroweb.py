import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Control de Vencimiento", layout="wide")

st.title("📦 Aplicación de Control de Vencimiento")

# Subida del archivo Excel
uploaded_file = st.file_uploader("Cargar archivo Excel (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        # Leer y procesar el archivo Excel
        data = pd.read_excel(uploaded_file, engine='openpyxl')
        data.columns = data.columns.str.strip()  # Limpiar espacios en nombres de columnas
        data['Material'] = data['Material'].astype(str).str.strip().str.lower()
        data = data.dropna(subset=['Material', 'vida util minima', 'vida util máxima'])

        # Convertir columnas de vida útil a numéricas
        data['vida util minima'] = pd.to_numeric(data['vida util minima'], errors='coerce')
        data['vida util máxima'] = pd.to_numeric(data['vida util máxima'], errors='coerce')

        # Usar 'Material' como índice
        data.set_index('Material', inplace=True)

        st.success("✅ Archivo cargado correctamente.")

        # Formulario para ingresar datos del usuario
        with st.form("verificacion_form"):
            st.subheader("🔍 Verificar Fecha de Vencimiento")
            material_input = st.text_input("Material").strip().lower()
            fecha_input = st.date_input("Fecha de vencimiento", format="DD/MM/YYYY")
            submitted = st.form_submit_button("Verificar")

            if submitted:
                if material_input in data.index:
                    producto = data.loc[material_input]
                    vida_util_minima = int(producto['vida util minima'])
                    vida_util_maxima = int(producto['vida util máxima'])
                    descripcion = producto.get('Textobrevedematerial', 'N/A')
                    cliente = producto.get('Cliente', 'N/A')

                    fecha_actual = datetime.today().date()
                    vida_util_actual = (fecha_input - fecha_actual).days
                    cumple = "✅ Sí" if vida_util_minima <= vida_util_actual <= vida_util_maxima else "❌ No"

                    # Mostrar tabla con resultado
                    resultado = pd.DataFrame([{
                        "Material": material_input,
                        "Descripción": descripcion,
                        "Cliente": cliente,
                        "Vida útil mínima (días)": vida_util_minima,
                        "Vida útil máxima (días)": vida_util_maxima,
                        "Vida útil actual (días)": vida_util_actual,
                        "¿Cumple requisitos?": cumple
                    }])

                    st.write("### 📋 Resultado")
                    st.dataframe(resultado, use_container_width=True)
                else:
                    st.error("🚫 El material no se encuentra en la base de datos.")
    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")
else:
    st.info("📁 Por favor, carga un archivo Excel para comenzar.")

