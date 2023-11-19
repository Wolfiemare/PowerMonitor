import paho.mqtt.client as mqtt
import tkinter as tk
import threading
import time
from datetime import datetime, timedelta
import json
import schedule
# from collections import OrderedDict
import os
import pandas as pd

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

# Set up the schedules
def setup_schedules():
    """
    Set up schedules for waking up and turning on plugs on weekdays and weekends.
    Existing jobs are cleared before setting up new schedules.
    """
    # Clear any existing jobs if this function might be run multiple times
    schedule.clear('weekday')
    schedule.clear('weekend')
    schedule.clear('update_data')

    # Schedule for weekdays
    for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
        schedule.every().day.at(weekday_wake_up_time).do(wake_up_and_turn_on_plugs).tag('weekday')

    # Schedule for weekends
    for day in ['saturday', 'sunday']:
        schedule.every().day.at(weekend_wake_up_time).do(wake_up_and_turn_on_plugs).tag('weekend')

    # Schedule data update every hour   
    schedule.every(10).minutes.do(update_all_plugs).tag('update_data')

# Turn on all plugs that are set to sleep in the plugs_to_sleep list
def wake_up_and_turn_on_plugs():
    for i, plug in enumerate(plugs_to_wake):
        if plug:
            turn_plug_on_off(i+1, "ON")    # Turn on the plug
            print(f"Plug {i+1} turned on.")
    update_status("Good Morning - I have turned the heaters on.")
    return # schedule.CancelJob  # This will cancel the job after it's run once

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
    try:
        payload = msg.payload.decode('utf-8')   # Convert the payload to a string
    except UnicodeDecodeError:
        print("Error: Payload is not UTF-8 encoded")
        return  

    print(f"Topic: {topic} \nMessage: {payload}")
    print("")
    # update_status(f"Topic: {topic} Message: {payload}")

    if 'SENSOR' in topic:
        plug_num_str = topic.split('/')[1].replace('Room', '').replace('Plug', '')
        #print(plug_num_str)

        if plug_num_str.isdigit():
            plug_num = int(plug_num_str)
            update_status(f"Plug {plug_num} data received.")
            energy_data = json.loads(payload)['ENERGY']
            # energy_data['Time'] = json.loads(payload)['Time']

            # Add the energy data to the list of dictionaries based on the plug number
            energy_data_list[plug_num-1].append(energy_data)
            #print(energy_data_list)

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
                #print(f"Plug {plug_num} power status updated to: {power_state}")
                #print(f"Current power status list: {power_status_list}")
                
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

                    #print(f"Plug {plug_num} power status updated to: {power_state}")
                    #print(f"Current power status list: {power_status_list}")
                
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

# Night,Night mode turns of heaters until the morning when the schedule turns them back on
def set_night_mode():
    # turn off all plugs that are set to sleep in the plugs_to_sleep list
    for i, plug in enumerate(plugs_to_sleep):
        if plug:
            turn_plug_on_off(i+1, "OFF")    # Turn off the plug
            print(f"Plug {i+1} turned off.")
    update_status("Plugs turn off ready for bed.")

# Wake up mode turns on all plugs that are set to wake in the plugs_to_wake list
def wake_up():
    """
    Turns on all plugs that are set to wake in the plugs_to_wake list.

    This function iterates over the plugs_to_wake list and turns on the plugs that are set to wake.
    Each plug is identified by its index in the list, starting from 0.
    After turning on a plug, it prints a message indicating which plug was turned on.
    """
    for i, plug in enumerate(plugs_to_wake):
        if plug:
            turn_plug_on_off(i+1, "ON")    # Turn on the plug
            print(f"Plug {i+1} turned on.")

def function3():
    update_status("Function 3 activated.")
    display_historical_data("Plug3")   
    
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
        schedule.run_pending()
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
        data_fields[name][13].config(bg="green" if power_status_list[i] =='ON' else "red", fg="white", font=('Helvetica', 10, 'bold'))

        if energy_data:
            # Get the latest energy data for the plug
            latest_energy_data = energy_data[-1]
        
            # Update the data fields with the latest energy data
            data_fields[name][0].delete(0, tk.END)
            data_fields[name][0].insert(0, f"{latest_energy_data['Total']:.2f}")
            data_fields[name][1].delete(0, tk.END)
            data_fields[name][1].insert(0, f"{latest_energy_data['Yesterday']:.2f}")
            data_fields[name][2].delete(0, tk.END)
            data_fields[name][2].insert(0, f"{latest_energy_data['Today']:.2f}")
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
        on_button = tk.Button(button_frame, text="ON", font=('Helvetica', 10), command=lambda plug_number=i+1: turn_plug_on_off(plug_number, "ON"), bg="dark grey")
        on_button.pack(side="left", fill="both", expand=True, padx=2)

        # OFF button
        off_button = tk.Button(button_frame, text="OFF", font=('Helvetica', 10), command=lambda plug_number=i+1: turn_plug_on_off(plug_number, "OFF"), bg="dark grey")
        off_button.pack(side="left", fill="both", expand=True, padx=2)

    # Function buttons area
    func_button_frame = tk.Frame(root, borderwidth=1, relief="sunken")
    func_button_frame.place(relx=0, rely=0.86, relwidth=1, relheight=0.1)

    # Creating function buttons and assigning commands
    func_buttons = [set_night_mode, wake_up, function3, function4]  # function4 is the exit function
    button_texts = ["Night, Night", "Wake Up", "Function 3", "Exit"]
    for i, (func, text) in enumerate(zip(func_buttons, button_texts)):
        btn = tk.Button(func_button_frame, text=text, font=('Helvetica', 10), command=func)
        btn.pack(side="left", expand=True, fill="x", padx=5, pady=2)

# Add data to the smart_plug_data dictionary
def add_data(plug, kWh, cost, timestamp=None):
    """
    Add data for a specific plug to the smart_plug_data dictionary.

    Args:
        plug (str): The name of the plug.
        kWh (float): The energy consumption in kilowatt-hours.
        cost (float): The cost of the energy consumption.
        timestamp (str, optional): The timestamp of the data entry in ISO 8601 format. 
            If not provided, the current timestamp will be used.

    Returns:
        None
    """
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M")
    else:
        timestamp = datetime.fromisoformat(timestamp).strftime("%Y-%m-%dT%H:%M")
    hour = datetime.fromisoformat(timestamp).hour
    if len(smart_plug_data[plug]) >= HOURS_IN_YEAR:
        smart_plug_data[plug].pop(0)
    smart_plug_data[plug].append({"timestamp": timestamp, "hour": hour, "kWh": round(kWh, 2), "Cost": round(cost, 2)})

# Get the data for a specific plug and date
def get_data_for_day(plug_id, date=None):
    """
    Retrieve the data for a specific day for a given plug.

    Args:
        plug_id (str): The ID of the plug.
        date (str, optional): The date in the format "%m-%d". If not provided, today's date will be used.

    Returns:
        dict: The data for the specified day for the given plug.
    """
    # If no date is provided, use today's date
    if date is None:
        date = datetime.now().strftime("%m-%d")

    return smart_plug_data[plug_id][date]

# Update the historical data for all plugs
def update_all_plugs():
    """
    Update the energy data for all plugs.

    This function loops over all plugs and retrieves the latest energy data.
    It calculates the kWh and cost for each plug and updates the smart_plug_data dictionary.
    Finally, it saves the updated data to a file and prints the data for Plug3.

    Parameters:
    None

    Returns:
    None
    """
    # Loop over all plugs
    for i in range(5):
        if energy_data_list[i]:
            # Get the latest energy data for the plug
            latest_energy_data = energy_data_list[i][-1]
            # Get the kWh and cost
            kWh = round(latest_energy_data['Today'], 2)
            cost = kWh * KWH_COST

            # Add the data to the smart_plug_data dictionary
            update_record(f"Plug{i+1}", kWh, cost)
    
    # save_data(file_path, smart_plug_data)  # Save the updated data to the file
    # print('*************************************************************************************************')
    # print(get_data_for_day('Plug3'))
    # print('*************************************************************************************************')
          
# spawn a child tkinter window to display historical data trend for a specific plug
def display_historical_data(plug):
    # Create a new window
    window = tk.Toplevel(root)
    window.title(f"{plug} Power Data")
    window.geometry("800x470")

    # Assuming get_data_for_day returns a list of dictionaries
    data = get_data_for_day(plug)

    # Define column headers
    headers = ['Hour', 'kWh', 'Cost']

    # Create header labels with smaller font and fixed width, minimal padding
    for j, header in enumerate(headers):
        header_label = tk.Label(window, text=header, font=('Arial', 8, 'bold'), width=10)
        header_label.grid(row=0, column=j, sticky='w', padx=1, pady=0)

    # Create a table in the window with smaller font, fixed width for labels, and minimal padding
    for i, record in enumerate(data):
        # Format hour labels as '00:00 - 01:00', '01:00 - 02:00', etc.
        hour_label_text = f"{i:02d}:00 - {i+1:02d}:00"
        hour_label = tk.Label(window, text=hour_label_text, font=('Arial', 8), width=15)
        hour_label.grid(row=i+1, column=0, sticky='w', padx=1, pady=0)

        # kWh and Cost columns
        for j, key in enumerate(['kWh', 'Cost']):
            cell_value = record[key]
            cell = tk.Label(window, text=f"{cell_value:.2f}", font=('Arial', 8), width=10)
            cell.grid(row=i+1, column=j+1, sticky='w', padx=1, pady=0)

    # Add an exit button in a column to the right of the data table with minimal padding
    exit_button = tk.Button(window, text="Exit", command=window.destroy, font=('Arial', 8))
    exit_button.grid(row=0, column=len(headers) + 1, rowspan=len(data) + 1, sticky='ns', padx=1, pady=0)

# Function to create initial data structure
def create_initial_data():
    """
    Creates an initial data structure for storing historical power consumption data.

    Returns:
        dict: A dictionary containing the initial data structure.
            The keys are the names of the smart plugs, and the values are dictionaries.
            Each inner dictionary represents the power consumption data for a specific smart plug.
            The keys of the inner dictionary are the dates in the format "mm-dd",
            and the values are lists of dictionaries representing the power consumption data for each hour of the day.
            Each hour dictionary contains the keys "kWh" and "Cost" with initial values of 0.00.
    """
    smart_plugs = ["Plug1", "Plug2", "Plug3", "Plug4", "Plug5"]
    data_structure = {plug: {} for plug in smart_plugs}

    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)
    delta = timedelta(days=1)

    while start_date <= end_date:
        date_str = start_date.strftime("%m-%d")
        for plug in smart_plugs:
            data_structure[plug][date_str] = [{"kWh": 0.00, "Cost": 0.00} for _ in range(24)]
        start_date += delta

    return data_structure

# Function to save data to JSON
def save_data(file_path, data):
    """
    Save data to a file.

    Args:
        file_path (str): The path to the file where the data will be saved.
        data (dict): The data to be saved.

    Returns:
        None
    """
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

# Function to load data from JSON
def load_data(file_path):
    """
    Load data from a JSON file.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        dict: The loaded data as a dictionary.
    """
    with open(file_path, 'r') as file:
        return json.load(file)

# Function to check for existing data or create new data
def initialize_data(file_path):
    """
    Initializes the data structure by either loading it from an existing file or creating a new one.

    Args:
        file_path (str): The path to the file containing the data structure.

    Returns:
        dict: The initialized data structure.

    """
    if os.path.exists(file_path):
        data_structure = load_data(file_path)
    else:
        data_structure = create_initial_data()
        save_data(file_path, data_structure)  # Save the initial data to the file
    return data_structure

# Function to update the record for a specific smart plug
def update_record(plug_id, kWh, cost, date=None, hour=None):
    """
    Update the record for a specific smart plug.

    Args:
        plug_id (int): The ID of the smart plug.
        kWh (float): The energy consumption in kilowatt-hours.
        cost (float): The cost of the energy consumption.
        date (str, optional): The date of the record in the format "mm-dd". If not provided, the current date is used.
        hour (int, optional): The hour of the record. If not provided, the current hour is used.

    Returns:
        None
    """
    # If date and hour are not provided, use current date and time
    if date is None:
        date = datetime.now().strftime("%m-%d")
    if hour is None:
        hour = datetime.now().hour

    # Update the record
    smart_plug_data[plug_id][date][hour] = {"kWh": round(kWh, 2), "Cost": round(cost, 2)}

# Function to get the data for a specific plug and date
def get_data_for_day(plug_id, date=None):
    """
    Retrieves the data for a specific plug on a given day.

    Args:
        plug_id (str): The ID of the plug.
        date (str, optional): The date in the format "%m-%d". If not provided, today's date will be used.

    Returns:
        dict: The data for the specified plug on the given day.
    """
    # If no date is provided, use today's date
    if date is None:
        date = datetime.now().strftime("%m-%d")

    return smart_plug_data[plug_id][date]

# MQTT Broker settings
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 60

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

plugs_to_wake = [False, True, True, True, False]   # SHould a plug turn on when the Wake schedule runs?

# Define the initial online status for the 6 plugs as False
plug_online_status = [False] * 5

# Create a dictionary of dictionaries to store the data fields
data_fields = {name: [] for name in column_names}

# Initialize the list of dictionaries for energy data for each plug
energy_data_list = [list() for _ in range(5)]

# 'weekday_wake_up_time' for Monday to Friday
weekday_wake_up_time = '06:30'

# 'weekend_wake_up_time' for Saturday and Sunday
weekend_wake_up_time = '09:00'

# Define the cost of 1 kWh of energy (in pounds)
KWH_COST = 0.2889

# Define the telemetry period (in seconds)
TELEMETRY_PERIOD = 10   # In seconds

# File path for the JSON file
file_path = "smart_plug_data.json"

# Initialize the data structure for storing historical power consumption data
smart_plug_data = initialize_data(file_path)

# Create the GUI
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

# Set up the schedules for turning on the heaters in the morning
setup_schedules()

# Start the data fetching in a background thread
fetch_thread = threading.Thread(target=fetch_data, daemon=True)
fetch_thread.start()

# Run the main loop of the GUI
root.mainloop()