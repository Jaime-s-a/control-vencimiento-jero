import streamlit as st
import pandas as pd
from datetime import datetime
import os
import pickle
import threading

# Ruta del archivo de la base de datos
database_file = os.path.join(os.path.expanduser("~"), "Downloads", "base_de_datos.pkl")

# Cargar los datos de la base de datos guardada
def cargar_base_de_datos():
    if os.path.exists(database_file):
        try:
            with open(database_file, "rb") as file:
                data = pickle.load(file)
            return data
        except Exception as e:
            st.error(f"Hubo un error al cargar la base de datos guardada: {e}")
    return None

# Guardar la base de datos
def guardar_base_de_datos(data):
    try:
        with open(database_file, "wb") as file:
            pickle.dump(data, file)
        st.info(f"Base de datos guardada correctamente en {database_file}.")
    except Exception as e:
        st.error(f"Hubo un error al guardar la base de datos: {e}")

# Cargar archivo XLSX
def cargar_xlsx():
    uploaded_file = st.file_uploader("Cargar archivo XLSX", type=["xlsx"])
    if uploaded_file is not None:
        try:
            data = pd.read_excel(uploaded_file, engine='openpyxl')

            # Limpiar nombres de las columnas
            data.columns = data.columns.str.strip()

            # Asegurarse de que las columnas sean adecuadas
            data['Material'] = data['Material'].astype(str).str.strip().str.lower()
            data = data.dropna(subset=['Material', 'vida util minima', 'vida util máxima'])
            data['vida util minima'] = pd.to_numeric(data['vida util minima'], errors='coerce')
            data['vida util máxima'] = pd.to_numeric(data['vida util máxima'], errors='coerce')

            # Guardar base de datos
            guardar_base_de_datos(data)

            st.success("Datos importados correctamente.")
            return data
        except Exception as e:
            st.error(f"Hubo un error al cargar los datos: {e}")
    return None

# Función para verificar vencimiento
def verificar_vencimiento(data, material_usuario, fecha_vencimiento_input):
    if data is None:
        st.error("Por favor, carga primero un archivo XLSX.")
        return

    material_usuario = material_usuario.strip().lower()

    if not material_usuario:
        st.error("Por favor, ingresa un material válido.")
        return

    try:
        # Convertir la fecha de vencimiento
        fecha_vencimiento = datetime.strptime(fecha_vencimiento_input, '%d-%m-%Y')

        # Buscar el material
        if material_usuario in data.index:
            producto = data.loc[material_usuario]

            # Extraer los valores relevantes
            vida_util_minima = producto['vida util minima']
            vida_util_maxima = producto['vida util máxima']
            descripcion = producto['Textobrevedematerial']
            cliente = producto['Cliente']

            # Obtener la fecha actual (hoy)
            fecha_actual = datetime.today()

            # Calcular la vida útil actual (días)
            vida_util_actual = (fecha_vencimiento - fecha_actual).days

            # Verificar si la vida útil actual está dentro del rango
            if vida_util_minima <= vida_util_actual <= vida_util_maxima:
                cumple = "Sí"
            else:
                cumple = "No"

            resultado = f"El Material {material_usuario} {descripcion} {cumple} \nCumple para ser despachado a {cliente}"
            st.success(resultado)
        else:
            st.error(f"Material {material_usuario} no encontrado.")
    except ValueError:
        st.error("La fecha de vencimiento no tiene el formato correcto. Debe ser DD-MM-YYYY.")

# Función principal para Streamlit
def main():
    st.title("Aplicación de Control de Vencimiento")

    # Cargar los datos guardados
    data = cargar_base_de_datos()

    # Botón para cargar archivo XLSX
    if st.button("Cargar XLSX"):
        data = cargar_xlsx()

    # Ingresar material y fecha de vencimiento
    material_usuario = st.text_input("Material:")
    fecha_vencimiento_input = st.text_input("Fecha de Vencimiento (DD-MM-YYYY):")

    # Botón para verificar vencimiento
    if st.button("Verificar Vencimiento"):
        if material_usuario and fecha_vencimiento_input:
            verificar_vencimiento(data, material_usuario, fecha_vencimiento_input)

    # Botón para borrar datos
    if st.button("Borrar Datos"):
        st.empty()

if __name__ == "__main__":
    main()
