import streamlit as st
import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime
import pandas as pd
#import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(
    page_title="Monitor de Sensor MQTT",
    page_icon="📊",
    layout="wide"
)

# Inicialización de variables en session state
if 'data' not in st.session_state:
    st.session_state.data = []
if 'last_update' not in st.session_state:
    st.session_state.last_update = None

# Configuración MQTT
MQTT_BROKER = "broker.mqttdashboard.com"  # Cambia esto según tu broker
MQTT_PORT = 1883
MQTT_TOPIC = "sensor_st"  # Cambia esto según tu tópico

# Callback cuando se recibe un mensaje
def on_message(client, userdata, message):
    try:
        # Decodificar el mensaje JSON
        payload = json.loads(message.payload.decode())
        
        # Agregar timestamp
        payload['timestamp'] = datetime.now().strftime('%H:%M:%S')
        
        # Actualizar datos
        st.session_state.data.append(payload)
        if len(st.session_state.data) > 50:  # Mantener solo últimos 50 registros
            st.session_state.data.pop(0)
        
        st.session_state.last_update = time.time()
    except Exception as e:
        st.error(f"Error procesando mensaje: {e}")

# Configurar cliente MQTT
client = mqtt.Client()
client.on_message = on_message

# Función para crear la gráfica
def create_sensor_plot(df):
    fig = go.Figure()
    
    # Agregar línea de datos
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['value'],
            mode='lines+markers',
            name='Valor del Sensor',
            line=dict(color='#1f77b4', width=2),
            marker=dict(size=6)
        )
    )
    
    # Personalizar el diseño
    fig.update_layout(
        title={
            'text': 'Valores del Sensor en el Tiempo',
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title='Tiempo',
        yaxis_title='Valor del Sensor',
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#f0f0f0'
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#f0f0f0'
        )
    )
    
    return fig

# Interfaz de usuario
st.title("📊 Monitor de Sensor en Tiempo Real")

# Placeholder para el contenido actualizable
placeholder = st.empty()

# Crear el cliente MQTT y conectar
try:
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
    client.subscribe(MQTT_TOPIC)
    st.success("✅ Conectado al broker MQTT")
except Exception as e:
    st.error(f"❌ Error de conexión: {e}")

# Bucle principal de la aplicación
while True:
    with placeholder.container():
        # Columnas para métricas y gráfica
        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("Últimas lecturas")
            
            # Mostrar último valor recibido
            if st.session_state.data:
                last_data = st.session_state.data[-1]
                st.metric(
                    label="Valor del Sensor",
                    value=f"{last_data.get('value', 'N/A')} {last_data.get('unit', '')}",
                    delta=None
                )
                st.text(f"Última actualización: {last_data.get('timestamp', 'N/A')}")
                
                # Mostrar estadísticas básicas
                if len(st.session_state.data) > 1:
                    df = pd.DataFrame(st.session_state.data)
                    st.markdown("### Estadísticas")
                    st.write(f"Promedio: {df['value'].mean():.2f}")
                    st.write(f"Máximo: {df['value'].max():.2f}")
                    st.write(f"Mínimo: {df['value'].min():.2f}")

        with col2:
            st.subheader("Histórico de lecturas")
            
            if st.session_state.data:
                # Crear DataFrame
                df = pd.DataFrame(st.session_state.data)
                
                # Crear y mostrar la gráfica
                fig = create_sensor_plot(df)
                st.plotly_chart(fig, use_container_width=True)

    # Esperar 3 segundos antes de la siguiente actualización
    time.sleep(3)
