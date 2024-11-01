import streamlit as st
import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime
import pandas as pd
import plotly.express as px

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
MQTT_BROKER = "localhost"  # Cambia esto según tu broker
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/data"  # Cambia esto según tu tópico

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

# Interfaz de usuario
st.title("📊 Monitor de Sensor en Tiempo Real")

# Columnas para métricas y gráfica
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Últimas lecturas")
    
    # Mostrar estado de conexión
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
        client.subscribe(MQTT_TOPIC)
        st.success("✅ Conectado al broker MQTT")
    except Exception as e:
        st.error(f"❌ Error de conexión: {e}")

    # Mostrar último valor recibido
    if st.session_state.data:
        last_data = st.session_state.data[-1]
        st.metric(
            label="Valor del Sensor",
            value=f"{last_data.get('value', 'N/A')} {last_data.get('unit', '')}"
        )
        st.text(f"Última actualización: {last_data.get('timestamp', 'N/A')}")

with col2:
    st.subheader("Histórico de lecturas")
    
    if st.session_state.data:
        # Crear DataFrame
        df = pd.DataFrame(st.session_state.data)
        
        # Crear gráfica con Plotly
        fig = px.line(
            df,
            x='timestamp',
            y='value',
            title='Valores del Sensor en el Tiempo'
        )
        fig.update_layout(
            xaxis_title="Tiempo",
            yaxis_title="Valor del Sensor"
        )
        st.plotly_chart(fig, use_container_width=True)

# Actualizar cada 3 segundos
st.empty()
time.sleep(3)
st.experimental_rerun()
