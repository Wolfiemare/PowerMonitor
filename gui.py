import paho.mqtt.client as mqtt
import tkinter as tk
import threading
import random
import time
import json

# MQTT Broker settings
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 60

# Define the MQTT on_connect event handler
def turn_plug_on_off(plug_num, condition):
    """
    Turns a Tasmota smart plug on or off using MQTT.

    Args:
        plug_num (int): The number of the plug to turn on or off.
        condition (str): The condition to set the plug to, either "On" or "Off".
    """
    if plug_online_status[plug_num-1]:
        topic = f"house/Room{plug_num}Plug/cmnd/Power"
        mqtt_client.publish(topic, condition)
        update_status(f"Plug {plug_num} turned {condition}.")
    else:
        update_status(f"Plug {plug_num} is offline.")

# Define the MQTT on_connect event handler
def set_telemetry_period(plug_num, tele_period):
    """
    Sets the telemetry period for a specific plug.

    Args:
        plug_num (int): The number of the plug to set the telemetry period for.
        tele_period (int): The telemetry period to set, in seconds.
    """
    topic = f"house/Room{plug_num}Plug/cmnd/TelePeriod"
    mqtt_client.publish(topic, tele_period)
    update_status(f"Telemetry period for plug {plug_num} set to {tele_period} seconds.")

# Define the MQTT on_connect event handler
def set_power_on_state(plug_num, state=1):
    """
    Set the power on state for a specific plug.

    Args:
        plug_num (int): The number of the plug.
        state (int, optional): The power on state to set. Defaults to 1.

    Returns:
        None
    """
    topic = f"house/Room{plug_num}Plug/cmnd/PowerOnState"
    mqtt_client.publish(topic, state)
    update_status(f"Power On State for plug {plug_num} set to {state}.")

# Define the MQTT on_connect event handler
def on_connect(client, userdata, flags, rc):
    """
    Callback function that is called when the client connects to the broker.

    :param client: The client instance that is connecting.
    :param userdata: Any user data that was specified during connection.
    :param flags: Response flags sent by the broker.
    :param rc: The connection result code.
    """
    print("Connected with result code "+str(rc))
    update_status("Connected with result code "+str(rc))

    client.subscribe("house/#")  # Subscribe to all topics within 'house/'
    
# Define the MQTT on_message event handler
def on_message(client, userdata, msg):
    """
    Callback function that is called when a message is received from the MQTT broker.

    Parameters:
    - client: The MQTT client instance that received the message.
    - userdata: Any custom data that was specified when setting up the MQTT client.
    - msg: The received message, containing the topic and payload.

    Returns:
    None

    This function processes the received message and performs actions based on the topic and payload.
    It updates the status, energy data, plug online status, power status, and handles any errors in the payload.
    """
    topic = msg.topic
    payload = msg.payload.decode('utf-8')

    print(f"Topic: {topic} \nMessage: {payload}")
    print("")
    # update_status(f"Topic: {topic} Message: {payload}")

    if 'SENSOR' in topic:
        plug_num_str = topic.split('/')[1].replace('Room', '').replace('Plug', '')
        print(plug_num_str)

        if plug_num_str.isdigit():
            plug_num = int(plug_num_str)
            update_status(f"Plug {plug_num} data received.")
            energy_data = json.loads(payload)['ENERGY']
            # energy_data['Time'] = json.loads(payload)['Time']

            # Add the energy data to the list of dictionaries based on the plug number
            energy_data_list[plug_num-1].append(energy_data)

    # Check if the plug is online
    if 'LWT' in topic:
        plug_num_str = topic.split('/')[1].replace('Room', '').replace('Plug', '')
        print(plug_num_str)

        if plug_num_str.isdigit():
            plug_num = int(plug_num_str)
            if payload == 'Online':
                plug_online_status[plug_num-1] = True
                update_status(f"Plug {plug_num} is online.")
                set_telemetry_period(plug_num, TELEMETRY_PERIOD)
                set_power_on_state(plug_num) # Set the power on state to ON
            else:
                plug_online_status[plug_num-1] = False
                update_status(f"Plug {plug_num} is offline.")
         
    # Check if the plug is providing power or not (i.e. if it is on or off)
    if 'STATE' in topic:
        plug_num_str = topic.split('/')[1].replace('Room', '').replace('Plug', '')
        print(plug_num_str)

        if plug_num_str.isdigit():
            plug_num = int(plug_num_str)
                        # Parse the JSON payload
            try:
                payload_dict = json.loads(payload)
                power_state = payload_dict.get('POWER', 'UNKNOWN')  # Default to 'UNKNOWN' if key is not present
                
                # Update the power status in the list
                power_status_list[plug_num - 1] = power_state
                print(f"Plug {plug_num} power status updated to: {power_state}")
                print(f"Current power status list: {power_status_list}")
                
            except json.JSONDecodeError:
                print("Error: Payload is not valid JSON")

    # Check if the plug has been turn on or off
    if 'RESULT' in topic:
        plug_num_str = topic.split('/')[1].replace('Room', '').replace('Plug', '')
        print(plug_num_str)

        if plug_num_str.isdigit():
            plug_num = int(plug_num_str)     
            try:
                payload_dict = json.loads(payload)
                if 'POWER' in payload_dict:
                    # The JSON payload has a 'POWER' key
                    power_state = payload_dict['POWER']
                    power_status_list[plug_num - 1] = power_state

                    print(f"Plug {plug_num} power status updated to: {power_state}")
                    print(f"Current power status list: {power_status_list}")
                
            except json.JSONDecodeError:
                print("Error: Payload is not valid JSON")

# Define the MQTT on_publish event handler
def on_publish(client, userdata, mid):
    """
    Callback function that is called when a message is successfully published to the broker.

    Parameters:
    client (paho.mqtt.client.Client): The client instance that triggered this callback.
    userdata: The private user data as set in Client() or userdata_set().
    mid (int): The message ID of the published message.

    Returns:
    None
    """
    print("Message published with id "+str(mid))
    update_status("Message published with id "+str(mid))

# Function to update the status bar
def update_status(message):
    """
    Updates the status message displayed in the GUI.

    Args:
        message (str): The message to display in the status bar.
    """
    status_message.config(text=f"Status: {message}")

# Dummy functions for the function buttons
def set_night_mode():
    # turn off all plugs that are set to sleep in the plugs_to_sleep list
    for i, plug in enumerate(plugs_to_sleep):
        if plug:
            turn_plug_on_off(i+1, "OFF")    # Turn off the plug
            print(f"Plug {i+1} turned off.")
    update_status("Plugs turn off ready for bed.")

def function2():
    update_status("Function 2 activated.")

def function3():
    update_status("Function 3 activated.")

# Function for the exit button
def function4():
    """
    This function stops the mainloop and destroys all widgets to close the window.
    """
    root.quit()  # This will stop the mainloop
    root.destroy()  # This will destroy all widgets and close the window

# Function to fetch data from the plugs
def fetch_data():
    """
    Continuously fetches data and updates the GUI every 2 seconds.

    This function schedules the `update_data_fields` function to run on the main thread
    every 2 seconds to update the GUI with the latest data.
    """
    while True:
        # Schedule the `update_data_field` to run on the main thread
        root.after(0, update_data_fields)
        time.sleep(2)  # Simulate delay for fetching data

# Function to update the data fields with data from energy_data_list
def update_data_fields():
    """
    Update the GUI data fields with the latest energy data for each plug.

    For each column in the GUI table, get the latest energy data for the corresponding plug,
    and update the data fields with the following information:
    - Total energy consumption (in kWh)
    - Energy consumption yesterday (in kWh)
    - Energy consumption today (in kWh)
    - Power consumption (in W)
    - Apparent power consumption (in VA)
    - Reactive power consumption (in VAr)
    - Power factor
    - Voltage (in V)
    - Current (in A)
    - Online status (either "ONLINE" or "OFFLINE")
    - Total cost (in £) based on the energy consumption and the KWH_COST constant
        (which should be defined elsewhere in the code)

    The current field is highlighted with different colors depending on its value:
    - Green if the current is less than 4.3 A
    - Orange if the current is between 4.31 A and 8.3 A
    - Red if the current is greater than 8.3 A
    """
    for i, name in enumerate(column_names):
        energy_data = energy_data_list[i]
        
        data_fields[name][12].delete(0, tk.END)
        status = "ONLINE" if plug_online_status[i] else "OFFLINE"
        data_fields[name][12].insert(0, status)
        data_fields[name][12].config(fg="green" if plug_online_status[i] else "red")

        data_fields[name][13].delete(0, tk.END)
        data_fields[name][13].insert(0, f"{power_status_list[i]}")
        data_fields[name][13].config(fg="green" if power_status_list[i] =='ON' else "red")

        if energy_data:
            # Get the latest energy data for the plug
            latest_energy_data = energy_data[-1]
        
            # Update the data fields with the latest energy data
            data_fields[name][0].delete(0, tk.END)
            data_fields[name][0].insert(0, f"{latest_energy_data['Total']}")
            data_fields[name][1].delete(0, tk.END)
            data_fields[name][1].insert(0, f"{latest_energy_data['Yesterday']}")
            data_fields[name][2].delete(0, tk.END)
            data_fields[name][2].insert(0, f"{latest_energy_data['Today']}")
            data_fields[name][3].delete(0, tk.END)
            data_fields[name][3].insert(0, f"{latest_energy_data['Power']}")
            data_fields[name][4].delete(0, tk.END)
            data_fields[name][4].insert(0, f"{latest_energy_data['ApparentPower']}")
            data_fields[name][5].delete(0, tk.END)
            data_fields[name][5].insert(0, f"{latest_energy_data['ReactivePower']}")
            data_fields[name][6].delete(0, tk.END)
            data_fields[name][6].insert(0, f"{latest_energy_data['Factor']}")
            data_fields[name][7].delete(0, tk.END)
            data_fields[name][7].insert(0, f"{latest_energy_data['Voltage']}")
            current = latest_energy_data['Current']
            data_fields[name][8].delete(0, tk.END)
            data_fields[name][8].insert(0, f"{current}")
            if current < 4.3:
                data_fields[name][8].config(font=('Helvetica', 10, 'bold'),bg="green", fg="white")
            elif 4.31 <= current <= 8.3:
                data_fields[name][8].config(font=('Helvetica', 10, 'bold'), bg="#FF6600", fg="white")
            else:
                data_fields[name][8].config(font=('Helvetica', 10, 'bold'), bg="red", fg="white")
            data_fields[name][9].delete(0, tk.END)
            data_fields[name][9].insert(0, f"£{latest_energy_data['Total']*KWH_COST:.2f}")
            data_fields[name][10].delete(0, tk.END)
            data_fields[name][10].insert(0, f"£{latest_energy_data['Yesterday']*KWH_COST:.2f}")
            data_fields[name][11].delete(0, tk.END)
            data_fields[name][11].insert(0, f"£{latest_energy_data['Today']*KWH_COST:.2f}")

# Function to create the GUI
def create_gui():
    # Create a frame for each column and populate it with labels and entry fields
    for i, name in enumerate(column_names):
        # Frame for the column
        frame = tk.Frame(root, borderwidth=1, relief="groove")
        frame.place(relx=i/5, rely=0, relwidth=1/5, relheight=0.85)  # Adjusted for function button area

        # Label for the column title
        label = tk.Label(frame, text=name, font=('Helvetica', 11, 'bold'))
        label.pack(side="top", fill="x")

        # Horizontal frames for data labels and fields
        for j in range(14):
            # Frame for each data row
            data_frame = tk.Frame(frame)
            data_frame.pack(side="top", fill="x", padx=2, pady=1)

            # Data label
            data_label = tk.Label(data_frame, text=data_labels[j], width=20, anchor="w", font=('Helvetica', 6))
            data_label.pack(side="left")

            # Data field
            data_field = tk.Entry(data_frame, font=('Helvetica', 9), width=6)
            data_field.pack(side="left", fill="x", expand=True)

            # Save the data field in the dictionary
            data_fields[name].append(data_field)
     
        # Frame for buttons
        button_frame = tk.Frame(frame, borderwidth=1, relief="sunken")
        button_frame.pack(side="bottom", fill="x", padx=2, pady=1)

        # Creating buttons and assigning commands
        # ON button
        on_button = tk.Button(button_frame, text="ON", font=('Helvetica', 10), command=lambda plug_number=i+1: turn_plug_on_off(plug_number, "ON"))
        on_button.pack(side="left", padx=2)

        # OFF button
        off_button = tk.Button(button_frame, text="OFF", font=('Helvetica', 10), command=lambda plug_number=i+1: turn_plug_on_off(plug_number, "OFF"))
        off_button.pack(side="left", padx=2)

    # Function buttons area
    func_button_frame = tk.Frame(root, borderwidth=1, relief="sunken")
    func_button_frame.place(relx=0, rely=0.86, relwidth=1, relheight=0.1)

    # Creating function buttons and assigning commands
    func_buttons = [set_night_mode, function2, function3, function4]  # function4 is the exit function
    button_texts = ["Night, Night", "Function 2", "Function 3", "Exit"]
    for i, (func, text) in enumerate(zip(func_buttons, button_texts)):
        btn = tk.Button(func_button_frame, text=text, font=('Helvetica', 10), command=func)
        btn.pack(side="left", expand=True, fill="x", padx=5, pady=2)
    
    # status_frame = tk.Frame(root, borderwidth=1, relief="sunken")
    # status_frame.place(relx=0, rely=0.85, relwidth=1, relheight=0.15)
    # status_message = tk.Label(status_frame, text="Status: Ready", bg="white", anchor="w", font=('Helvetica', 10))
    # status_message.pack(side="left", fill="both", expand=True)

# Create the main window
root = tk.Tk()
root.title("Tasmota Power Data Display")
root.geometry("800x470")

# Define a list of column names
column_names = ["Plug 1 - Office", "Plug 2 - Hallway", "Plug 3 - Lounge", "Plug 4 - Upstairs Hall", "Plug 5 - Bedroom"]

# Define a list of data labels
data_labels =  [
                'TOTAL (kWh)', 'YESTERDAY (kWh)', 'TODAY (kWh)', 'POWER (W)', 'APPARENT POWER (VA)', 'REACTIVE POWER (VAr)', 
                'FACTOR', 'VOLTAGE (V)', 'CURRENT (A)', 'TOTAL COST', 'YESTERDAY COST', 'TODAY COST',
                'STATUS', 'POWER STATE'
                ]       

power_status_list = ['OFF', 'OFF', 'OFF', 'OFF', 'OFF']  # Plugs ON/OFF status

plugs_to_sleep = [True, True, True, True, False]   # SHould a plug turn off when the Sleep button is pressed?

# Define the initial online status for the 6 plugs as False
plug_online_status = [False] * 5

# Create a dictionary of dictionaries to store the data fields
data_fields = {name: [] for name in column_names}

# Initialize the list of dictionaries for energy data for each plug
energy_data_list = [list() for _ in range(5)]

# Define the cost of 1 kWh of energy (in pounds)
KWH_COST = 0.2889
# Define the telemetry period (in seconds)
TELEMETRY_PERIOD = 20   # In seconds

create_gui()

# Status message box
status_frame = tk.Frame(root, borderwidth=1, relief="sunken")
status_frame.place(relx=0, rely=0.95, relwidth=1, relheight=0.05)
status_message = tk.Label(status_frame, text="Status: Ready", bg="white", anchor="w", font=('Helvetica', 8))
status_message.pack(side="left", fill="both", expand=True)

# Initiate MQTT Client
mqtt_client = mqtt.Client('Power Logger')
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.on_publish = on_publish

# Connect with MQTT Broker
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)
mqtt_client.loop_start()

# Start the data fetching in a background thread
fetch_thread = threading.Thread(target=fetch_data, daemon=True)
fetch_thread.start()

# Run the main loop of the GUI
root.mainloop()
