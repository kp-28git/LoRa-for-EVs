import tkinter as tk
from tkinter import ttk, scrolledtext
import serial
import serial.tools.list_ports
import threading
import time
import datetime


class SerialMonitorApp:
    def __init__(self, root):  # Corrected method name
        self.root = root
        self.root.title("Vehicle Monitoring System")
        self.root.geometry("800x600")

        # Customize styles
        style = ttk.Style()
        style.configure("TFrame", background="#f0f0f5")
        style.configure("TLabel", background="#f0f0f5", font=("Helvetica", 12))
        style.configure("Title.TLabel", font=("Helvetica", 16, "bold"), foreground="#333")
        style.configure("TButton", font=("Helvetica", 12), padding=5)

        self.serial_connection = None

        # Create Notebook (Tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both")

        # Create Tabs
        self.create_home_tab()
        self.create_serial_monitor_tab()


    def create_home_tab(self):
        # Home Tab
        self.home_frame = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(self.home_frame, text='Home')

        # Layout frames within Home Tab
        self.home_main_frame = ttk.Frame(self.home_frame, style="TFrame")
        self.personal_details_frame = ttk.Frame(self.home_frame, style="TFrame")
        self.request_charge_frame = ttk.Frame(self.home_frame, style="TFrame")
        self.inbox_frame = ttk.Frame(self.home_frame, style="TFrame")

        # Show main home options initially
        self.home_main_frame.pack(fill='both', expand=True, padx=20, pady=20, side='left')
        self.inbox_frame.pack(fill='y', padx=20, pady=20, side='right')

        # === Inbox Frame ===
        self.inbox_box = ttk.Label(self.inbox_frame, text="Inbox", style="Title.TLabel")
        self.inbox_box.pack(pady=10)

        self.inbox_display = scrolledtext.ScrolledText(self.inbox_frame, wrap=tk.WORD, height=10, width=40)
        self.inbox_display.pack(pady=10)

        self.accept_button = ttk.Button(self.inbox_frame, text="Yes", command=lambda: self.send_data("Y"))
        self.decline_button = ttk.Button(self.inbox_frame, text="No", command=lambda: self.send_data("N"))

        self.accept_button.pack_forget()
        self.decline_button.pack_forget()

        # === Home Main Frame ===
        ttk.Label(self.home_main_frame, text="Vehicle Monitoring System", style="Title.TLabel").pack(pady=20)

        personal_btn = ttk.Button(self.home_main_frame, text="Personal Details", command=self.show_personal_details)
        personal_btn.pack(pady=10)

        request_charge_btn = ttk.Button(self.home_main_frame, text="Request for Charge", command=self.request_charge)
        request_charge_btn.pack(pady=10)

        # === Personal Details Frame ===
        ttk.Label(self.personal_details_frame, text="Personal Details", style="Title.TLabel").pack(pady=20)

        details = {
            "Owner Name": "Neel Patel",
            "Vehicle Number": "GJ06LS1150",
            "Model": "Skoda Superb",
            "Chassis Number": "MA3EYD32S007004AN"
        }

        for key, value in details.items():
            ttk.Label(self.personal_details_frame, text=f"{key}: {value}", style="TLabel").pack(pady=5)

        back_btn_pd = ttk.Button(self.personal_details_frame, text="Back", command=self.show_home_main)
        back_btn_pd.pack(pady=20)

        # === Request Charge Frame ===
        ttk.Label(self.request_charge_frame, text="Request for Charge", style="Title.TLabel").pack(pady=20)

        self.charge_status_label = ttk.Label(self.request_charge_frame, text="Status: Idle", font=("Helvetica", 12, "italic"), background="#f0f0f5")
        self.charge_status_label.pack(pady=10)

        # Keypad frame for entering charging capacity
        self.keypad_frame = ttk.Frame(self.request_charge_frame)
        self.keypad_frame.pack(pady=10)

        self.charging_capacity = ""  # Store the current input

        # Create buttons for keypad
        self.create_keypad()

        back_btn_rc = ttk.Button(self.request_charge_frame, text="Back", command=self.show_home_main)
        back_btn_rc.pack(pady=20)

        # === Date and Battery Capacity ===
        self.date_label = ttk.Label(self.home_main_frame, text="", style="TLabel")
        self.date_label.pack(pady=10)
        self.update_date()

        self.battery_label = ttk.Label(self.home_main_frame, text="Battery Capacity: 85%", style="TLabel")
        self.battery_label.pack(pady=5)

    def show_personal_details(self):
        self.home_main_frame.pack_forget()
        self.personal_details_frame.pack(fill='both', expand=True)

    def show_home_main(self):
        self.personal_details_frame.pack_forget()
        self.request_charge_frame.pack_forget()
        self.home_main_frame.pack(fill='both', expand=True, padx=20, pady=20, side='right')
        self.inbox_frame.pack(fill='y', padx=20, pady=20, side='left')

    def request_charge(self):
        # Switch to Request Charge Frame
        self.home_main_frame.pack_forget()
        self.request_charge_frame.pack(fill='both', expand=True)

        # Update status
        self.charge_status_label.config(text="Status: Waiting for charging capacity input...")

        # Immediately send "S" to the serial monitor
        self.send_data("S")

    def create_keypad(self):
        # Create numeric keypad buttons (0-9)
        for row in range(3):
            for col in range(3):
                num = row * 3 + col + 1
                button = ttk.Button(self.keypad_frame, text=str(num), command=lambda num=num: self.append_digit(num))
                button.grid(row=row, column=col, padx=5, pady=5, ipadx=10, ipady=10)

        # Add 0 button
        zero_button = ttk.Button(self.keypad_frame, text="0", command=lambda: self.append_digit(0))
        zero_button.grid(row=3, column=1, padx=5, pady=5, ipadx=10, ipady=10)

        # Add Backspace button (renamed from 'Back')
        backspace_button = ttk.Button(self.keypad_frame, text="Back", command=self.delete_digit)
        backspace_button.grid(row=3, column=0, padx=5, pady=5, ipadx=10, ipady=10)

        # Add Enter button to send the entered charging capacity
        enter_button = ttk.Button(self.keypad_frame, text="Enter", command=self.send_charge_capacity)
        enter_button.grid(row=3, column=2, padx=5, pady=5, ipadx=10, ipady=10)

    def append_digit(self, digit):
        self.charging_capacity += str(digit)
        self.charge_status_label.config(text=f"Status: {self.charging_capacity}W")

    def delete_digit(self):
        self.charging_capacity = self.charging_capacity[:-1]
        self.charge_status_label.config(text=f"Status: {self.charging_capacity}W")

    def send_charge_capacity(self):
        # Send the charging capacity to the serial monitor
        if self.charging_capacity:
            self.send_data(self.charging_capacity)  # Send the entered value

            # After sending, switch to home tab
            self.show_home_main()

            # Display request sent message and reset after 5 seconds
            self.charge_status_label.config(text=f"Request for {self.charging_capacity}kWh sent, Waiting for Response")

            # Reset status after 5 seconds
            self.root.after(5000, lambda: self.charge_status_label.config(text="Status: Idle"))

            # Reset the input field after sending
            self.charging_capacity = "" 

    def update_date(self):
        self.date_label.config(text=f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.root.after(1000, self.update_date)

    def create_serial_monitor_tab(self):
        self.monitor_frame = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(self.monitor_frame, text="Serial Monitor")

        settings_frame = ttk.LabelFrame(self.monitor_frame, text="Serial Settings", style="TFrame")
        settings_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(settings_frame, text="Port:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.serial_ports = ttk.Combobox(settings_frame, values=[], width=30)
        self.serial_ports.grid(row=0, column=1, padx=5, pady=5)
        self.serial_ports.set("COM5")

        ttk.Label(settings_frame, text="Baud Rate:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.baud_rates = ttk.Combobox(settings_frame, values=["9600", "115200", "250000"], width=30)
        self.baud_rates.set("115200")
        self.baud_rates.grid(row=1, column=1, padx=5, pady=5)

        open_btn = ttk.Button(settings_frame, text="Open", command=self.open_serial_connection)
        open_btn.grid(row=2, column=0, columnspan=2, pady=10)

        self.output_text = scrolledtext.ScrolledText(self.monitor_frame, wrap=tk.WORD, height=20, width=80)
        self.output_text.pack(padx=10, pady=10)

        close_btn = ttk.Button(self.monitor_frame, text="Close", command=self.close_serial_connection)
        close_btn.pack(pady=10)

    def open_serial_connection(self):
        try:
            selected_port = self.serial_ports.get()
            baud_rate = self.baud_rates.get()
            self.serial_connection = serial.Serial(selected_port, baud_rate, timeout=1)
            self.serial_connection.flush()
            self.output_text.insert(tk.END, f"Connected to {selected_port} at {baud_rate} baud\n")
            self.output_text.see(tk.END)
            self.receive_thread = threading.Thread(target=self.receive_data)
            self.receive_thread.daemon = True
            self.receive_thread.start()
        except Exception as e:
            self.output_text.insert(tk.END, f"Error: {e}\n")
            self.output_text.see(tk.END)

    def close_serial_connection(self):
        if self.serial_connection:
            self.serial_connection.close()
            self.output_text.insert(tk.END, "Disconnected\n")
            self.output_text.see(tk.END)

    def send_data(self, data):
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.write(data.encode())
            self.output_text.insert(tk.END, f"Sent: {data}\n")
            self.output_text.see(tk.END)

    def receive_data(self):
        while True:
            if self.serial_connection.in_waiting > 0:
                message = self.serial_connection.readline().decode('utf-8').strip()
                self.output_text.insert(tk.END, f"Received: {message}\n")
                self.output_text.see(tk.END)
                self.handle_inbox(message)

    def handle_inbox(self, message):
        # Display message in inbox box
        self.inbox_display.insert(tk.END, f"Received: {message}\n")
        self.inbox_display.see(tk.END)

        # Check for capacity requests
        if "Requested capacity is within the limits." in message:
            self.accept_button.pack(pady=5)
            self.decline_button.pack(pady=5)
        else:
            self.accept_button.pack_forget()
            self.decline_button.pack_forget()


if __name__ == "__main__":
    root = tk.Tk()
    app = SerialMonitorApp(root)
    root.mainloop()
