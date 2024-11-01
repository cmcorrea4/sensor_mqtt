import streamlit as st
import paho.mqtt.client as mqtt
import json
from datetime import datetime
import time

# Configuración de la página
st.set_page_config(
    page_title="Monitor de Sensor MQTT",
    page_icon="📊"
)

# Configuración MQTT
MQTT_BROKER = "broker.mqttdashboard.com"  # Cambia esto según tu broker
MQTT_PORT = 1883
MQTT_TOPIC = "sensor_st"  # Cambia esto según tu tópico

def get_mqtt_message():
    """Función para obtener un único mensaje MQTT"""
    message_received = {"received": False, "payload": None}
    
    def on_message(client, userdata, message):
        try:
            # Decodificar el mensaje JSON con el formato específico
            raw_payload = message.payload.decode()
            payload = json.loads(raw_payload)
            
            # Crear diccionario con los datos formateados
            formatted_data = {
                'temperatura': payload.get('Temp', 'N/A'),
                'humedad': payload.get('Hum', 'N/A'),
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'raw_data': raw_payload  # Guardamos el payload original para debugging
            }
            
            message_received["payload"] = formatted_data
            message_received["received"] = True
            
        except json.JSONDecodeError as e:
            st.error(f"Error decodificando JSON: {e}\nPayload recibido: {message.payload}")
        except Exception as e:
            st.error(f"Error procesando mensaje: {e}")
    
    try:
        # Crear y configurar el cliente
        client = mqtt.Client()
        client.on_message = on_message
        
        # Conectar al broker
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.subscribe(MQTT_TOPIC)
        client.loop_start()
        
        # Esperar hasta 5 segundos por un mensaje
        timeout = time.time() + 5
        while not message_received["received"] and time.time() < timeout:
            time.sleep(0.1)
        
        # Detener el cliente
        client.loop_stop()
        client.disconnect()
        
        return message_received["payload"]
    
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

# Interfaz de usuario
st.title("📊 Monitor de Sensor")

# Botón de actualización
if st.button("Obtener Lectura"):
    with st.spinner('Escuchando el tópico MQTT...'):
        data = get_mqtt_message()
        
        if data:
            st.success("✅ Mensaje recibido")
            
            # Crear dos columnas para mostrar temperatura y humedad
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    label="Temperatura",
                    value=f"{data['temperatura']}°C" if data['temperatura'] != 'N/A' else 'N/A'
                )
            
            with col2:
                st.metric(
                    label="Humedad",
                    value=f"{data['humedad']}%" if data['humedad'] != 'N/A' else 'N/A'
                )
            
            st.text(f"Timestamp: {data['timestamp']}")
            
            # Mostrar datos raw para debugging
            with st.expander("Ver datos raw"):
                st.code(data['raw_data'])
        else:
            st.warning("No se recibió ningún mensaje en los últimos 5 segundos")
