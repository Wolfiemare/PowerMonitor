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
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    update_status("Connected with result code "+str(rc))

    client.subscribe("house/#")  # Subscribe to all topics within 'house/'
    
# Define the MQTT on_message event handler
def on_message(client, userdata, msg):
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

            print(energy_data_list)

    # Check if the plug is online
    if 'LWT' in topic:
        plug_num_str = topic.split('/')[1].replace('Room', '').replace('Plug', '')
        print(plug_num_str)

        if plug_num_str.isdigit():
            plug_num = int(plug_num_str)
            if payload == 'Online':
                plug_online_status[plug_num-1] = True
                update_status(f"Plug {plug_num} is online.")
            else:
                plug_online_status[plug_num-1] = False
                update_status(f"Plug {plug_num} is offline.")



# Define the MQTT on_publish event handler
def on_publish(client, userdata, mid):
    print("Message published with id "+str(mid))
    update_status("Message published with id "+str(mid))

# Function to update the status bar
def update_status(message):
    status_message.config(text=f"Status: {message}")

# Dummy functions for the function buttons
def function1():
    update_status("Function 1 activated.")

def function2():
    update_status("Function 2 activated.")
def function3():
    update_status("Function 3 activated.")

# Function for the exit button
def function4():
    root.quit()  # This will stop the mainloop
    root.destroy()  # This will destroy all widgets and close the window

# Function to fetch data from the plugs
def fetch_data():
    while True:
        # Schedule the `update_data_field` to run on the main thread
        root.after(0, update_data_fields)
        time.sleep(2)  # Simulate delay for fetching data

        # mqtt_client.publish("house/RoomPlug1/cmnd/STATUS", "10")
        # mqtt_client.publish("house/RoomPlug2/cmnd/STATUS", "10")

# Function to update the data fields with data from energy_data_list
def update_data_fields():
    for i, name in enumerate(column_names):
        energy_data = energy_data_list[i]
        
        data_fields[name][12].delete(0, tk.END)
        status = "Online" if plug_online_status[i] else "Offline"
        data_fields[name][12].insert(0, status)
        data_fields[name][12].config(fg="green" if plug_online_status[i] else "red")

        if energy_data:
            # Get the latest energy data for the plug
            latest_energy_data = energy_data[-1]
        
            # Update the data fields with the latest energy data
            data_fields[name][0].delete(0, tk.END)
            data_fields[name][0].insert(0, f"{latest_energy_data['Total']} kWh")
            data_fields[name][1].delete(0, tk.END)
            data_fields[name][1].insert(0, f"{latest_energy_data['Yesterday']} kWh")
            data_fields[name][2].delete(0, tk.END)
            data_fields[name][2].insert(0, f"{latest_energy_data['Today']} kWh")
            data_fields[name][3].delete(0, tk.END)
            data_fields[name][3].insert(0, f"{latest_energy_data['Power']} W")
            data_fields[name][4].delete(0, tk.END)
            data_fields[name][4].insert(0, f"{latest_energy_data['ApparentPower']} VA")
            data_fields[name][5].delete(0, tk.END)
            data_fields[name][5].insert(0, f"{latest_energy_data['ReactivePower']} VAr")
            data_fields[name][6].delete(0, tk.END)
            data_fields[name][6].insert(0, f"{latest_energy_data['Factor']}")
            data_fields[name][7].delete(0, tk.END)
            data_fields[name][7].insert(0, f"{latest_energy_data['Voltage']} V")
            current = latest_energy_data['Current']
            data_fields[name][8].delete(0, tk.END)
            data_fields[name][8].insert(0, f"{current} A")
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
          

# Create the main window
root = tk.Tk()
root.title("Tasmota Power Data Display")
root.geometry("800x480")

# Define a list of column names
column_names = ["Plug 1 - Office", "Plug 2 - Bedroom", "Plug 3", "Plug 4", "Plug 5"]
data_labels =  [
                'TOTAL', 'YESTERDAY', 'TODAY', 'POWER', 'APPARENT POWER', 'REACTIVE POWER', 
                'FACTOR', 'VOLTAGE', 'CURRENT', 'TOTAL COST', 'YESTERDAY COST', 'TODAY COST',
                'STATUS' 
                ]               
                

data_fields = {name: [] for name in column_names}
KWH_COST = 0.2889

# Define the initial online status for the 6 plugs as False
plug_online_status = [False] * 6

# Create a frame for each column and populate it with labels and entry fields
for i, name in enumerate(column_names):
    # Frame for the column
    frame = tk.Frame(root, borderwidth=1, relief="groove")
    frame.place(relx=i/5, rely=0, relwidth=1/5, relheight=0.75)  # Adjusted for function button area

    # Label for the column title
    label = tk.Label(frame, text=name, font=('Helvetica', 12, 'bold'))
    label.pack(side="top", fill="x")

    # Horizontal frames for data labels and fields
    for j in range(13):
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
        

# Function buttons area
func_button_frame = tk.Frame(root, borderwidth=1, relief="sunken")
func_button_frame.place(relx=0, rely=0.75, relwidth=1, relheight=0.1)

# Creating function buttons and assigning commands
func_buttons = [function1, function2, function3, function4]  # function4 is the exit function
button_texts = ["Function 1", "Function 2", "Function 3", "Exit"]
for i, (func, text) in enumerate(zip(func_buttons, button_texts)):
    btn = tk.Button(func_button_frame, text=text, font=('Helvetica', 10), command=func)
    btn.pack(side="left", expand=True, fill="x", padx=5, pady=2)

# Status message box
status_frame = tk.Frame(root, borderwidth=1, relief="sunken")
status_frame.place(relx=0, rely=0.85, relwidth=1, relheight=0.15)
status_message = tk.Label(status_frame, text="Status: Ready", bg="white", anchor="w", font=('Helvetica', 10))
status_message.pack(side="left", fill="both", expand=True)

# Initialize the list of dictionaries for energy data for each plug
energy_data_list = [list() for _ in range(5)]

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
