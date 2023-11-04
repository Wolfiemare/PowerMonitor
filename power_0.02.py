import paho.mqtt.client as mqtt
import PySimpleGUI as sg
import json
import threading
import time

# MQTT Broker settings
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 60

# PySimpleGUI window layout
layout = [
    [sg.Text("Energy Data for RoomPlug1", font='Any 15')],
    [sg.Text("Total:"), sg.Text('', key='-TOTAL1-')],
    [sg.Text("Yesterday:"), sg.Text('', key='-YESTERDAY1-')],
    [sg.Text("Today:"), sg.Text('', key='-TODAY1-')],
    [sg.Text("Power:"), sg.Text('', key='-POWER1-')],
    [sg.Text("Apparent Power:"), sg.Text('', key='-APPARENTPOWER1-')],
    [sg.Text("Reactive Power:"), sg.Text('', key='-REACTIVEPOWER1-')],
    [sg.Text("Factor:"), sg.Text('', key='-FACTOR1-')],
    [sg.Text("Voltage:"), sg.Text('', key='-VOLTAGE1-')],
    [sg.Text("Current:"), sg.Text('', key='-CURRENT1-')],
    [sg.Text("Energy Data for RoomPlug2", font='Any 15')],
    [sg.Text("Total:"), sg.Text('', key='-TOTAL2-')],
    [sg.Text("Yesterday:"), sg.Text('', key='-YESTERDAY2-')],
    [sg.Text("Today:"), sg.Text('', key='-TODAY2-')],
    [sg.Text("Power:"), sg.Text('', key='-POWER2-')],
    [sg.Text("Apparent Power:"), sg.Text('', key='-APPARENTPOWER2-')],
    [sg.Text("Reactive Power:"), sg.Text('', key='-REACTIVEPOWER2-')],
    [sg.Text("Factor:"), sg.Text('', key='-FACTOR2-')],
    [sg.Text("Voltage:"), sg.Text('', key='-VOLTAGE2-')],
    [sg.Text("Current:"), sg.Text('', key='-CURRENT2-')],
    [sg.Button('Exit')]
]

# Create the window
window = sg.Window('Tasmota Energy Data', layout)

# Define the MQTT on_connect event handler
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("house/RoomPlug1/stat/STATUS10", qos=0)
    client.subscribe("house/RoomPlug2/stat/STATUS10", qos=0)

# Define the MQTT on_message event handler
def on_message(client, userdata, msg):
    print(f"Topic: {msg.topic} Message: {msg.payload.decode('utf-8')}")
    topic = msg.topic
    payload = msg.payload.decode('utf-8')
    print(f"Topic: {topic} Message: {payload}")
    
    data = json.loads(payload)['StatusSNS']['ENERGY']
    if 'RoomPlug1' in topic:
        window.write_event_value('-ENERGY1-', data)
    elif 'RoomPlug2' in topic:
        window.write_event_value('-ENERGY2-', data)

# Define the MQTT on_publish event handler
def on_publish(client, userdata, mid):
    print("Message published with id "+str(mid))

# Define the function to publish the sensor data request
def publish_sensor_data_request():
    while True:
        time.sleep(5)
        mqtt_client.publish("house/RoomPlug1/cmnd/STATUS", "10")
        mqtt_client.publish("house/RoomPlug2/cmnd/STATUS", "10")
        

# Initiate MQTT Client
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.on_publish = on_publish

# Connect with MQTT Broker
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)
mqtt_client.loop_start()

# Start the thread to publish sensor data requests every 20 seconds
request_thread = threading.Thread(target=publish_sensor_data_request, daemon=True)
request_thread.start()

# Event loop to update the GUI with the received energy data
while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED or event == 'Exit':
        break

    if event == '-ENERGY1-':
        energy_data = values[event]
        # Update plug1 data in the GUI
        for key_suffix in ['TOTAL', 'YESTERDAY', 'TODAY', 'POWER', 'APPARENTPOWER', 'REACTIVEPOWER', 'FACTOR', 'VOLTAGE', 'CURRENT']:
            window[f'-{key_suffix}1-'].update(energy_data[key_suffix])

    elif event == '-ENERGY2-':
        energy_data = values[event]
        # Update plug2 data in the GUI
        for key_suffix in ['TOTAL', 'YESTERDAY', 'TODAY', 'POWER', 'APPARENTPOWER', 'REACTIVEPOWER', 'FACTOR', 'VOLTAGE', 'CURRENT']:
            window[f'-{key_suffix}2-'].update(energy_data[key_suffix])

# Clean up
window.close()
mqtt_client.loop_stop()
mqtt_client.disconnect()
