import streamlit as st
import paho.mqtt.client as mqtt
import json
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Monitor de Sensor MQTT",
    page_icon="📊"
)

# Inicialización de variables en session state
if 'last_data' not in st.session_state:
    st.session_state.last_data = None

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
        
        # Guardar último dato
        st.session_state.last_data = payload
    except Exception as e:
        st.error(f"Error procesando mensaje: {e}")

# Configurar cliente MQTT
client = mqtt.Client()
client.on_message = on_message

# Interfaz de usuario
st.title("📊 Monitor de Sensor")

# Conexión MQTT
try:
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
    client.subscribe(MQTT_TOPIC)
    st.success("✅ Conectado al broker MQTT")
except Exception as e:
    st.error(f"❌ Error de conexión: {e}")

# Botón de actualización
if st.button("Actualizar Lectura"):
    if st.session_state.last_data:
        st.metric(
            label="Valor del Sensor",
            value=f"{st.session_state.last_data.get('value', 'N/A')} {st.session_state.last_data.get('unit', '')}"
        )
        st.text(f"Última actualización: {st.session_state.last_data.get('timestamp', 'N/A')}")
    else:
        st.info("Esperando datos del sensor...")
