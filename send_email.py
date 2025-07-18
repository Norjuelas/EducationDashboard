# 1. Importar las librerías necesarias
import streamlit as st
import pandas as pd
import plotly.express as px
import warnings
import os
import google.generativeai as genai
from datetime import datetime

# Ignorar advertencias futuras que puedan surgir de las librerías
warnings.simplefilter(action='ignore', category=FutureWarning)

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Dashboard de Proyecto con IA", page_icon="🚀", layout="wide")

# --- FUNCIONES AUXILIARES ---
def wrap_text(text, length=50):
    """Ajusta el texto a una longitud máxima por línea para el gráfico."""
    if len(text) > length:
        # Usamos <br> para que Plotly lo interprete como un salto de línea
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            if len(current_line + " " + word) <= length:
                current_line += " " + word
            else:
                lines.append(current_line.strip())
                current_line = word
        lines.append(current_line.strip())
        return "<br>".join(lines)
    return text

# --- TÍTULO PRINCIPAL ---
st.title("🚀 Dashboard de Gestión de Proyectos con IA")
st.markdown("Carga tu archivo, interactúa con los datos y gestiona tus tareas en tiempo real.")

# --- OBTENER API KEY Y CONFIGURAR GEMINI ---
# Para usar el chatbot, crea un archivo .env en la misma carpeta del script
# y añade la línea: GEMINI_API_KEY="TU_API_KEY_AQUI"
try:
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
except ImportError:
    api_key = None
    st.sidebar.warning("Instala `python-dotenv` (`pip install python-dotenv`) para cargar la API Key desde un archivo .env", icon="🧩")


# --- INICIALIZACIÓN DE SESSION STATE ---
if 'df' not in st.session_state:
    st.session_state.df = None

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.header("1. Cargar Archivo")
    uploaded_file = st.file_uploader("Selecciona tu archivo Excel (.xlsx)", type=["xlsx"])

    if uploaded_file:
        try:
            df_cargado = pd.read_excel(uploaded_file)
            # Definimos los nombres EXACTOS de las columnas que usaremos
            required_cols = ['Hito/Actividad', 'Fecha de inicio', 'Fecha de fin', 'Etapa', 'Responsable', 'Estado']
            
            # Limpieza de espacios en blanco
            for col in required_cols:
                if col in df_cargado.columns and df_cargado[col].dtype == 'object':
                    df_cargado[col] = df_cargado[col].str.strip()
            
            # Conversión de fechas
            df_cargado['Fecha de inicio'] = pd.to_datetime(df_cargado['Fecha de inicio'], errors='coerce')
            df_cargado['Fecha de fin'] = pd.to_datetime(df_cargado['Fecha de fin'], errors='coerce')
            
            # Añadir columna de notificación si no existe
            if 'Notificación Enviada' not in df_cargado.columns:
                df_cargado['Notificación Enviada'] = False

            st.session_state.df = df_cargado.dropna(subset=['Fecha de inicio', 'Fecha de fin'])
            st.success("Archivo cargado y procesado.", icon="✅")
        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")
            st.session_state.df = None

    if st.session_state.df is not None:
        df_display = st.session_state.df
        st.divider()
        st.header("2. Filtros del Dashboard")
        etapas_unicas = df_display['Etapa'].dropna().unique().tolist()
        responsables_unicos = df_display['Responsable'].dropna().unique().tolist()
        estados_unicos = df_display['Estado'].dropna().unique().tolist()

        selected_etapa = st.selectbox("Filtrar por Etapa:", ["Todas"] + etapas_unicas)
        selected_responsable = st.selectbox("Filtrar por Responsable:", ["Todos"] + responsables_unicos)
        selected_estado = st.selectbox("Filtrar por Estado:", ["Todos"] + estados_unicos)
        
        # Aplicación de filtros
        df_filtrado = df_display.copy()
        if selected_etapa != "Todas":
            df_filtrado = df_filtrado[df_filtrado['Etapa'] == selected_etapa]
        if selected_responsable != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Responsable'] == selected_responsable]
        if selected_estado != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Estado'] == selected_estado]
    else:
        df_filtrado = pd.DataFrame() # Dataframe vacío si no hay nada cargado

    st.divider()
    # --- CHATBOT EN LA BARRA LATERAL ---
    st.header("💬 Asistente IA")
    if not api_key:
        st.warning("Define tu `GEMINI_API_KEY` en un archivo `.env` para activar el chat.", icon="⚠️")
    else:
        model = genai.GenerativeModel('gemini-1.5-flash')
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        if prompt := st.chat_input("Pregúntale a los datos..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("Pensando..."):
                    datos_contexto = df_filtrado.to_markdown(index=False)
                    prompt_completo = f"""Eres un analista de datos experto y amigable. Tu única fuente de información son los siguientes datos extraídos de un dashboard de proyectos. No puedes usar información externa.

**Datos Actuales del Dashboard:**
{datos_contexto}

**Pregunta del Usuario:**
"{prompt}"

Basándote EXCLUSIVAMENTE en la tabla de datos proporcionada, responde a la pregunta del usuario. Si la respuesta no está en los datos, indícalo amablemente."""

                    try:
                        response = model.generate_content(prompt_completo)
                        response_text = response.text
                    except Exception as e:
                        response_text = f"Ocurrió un error al contactar a la IA: {e}"
                    
                    st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})

# --- CUERPO PRINCIPAL ---
if st.session_state.df is None:
    st.info("⬆️ Por favor, carga tu archivo de Excel desde la barra lateral para comenzar.")
    st.stop()

# --- SECCIÓN DE MÉTRICAS CLAVE ---
st.header("📊 Métricas Clave del Proyecto")
if not df_filtrado.empty:
    total_actividades = len(df_filtrado)
    completadas = df_filtrado['Estado'].str.contains("CUMPLIDA", na=False).sum()
    en_curso = df_filtrado[df_filtrado['Estado'] == "A TIEMPO"].shape[0]
    progreso_general = (completadas / total_actividades) * 100 if total_actividades > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Actividades", f"{total_actividades} 📝")
    col2.metric("Actividades Completadas", f"{completadas} ✅")
    col3.metric("Actividades En Curso", f"{en_curso} ⏳")
    st.progress(int(progreso_general), text=f"Progreso General (Actividades Completadas): {progreso_general:.1f}%")
else:
    st.warning("No hay actividades que coincidan con los filtros seleccionados.")

# --- DIAGRAMA DE GANTT ---
st.header("🗓️ Cronograma de Actividades (Gantt)")
if not df_filtrado.empty:
    # Aplicar el ajuste de texto a la columna de actividad para el gráfico
    df_gantt = df_filtrado.copy()
    df_gantt['Actividad_Ajustada'] = df_gantt['Hito/Actividad'].apply(lambda x: wrap_text(x, 60))

    fig = px.timeline(
        df_gantt,
        x_start='Fecha de inicio',
        x_end='Fecha de fin',
        y='Actividad_Ajustada',
        color='Estado',
        title="Cronograma por Estado de Actividad",
        hover_name='Hito/Actividad',
        custom_data=['Responsable', 'Etapa']
    )
    fig.update_yaxes(autorange="reversed", title="Actividad")
    fig.update_xaxes(title="Fecha")
    fig.update_traces(
        hovertemplate="<b>%{hover_name}</b><br><br>" +
                      "<b>Responsable:</b> %{customdata[0]}<br>" +
                      "<b>Etapa:</b> %{customdata[1]}<br>" +
                      "<b>Inicio:</b> %{x[0]|%d-%b-%Y}<br>" +
                      "<b>Fin:</b> %{x[1]|%d-%b-%Y}<extra></extra>"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Selecciona otros filtros para visualizar el diagrama de Gantt.")

# --- TABLA DE DATOS EDITABLE ---
st.header("📋 Gestionar Tareas del Proyecto")
st.markdown("Puedes editar, agregar o eliminar tareas directamente en esta tabla. Los cambios se reflejarán en todo el dashboard.")

edited_df = st.data_editor(
    df_filtrado,
    num_rows="dynamic", # Permite agregar y eliminar filas
    use_container_width=True,
    column_config={
        "Fecha de inicio": st.column_config.DateColumn("Fecha de inicio", format="YYYY-MM-DD"),
        "Fecha de fin": st.column_config.DateColumn("Fecha de fin", format="YYYY-MM-DD"),
        "Notificación Enviada": st.column_config.CheckboxColumn("Notificación Enviada", default=False)
    },
    key="data_editor"
)

# Lógica para actualizar el dataframe principal en session_state con los cambios
if edited_df is not None and not edited_df.equals(df_filtrado):
    # Esto es complejo porque 'edited_df' solo tiene las filas filtradas.
    # Necesitamos una forma de mapear los cambios de vuelta al dataframe original.
    # Una estrategia simple es actualizar st.session_state.df con la tabla editada,
    # pero esto puede perder las filas no filtradas.
    # Por ahora, una solución más segura es mostrar un botón para confirmar los cambios.
    if st.button("Guardar Cambios en la Tabla"):
        # Actualizar el estado de la sesión con los datos editados.
        # Esta es una implementación simple. Una app real requeriría una lógica de fusión más robusta.
        st.session_state.df = pd.concat([st.session_state.df[~st.session_state.df.index.isin(df_filtrado.index)], edited_df])
        st.success("¡Cambios guardados! El dashboard se actualizará.")
        st.rerun()