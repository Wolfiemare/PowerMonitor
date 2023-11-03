# Import necessary libraries
import datetime
import paho.mqtt.client as mqtt
import time
import csv
from pathlib import Path
import ast
import PySimpleGUI as sg
import json
import asyncio
import threading

def send_Message(msg):
    """
    Sends an MQTT message to a specified topic.

    Args:
        msg (str): The message to be sent.

    Returns:
        None.
    """
    topic = TOPIC + SUB_TOPIC_SUPERVISOR
    # Publish the message to the MQTT broker
    result = client.publish(topic, msg)
    # Check if the message was successfully sent
    status = result[0]
    if status == 0:
        print(f"Sent `{msg}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")


def on_message(client, userdata, message):
    """
    Callback function for when a message is received.
    Updates global variables based on the received message.

    Args:
        client: The MQTT client.
        userdata: User-defined data that is passed as the "userdata" parameter of the connect() function.
        message: The received message.

    Returns:
        None.
    """

    # # Use global keyword to access global variables
    # global readingTaken, controllersParameters, graphic_off, parametersReceived, display_update_required

    # Print the topic of the received message
    print(message.topic)

    # Convert the received message to string
    receivedMessage = message.payload.decode("utf-8")

    # if 'RoomData' in message.topic:
    #     # Convert the received string to dictionary
    #     controllersParameters = json.loads(receivedMessage)

    #     # Check if heating is selected or not
    #     if controllersParameters['heating_selected'] == 'Yes':
    #         graphic_off = False
    #     else:
    #         graphic_off = True

    #     # # Request an update of the GUI display with the latest controller parameters
    #     # display_update_required = True
    #     # update_display()

    #     # Send custom event to the main thread for GUI update
    #     window.write_event_value(UPDATE_EVENT, None)

    #     # Set the flag to indicate that parameters have been received
    #     parametersReceived = True

    #     # Save the received parameters to a CSV file
    #     csv_file = f"{controllersParameters['room_name']}.csv"
    #     append_to_csv(controllersParameters, csv_file)


TOPIC = 'house/Room2Plug/'  #Base address for Tasmota Plug MQTT interface
SUB_TOPIC_REQUESTSENSOR = 'cmnd/status'
SUB_TOPIC_CONTROL = 'cmnd/Power1'
SUB_TOPIC_STATUS = 'stat/'
SUB_TOPIC_ROOM_DATA = 'stat/RoomData'
SUB_TOPIC_SUPERVISOR = 'stat/Supervisor'

# Set up MQTT Client
mqttBroker ="Logger"

client = mqtt.Client(mqttBroker)
client.connect("broker.hivemq.com") 
client.loop_start()

#client.subscribe("house/Room1Plug/stat/RoomData")
client.subscribe("house/Room1Plug/#")
client.on_message=on_message 