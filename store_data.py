import json
import os
from datetime import datetime

# ...

def store_data(plug_num, latest_energy_data):
    # Check if the data directory exists, if not, create it
    if not os.path.exists("data"):
        os.mkdir("data")

    # Check if the file for the current plug exists, if not, create it
    filename = f"data/plug{plug_num}.json"
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            json.dump({}, f)

    # Load the data from the file into a dictionary
    with open(filename, "r") as f:
        data = json.load(f)

    # Add the latest energy data to the dictionary with the current date and hour as the key
    now = datetime.now()
    key = now.strftime("%Y-%m-%d %H:%M:%S")
    data[key] = latest_energy_data["Today"]

    # If the dictionary has more than 24 entries, remove the oldest entry
    if len(data) > 24:
        oldest_key = min(data.keys())
        del data[oldest_key]

    # Write the updated dictionary to the file
    with open(filename, "w") as f:
        json.dump(data, f)

def fetch_data():
    while True:
        # ...

        if energy_data:
            # Get the latest energy data for the plug
            latest_energy_data = energy_data[-1]

            # Update the data fields with the latest energy data
            # ...

            # Store the latest energy data in a JSON file
            store_data(i+1, latest_energy_data)

        # ...

        time.sleep(3600)  # Wait for 1 hour before fetching data again
