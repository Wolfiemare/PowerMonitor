import paho.mqtt.client as mqtt
import time

# MQTT Broker settings
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 60

# Define on_connect event Handler
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("house/#")  # Subscribe to all topics within 'house/'

# Define on_message event Handler
def on_message(client, userdata, msg):
    print(f"Topic: {msg.topic} Message: {msg.payload.decode('utf-8')}")

# Define on_subscribe event Handler
def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))

# Define function to publish message
def on_publish(client, userdata, mid):
    print("Message published with id "+str(mid))

def publish_message(topic, sub_topic, message):
    result = mqtt_client.publish(topic + sub_topic, message)
    result.wait_for_publish()
    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        print("Message published successfully")
    else:
        print("Failed to publish message")


# Initiate MQTT Client
mqtt_client = mqtt.Client('Logger')

# Register event handlers
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.on_subscribe = on_subscribe

# Set MQTT topics
TOPIC_PLUG1 = 'house/Room1Plug/'  # Base address for Tasmota Plug MQTT interface
TOPIC_PLUG2 = 'house/Room2Plug/'  # Base address for Tasmota Plug MQTT interface

SUB_TOPIC_REQUESTSENSOR = 'cmnd/status'
SUB_TOPIC_CONTROL = 'cmnd/Power1'
SUB_TOPIC_DATA_TIMEPERIOD = 'cmnd/TelePeriod'
SUB_TOPIC_STATUS = 'stat/'
SUB_TOPIC_ROOM_DATA = 'stat/RoomData'
SUB_TOPIC_ROOM_PARA = 'stat/RoomParameter'



# Connect with MQTT Broker
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)

publish_message(TOPIC_PLUG1, SUB_TOPIC_DATA_TIMEPERIOD, '10')
publish_message(TOPIC_PLUG2, SUB_TOPIC_DATA_TIMEPERIOD, '10')

# Start the loop to process the callbacks
while True:
    mqtt_client.loop()
    # Publish message to MQTT Broker
    # publish_message(TOPIC_PLUG1, SUB_TOPIC_REQUESTSENSOR, '10')
    # publish_message(TOPIC_PLUG2, SUB_TOPIC_REQUESTSENSOR, '10')
    
    # Wait for 10 seconds
    time.sleep(1)
