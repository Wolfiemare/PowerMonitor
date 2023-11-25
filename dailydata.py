import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
from datetime import datetime, timedelta

def display_data_window(data):
    # Create a new Tkinter window
    window = tk.Toplevel(root)
    window.title("Smart Plug Data")
    window.geometry("800x470")

    # Function to create labels for data
    def create_data_labels(row_start, data_subset, row_offset):
        # Create column headers
        for col, text in enumerate(['Hour', 'kWh', 'Cost']):
            header = tk.Label(window, text=text, font=('Arial', 10, 'bold'))
            header.grid(row=row_offset, column=col + 4 * (row_start // 12), padx=5, pady=0)

        # Create data labels
        for i, record in enumerate(data_subset):
            hour_label_text = f"{(row_start + i) % 24:02d}:00 - {(row_start + i + 1) % 24:02d}:00"
            hour_label = tk.Label(window, text=hour_label_text, width=15)
            hour_label.grid(row=row_offset + i + 1, column=0 + 4 * (row_start // 12), padx=5, pady=0)

            for j, key in enumerate(['kWh', 'Cost']):
                cell = tk.Label(window, text=f"{record[key]:.2f}", width=8)
                cell.grid(row=row_offset + i + 1, column=j + 1 + 4 * (row_start // 12), padx=5, pady=0)

    # Split data into two halves for two columns
    first_half, second_half = data[:12], data[12:]

    # Create data labels for both halves, offset by 2 rows to leave space for the control frame
    create_data_labels(0, first_half, 2)
    create_data_labels(12, second_half, 2)

    # Create a frame for the control elements
    control_frame = tk.Frame(window)
    control_frame.grid(row=0, column=0, columnspan=8, sticky='ew', padx=5, pady=5)

    # Place the controls in the control frame
    date_label = tk.Label(control_frame, text="Select Date:")
    date_label.pack(side='left', padx=(0, 10))

    today = datetime.now()
    calendar = Calendar(control_frame, selectmode='day', year=today.year, month=today.month, day=today.day)
    calendar.pack(side='left', fill='x', expand=True)

    plug_label = tk.Label(control_frame, text="Select Plug:")
    plug_label.pack(side='left', padx=(10, 0))

    plug_selector = ttk.Combobox(control_frame, values=["Plug1", "Plug2", "Plug3", "Plug4", "Plug5"], state="readonly", width=10)
    plug_selector.pack(side='left', padx=(0, 10))
    plug_selector.set("Plug1")  # Default selection

    exit_button = tk.Button(control_frame, text="Exit", command=window.destroy)
    exit_button.pack(side='left')

def get_data_for_day():
    # Sample data - Replace this with actual data retrieval logic
    return [{'kWh': i*0.1, 'Cost': i*0.05} for i in range(24)]

# Example usage
root = tk.Tk()
root.geometry("200x100")
test_button = tk.Button(root, text="Show Data", command=lambda: display_data_window(get_data_for_day()))
test_button.pack()
root.mainloop()
