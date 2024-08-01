import tkinter as tk
from tkinter import filedialog
import serial
import time

def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("Bin Files", "*.bin")])
    if file_path:
        # Code to burn the bin file to the development board
        # Replace this with your actual programming logic
        print(f"Selected file: {file_path}")
        print("Programming in progress...")
        time.sleep(2)  # Simulating programming process
        print("Programming completed!")

def burn_file():

    selected_port = port_var.get()
    selected_baudrate = baudrate_var.get()
    if selected_port and selected_baudrate:
        print(f"Selected port: {selected_port}")
        print(f"Selected baud rate: {selected_baudrate}")
        select_file()

root = tk.Tk()
root.title("Bin File Burner")

# Serial Port Selection
port_label = tk.Label(root, text="Serial Port:")
port_label.pack()
port_var = tk.StringVar(root)
import serial.tools.list_ports

port_dropdown = tk.OptionMenu(root, port_var, *serial.tools.list_ports.comports())
port_dropdown.pack()

# Baud Rate Selection
baudrate_label = tk.Label(root, text="Baud Rate:")
baudrate_label.pack()
baudrate_var = tk.IntVar(root)
baudrate_dropdown = tk.OptionMenu(root, baudrate_var, 9600, 115200, 230400, 460800)
baudrate_dropdown.pack()

# Burn Button
burn_button = tk.Button(root, text="Burn File", command=burn_file)
burn_button.pack()

root.mainloop()