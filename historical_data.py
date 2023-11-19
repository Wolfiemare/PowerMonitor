import os
import json
from datetime import datetime, timedelta

# Function to create initial data structure
from datetime import datetime, timedelta

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
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

# Function to load data from JSON
def load_data(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Function to check for existing data or create new data
def initialize_data(file_path):
    if os.path.exists(file_path):
        data_structure = load_data(file_path)
    else:
        data_structure = create_initial_data()
        save_data(file_path, data_structure)  # Save the initial data to the file
    return data_structure

def update_record(plug_id, kWh, cost, date=None, hour=None):
    # If date and hour are not provided, use current date and time
    if date is None:
        date = datetime.now().strftime("%m-%d")
    if hour is None:
        hour = datetime.now().hour

    # Update the record
    smart_plug_data[plug_id][date][hour] = {"kWh": round(kWh, 2), "Cost": round(cost, 2)}

def get_data_for_day(plug_id, date=None):
    # If no date is provided, use today's date
    if date is None:
        date = datetime.now().strftime("%m-%d")

    return smart_plug_data[plug_id][date]


# Example usage
# update_record("Plug1", 5.123, 1.456)  # Updates with current date and time
# update_record("Plug1", 5.123, 1.456, "01-15", 14)  # Updates for Jan 15th at 14:00


# File path for the JSON file
file_path = "smart_plug_data.json"

# Initialize the data structure
smart_plug_data = initialize_data(file_path)

#print(smart_plug_data)
update_record("Plug1", 0.7, 0.1)
save_data(file_path, smart_plug_data)
todays_data = get_data_for_day("Plug1")
print(todays_data[8-1])

