import json
import pandas as pd
import tkinter as tk
from tkinter.filedialog import askopenfilename

def read_json_plug_data(file_path):
    # Read the JSON file
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Process and save data for each plug
    for plug in range(1, 6):  # From Plug1 to Plug5
        plug_key = f'Plug{plug}'
        print(f"Processing data for {plug_key}...")

        if plug_key in data:
            dates = []
            kWh_values = []
            cost_values = []

            for date, daily_data in data[plug_key].items():
                dates.append(date)
                kWh_values.append(daily_data.get('kWh', 0))
                cost_values.append(daily_data.get('Cost', 0))

            # Create a DataFrame and save it to an Excel file
            df = pd.DataFrame({'Date': dates, 'kWh': kWh_values, 'Cost': cost_values})
            excel_file_name = f'{plug_key}_data.xlsx'
            df.to_excel(excel_file_name, index=False)
            print(f"Data saved to {excel_file_name}")

        else:
            print(f"No data available for {plug_key}")

def select_file():
    root = tk.Tk()
    root.withdraw()  # We don't want a full GUI, so keep the root window from appearing
    file_path = askopenfilename(filetypes=[("JSON files", "*.json")])  # Show an "Open" dialog box and return the path to the selected file
    if file_path:  # If a file was selected
        read_json_plug_data(file_path)

select_file()
