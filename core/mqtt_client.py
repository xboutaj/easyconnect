import ssl
import threading
import paho.mqtt.client as mqtt

latest_message = {}

def on_connect(client, userdata, flags, rc):
    print("[MQTT] Connected with result code", rc)
    client.subscribe("easyconnect/#") 

def on_message(client, userdata, msg):
    global latest_message
    topic = msg.topic
    payload = msg.payload.decode()
    latest_message[topic] = payload
    print(f"[MQTT] Message received: {topic} → {payload}")

def publish_message(topic, payload):
    mqtt_client.publish(topic, payload)

def start_mqtt():
    global mqtt_client
    mqtt_client = mqtt.Client()
    mqtt_client.tls_set("core/hivemq-cert.pem", tls_version=ssl.PROTOCOL_TLS_CLIENT)

    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect("broker.hivemq.com", 8883)
    thread = threading.Thread(target=mqtt_client.loop_forever)
    thread.daemon = True
    thread.start()