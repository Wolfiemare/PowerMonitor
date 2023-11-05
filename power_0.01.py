import paho.mqtt.client as mqtt
import time
import PySimpleGUI as sg

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
import json

def on_message(client, userdata, msg):

    # print(f"Topic: {msg.topic} Message: {msg.payload.decode('utf-8')}")

    if msg.topic.endswith("/SENSOR"):   

        # Decode the message payload from JSON to a Python dictionary
        data = json.loads(msg.payload.decode('utf-8'))

        # Extract the relevant data from the dictionary
        energy_data = data['ENERGY']
        total_energy = energy_data['Total']
        yesterday_energy = energy_data['Yesterday']
        today_energy = energy_data['Today']
        power = energy_data['Power']
        voltage = energy_data['Voltage']
        current = energy_data['Current']

        # Extract the plug number from the topic string
        plug_number = msg.topic.split("/")[1]

        # Store the data in a suitable data structure for later use
        plug_data = {
            'total_energy': total_energy,
            'yesterday_energy': yesterday_energy,
            'today_energy': today_energy,
            'power': power,
            'voltage': voltage,
            'current': current
        }

        # Store the data in a list for up to 5 plugs
        if plug_number == "Room1Plug":
            # Store the data for Plug 1 in the list
            plug_data_list[0] = plug_data
            window['-PLUG1-'].update(f"Total Energy: {total_energy}\nYesterday Energy: {yesterday_energy}\nToday Energy: {today_energy}\nPower: {power}\nVoltage: {voltage}\nCurrent: {current}")
        elif plug_number == "Room2Plug":
            # Store the data for Plug 2 in the list
            plug_data_list[1] = plug_data
            window['-PLUG2-'].update(f"Total Energy: {total_energy}\nYesterday Energy: {yesterday_energy}\nToday Energy: {today_energy}\nPower: {power}\nVoltage: {voltage}\nCurrent: {current}")
        elif plug_number == "Room3Plug":
            # Store the data for Plug 3 in the list
            plug_data_list[2] = plug_data
            window['-PLUG3-'].update(f"Total Energy: {total_energy}\nYesterday Energy: {yesterday_energy}\nToday Energy: {today_energy}\nPower: {power}\nVoltage: {voltage}\nCurrent: {current}")
        elif plug_number == "Room4Plug":
            # Store the data for Plug 4 in the list
            plug_data_list[3] = plug_data
            window['-PLUG4-'].update(f"Total Energy: {total_energy}\nYesterday Energy: {yesterday_energy}\nToday Energy: {today_energy}\nPower: {power}\nVoltage: {voltage}\nCurrent: {current}")
        elif plug_number == "Room5Plug":
            # Store the data for Plug 5 in the list
            plug_data_list[4] = plug_data
            window['-PLUG5-'].update(f"Total Energy: {total_energy}\nYesterday Energy: {yesterday_energy}\nToday Energy: {today_energy}\nPower: {power}\nVoltage: {voltage}\nCurrent: {current}")

        # Print the data for all plugs
        print("Data for all plugs:")
        print(plug_data_list)

# Initialize the list to store data for up to 5 plugs
plug_data_list = [None] * 5

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

# Create PySimpleGUI window
sg.theme('DarkBlue3')
layout = [[sg.Text('Plug 1', font=('Helvetica', 20), justification='center', key='-PLUG1-')],
          [sg.Text('Plug 2', font=('Helvetica', 20), justification='center', key='-PLUG2-')],
          [sg.Text('Plug 3', font=('Helvetica', 20), justification='center', key='-PLUG3-')],
          [sg.Text('Plug 4', font=('Helvetica', 20), justification='center', key='-PLUG4-')],
          [sg.Text('Plug 5', font=('Helvetica', 20), justification='center', key='-PLUG5-')]]
window = sg.Window('Power Monitor', layout, size=(800, 600))

# Connect with MQTT Broker
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)

publish_message(TOPIC_PLUG1, SUB_TOPIC_DATA_TIMEPERIOD, '10')
publish_message(TOPIC_PLUG2, SUB_TOPIC_DATA_TIMEPERIOD, '10')

# Start the loop to process the callbacks
while True:
    event, values = window.read(timeout=100)
    if event == sg.WIN_CLOSED:
        break
    mqtt_client.loop()
    print("Waiting for messages...")
    time.sleep(1)

window.close()
