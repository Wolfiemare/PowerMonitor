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

    client.subscribe("house/RoomPlug1/stat/STATUS10", qos=0)
    client.subscribe("house/RoomPlug2/stat/STATUS10", qos=0)

# Define the MQTT on_message event handler
def on_message(client, userdata, msg):
    print(f"Topic: {msg.topic} Message: {msg.payload.decode('utf-8')}")
    topic = msg.topic
    payload = msg.payload.decode('utf-8')
    
    print(f"Topic: {topic} Message: {payload}")
    update_status(f"Topic: {topic} Message: {payload}")

    data = json.loads(payload)['StatusSNS']['ENERGY']
    # if 'RoomPlug1' in topic:
    #     window.write_event_value('-ENERGY1-', data)
    # elif 'RoomPlug2' in topic:
    #     window.write_event_value('-ENERGY2-', data)

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
        # Simulate data retrieval with random numbers
        new_data = {name: random.randint(50, 200) for name in column_names}
        # Update GUI with new data in a thread-safe way
        for name, data in new_data.items():
            # Schedule the `update_data_field` to run on the main thread
            root.after(0, update_data_field, name, data)
        time.sleep(2)  # Simulate delay for fetching data

        mqtt_client.publish("house/RoomPlug1/cmnd/STATUS", "10")
        mqtt_client.publish("house/RoomPlug2/cmnd/STATUS", "10")

# Function to update the data fields
def update_data_field(plug_name, data):
    for i, entry in enumerate(data_fields[plug_name]):
        entry.delete(0, tk.END)  # Clear the current entry
        entry.insert(0, f"{data + i*10}W")    # Insert new data with a unique increment

# Create the main window
root = tk.Tk()
root.title("Tasmota Power Data Display")
root.geometry("800x480")

# Define a list of column names
column_names = ["Plug 1", "Plug 2", "Plug 3", "Plug 4", "Plug 5"]
data_fields = {name: [] for name in column_names}

# Create a frame for each column and populate it with labels and entry fields
for i, name in enumerate(column_names):
    # Frame for the column
    frame = tk.Frame(root, borderwidth=1, relief="groove")
    frame.place(relx=i/5, rely=0, relwidth=1/5, relheight=0.75)  # Adjusted for function button area

    # Label for the column title
    label = tk.Label(frame, text=name, font=('Helvetica', 10, 'bold'))
    label.pack(side="top", fill="x")

    # Horizontal frames for data labels and fields
    for j in range(6):
        # Frame for each data row
        data_frame = tk.Frame(frame)
        data_frame.pack(side="top", fill="x", padx=2, pady=1)

        # Data label
        data_label = tk.Label(data_frame, text=f"Data {j+1}:", width=8, anchor="w", font=('Helvetica', 8))
        data_label.pack(side="left")

        # Data field
        data_field = tk.Entry(data_frame, font=('Helvetica', 8))
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

# Initiate MQTT Client
mqtt_client = mqtt.Client()
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
