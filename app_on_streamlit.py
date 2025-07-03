import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np
import google.generativeai as genai
import os
from dotenv import load_dotenv

# --- Cargar variables de entorno desde el archivo .env ---
load_dotenv()

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA Y ESTILO
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard Integral de Programas",
    page_icon="🌌",
    layout="wide"
)

# --- CSS FUTURISTA ---
def aplicar_estilo_futurista():
    estilo = """
    <style>
    .stApp { background-color: #0E1117; }
    .stPlotlyChart { border-radius: 15px; padding: 10px; background: linear-gradient(145deg, #1e2229, #181c22); box-shadow:  5px 5px 10px #0a0c0f, -5px -5px 10px #282c35; }
    h1, h2, h3 { color: #00F2FF; text-shadow: 0 0 5px #00F2FF; }
    .stMarkdown, .stDataFrame, .stSelectbox, .stMultiSelect { color: #FAFAFA; }
    </style>
    """
    st.markdown(estilo, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# LÓGICA DE DATOS Y GRÁFICOS (Sin cambios)
# -----------------------------------------------------------------------------
# Las funciones crear_datos_simulados(), calcular_estado_actividad(), y 
# crear_grafico_prediccion() se mantienen exactamente igual que en la versión anterior.
# (Se omiten aquí por brevedad, pero deben estar en tu archivo .py)
def crear_datos_simulados():
    hoy = datetime.now()
    datos = {
        'Programa': ['Colombia Programa', 'Colombia Programa', 'Ciberpaz', 'Ciberpaz', 'Smartfilms', 'Smartfilms', 'Legado de Gabo', 'Ministerio General'],
        'Actividad': ['Implementación Componente 1', 'Implementación Componente 2', 'Inducción equipo Ciberpaz', 'Sensibilización en Rock al Parque', 'Taller de capacitación', 'Desarrollo del taller', 'Pesquisas mensuales', 'Visita a maestras'],
        'Fecha Inicio': [(hoy - timedelta(days=60)), (hoy - timedelta(days=45)), (hoy - timedelta(days=30)), (hoy - timedelta(days=10)), (hoy - timedelta(days=90)), (hoy - timedelta(days=20)), (hoy - timedelta(days=120)), (hoy - timedelta(days=70))],
        'Fecha Límite': [(hoy + timedelta(days=60)), (hoy + timedelta(days=90)), (hoy + timedelta(days=5)), (hoy + timedelta(days=2)), (hoy + timedelta(days=10)), (hoy + timedelta(days=45)), (hoy + timedelta(days=100)), (hoy + timedelta(days=30))],
        'Porcentaje Ejecución': [55.0, 30.0, 95.0, 10.0, 100.0, 5.0, 35.0, 80.0]
    }
    df = pd.DataFrame(datos)
    df['Fecha Inicio'] = pd.to_datetime(df['Fecha Inicio'].apply(lambda x: x.strftime('%Y-%m-%d')))
    df['Fecha Límite'] = pd.to_datetime(df['Fecha Límite'].apply(lambda x: x.strftime('%Y-%m-%d')))
    return df

def calcular_estado_actividad(df):
    hoy = pd.to_datetime(datetime.now().date())
    df['Duración Total'] = (df['Fecha Límite'] - df['Fecha Inicio']).dt.days
    df['Días Transcurridos'] = (hoy - df['Fecha Inicio']).dt.days.clip(0)
    df['Progreso Esperado'] = (df['Días Transcurridos'] / df['Duración Total']) * 100
    df['Progreso Esperado'] = df['Progreso Esperado'].clip(0, 100)
    df.loc[hoy > df['Fecha Límite'], 'Progreso Esperado'] = 100
    df['Diferencia'] = df['Porcentaje Ejecución'] - df['Progreso Esperado']
    condiciones = [ (df['Diferencia'] >= -5), (df['Diferencia'] > -20) & (df['Diferencia'] < -5), (df['Diferencia'] <= -20) ]
    estados = ['Verde', 'Amarillo', 'Rojo']
    colores_map = {'Verde': '#39FF14', 'Amarillo': '#FFFF00', 'Rojo': '#FF00E6'}
    df['Estado'] = pd.Series(pd.Categorical(np.select(condiciones, estados, default='Verde'), categories=estados, ordered=True))
    df['Color'] = df['Estado'].map(colores_map)
    return df

def crear_grafico_prediccion(actividad_data):
    hoy = pd.to_datetime(datetime.now().date())
    fecha_inicio = actividad_data['Fecha Inicio'].iloc[0]
    fecha_limite = actividad_data['Fecha Límite'].iloc[0]
    progreso_actual = actividad_data['Porcentaje Ejecución'].iloc[0]
    dias_transcurridos = (hoy - fecha_inicio).days
    if dias_transcurridos <= 0:
        return None
    velocidad = progreso_actual / dias_transcurridos
    progreso_proyectado = progreso_actual + (velocidad * (fecha_limite - hoy).days)
    progreso_final = min(progreso_proyectado, 120) 
    ruta_ideal = pd.DataFrame({'Fecha': [fecha_inicio, fecha_limite], 'Progreso': [0, 100]})
    ruta_real = pd.DataFrame({'Fecha': [fecha_inicio, hoy], 'Progreso': [0, progreso_actual]})
    ruta_proyectada = pd.DataFrame({'Fecha': [hoy, fecha_limite], 'Progreso': [progreso_actual, progreso_final]})
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ruta_ideal['Fecha'], y=ruta_ideal['Progreso'], mode='lines', name='Ruta Ideal', line=dict(color='#39FF14', width=2)))
    fig.add_trace(go.Scatter(x=ruta_real['Fecha'], y=ruta_real['Progreso'], mode='lines', name='Progreso Real', line=dict(color='#00F2FF', width=4)))
    fig.add_trace(go.Scatter(x=ruta_proyectada['Fecha'], y=ruta_proyectada['Progreso'], mode='lines', name='Proyección', line=dict(color='#FF00E6', width=2, dash='dash')))
    fig.add_trace(go.Scatter(x=[hoy], y=[progreso_actual], mode='markers', name='Hoy', marker=dict(color='#00F2FF', size=12, line=dict(width=2, color='white'))))
    fig.update_layout(title=f"Predicción para: {actividad_data['Actividad'].iloc[0]}", xaxis_title="Tiempo", yaxis_title="Avance (%)", yaxis_range=[0, max(110, progreso_final * 1.1)], template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    return fig

# -----------------------------------------------------------------------------
# INICIO DEL DASHBOARD
# -----------------------------------------------------------------------------
aplicar_estilo_futurista()

# --- Obtener API Key y configurar Gemini ---
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# --- BARRA LATERAL (SIDEBAR) ---
st.sidebar.header("Filtros del Dashboard")
df_original = crear_datos_simulados()
df_procesado = calcular_estado_actividad(df_original.copy())
programa_seleccionado = st.sidebar.multiselect('Programa:', options=df_procesado['Programa'].unique(), default=df_procesado['Programa'].unique())
estado_seleccionado = st.sidebar.multiselect('Estado (Semáforo):', options=df_procesado['Estado'].unique(), default=df_procesado['Estado'].unique())
df_filtrado = df_procesado[(df_procesado['Programa'].isin(programa_seleccionado)) & (df_procesado['Estado'].isin(estado_seleccionado))]

st.sidebar.divider()

# --- CHATBOT EN LA BARRA LATERAL ---
st.sidebar.header("💬 Asistente IA")
if not api_key:
    st.sidebar.warning("Define tu GEMINI_API_KEY en un archivo .env para activar el chat.", icon="⚠️")
else:
    model = genai.GenerativeModel('gemini-1.5-flash')
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mostrar historial (en la sidebar)
    for message in st.session_state.messages:
        with st.sidebar.chat_message(message["role"]):
            st.sidebar.markdown(message["content"])
    
    # Input del usuario (en la sidebar)
    if prompt := st.sidebar.chat_input("Pregúntale a los datos..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        datos_contexto = df_filtrado.to_markdown(index=False)
        prompt_completo = f"Eres un analista de datos experto. Basándote EXCLUSIVAMENTE en los siguientes datos del dashboard:\n\n{datos_contexto}\n\nResponde a la pregunta: \"{prompt}\""

        try:
            response = model.generate_content(prompt_completo)
            response_text = response.text
        except Exception as e:
            response_text = f"Ocurrió un error: {e}"
            
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        st.rerun() # Recargar para mostrar el nuevo mensaje

# --- CUERPO PRINCIPAL DEL DASHBOARD ---
st.title("🌌 Dashboard Integral de Seguimiento de Programas")

if df_filtrado.empty:
    st.warning("No hay datos que coincidan con los filtros seleccionados.")
else:
    # SECCIÓN 1: Resumen de Estado
    st.header("🚦 Resumen General del Estado")
    conteo_estados = df_filtrado['Estado'].value_counts()
    fig_dona = go.Figure(data=[go.Pie(labels=conteo_estados.index, values=conteo_estados.values, hole=.7, marker_colors=[df_filtrado['Color'].unique()[i] for i in range(len(conteo_estados.index))], textinfo='label+percent', insidetextorientation='radial')])
    fig_dona.update_layout(showlegend=False, height=350, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_dona, use_container_width=True)
    st.divider()

    # SECCIÓN 2: Diagrama de Gantt
    st.header("🗓️ Cronograma de Proyectos (Diagrama de Gantt)")
    fig_gantt = px.timeline(df_filtrado, x_start="Fecha Inicio", x_end="Fecha Límite", y="Actividad", color="Programa", title="Línea de Tiempo por Actividad", template="plotly_dark")
    fig_gantt.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    fig_gantt.update_yaxes(categoryorder='total ascending')
    st.plotly_chart(fig_gantt, use_container_width=True)
    st.divider()

    # SECCIÓN 3: Análisis de Rendimiento
    st.header("📊 Análisis de Avance vs. Retraso")
    df_filtrado_sorted = df_filtrado.sort_values(by='Diferencia', ascending=True)
    fig_barras = px.bar(df_filtrado_sorted, x='Diferencia', y='Actividad', orientation='h', color='Estado', color_discrete_map={'Verde': '#39FF14', 'Amarillo': '#FFFF00', 'Rojo': '#FF00E6'}, title='Diferencia entre Progreso Real y Esperado (%)', template="plotly_dark")
    fig_barras.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_barras, use_container_width=True)
    st.divider()

    # SECCIÓN 4: Motor de Predicción
    st.header("🔮 Motor de Predicción de Evolución")
    actividades_disponibles = df_filtrado['Actividad'].tolist()
    actividad_seleccionada = st.selectbox('Selecciona una Actividad para la Predicción:', options=actividades_disponibles)
    if actividad_seleccionada:
        datos_actividad = df_filtrado[df_filtrado['Actividad'] == actividad_seleccionada]
        figura_prediccion = crear_grafico_prediccion(datos_actividad)
        if figura_prediccion:
            st.plotly_chart(figura_prediccion, use_container_width=True)