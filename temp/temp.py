import tkinter as tk
from tkinter import scrolledtext
import serial
import serial.tools.list_ports
import threading

class SerialAssistant:
    def __init__(self, master):
        self.master = master
        self.master.title("Reader")

        self.serial = None
        self.is_running = False

        # GUI 设置
        self.text_area = scrolledtext.ScrolledText(master, width=100, height=50)
        self.text_area.grid(column=0, row=0, columnspan=4, padx=10, pady=10)

        self.port_label = tk.Label(master, text="选择串口:")
        self.port_label.grid(column=0, row=1, padx=10, pady=10)

        self.baudrate_label = tk.Label(master, text="波特率:")
        self.baudrate_label.grid(column=1, row=1, padx=10, pady=10)

        self.port_options = self.get_serial_ports()
        self.port_var = tk.StringVar(master)
        if self.port_options:  # 检查是否有可用的串口
            self.port_var.set(self.port_options[0])  # 默认选择第一个串口
        else:
            self.port_var.set('')  # 如果没有串口，设置为空字符串
        self.port_menu = tk.OptionMenu(master, self.port_var, *self.port_options)
        self.port_menu.grid(column=0, row=2, padx=10, pady=10)

        self.baudrate_var = tk.IntVar(master, 115200)  # 默认波特率9600
        self.baudrate_menu = tk.OptionMenu(master, self.baudrate_var, 9600, 3000000, 115200)
        self.baudrate_menu.grid(column=1, row=2, padx=10, pady=10)

        self.connect_button = tk.Button(master, text="连接", command=self.connect)
        self.connect_button.grid(column=2, row=2, padx=10, pady=10)

        self.disconnect_button = tk.Button(master, text="断开连接", command=self.disconnect)
        self.disconnect_button.grid(column=3, row=2, padx=10, pady=10)

        self.disconnect_button.config(state=tk.DISABLED)

        self.send_button = tk.Button(master, text="发送数据", command=self.send_data)
        self.send_button.grid(column=2, row=1, padx=10, pady=10)

        self.data_entry = tk.Entry(master)
        self.data_entry.grid(column=3, row=1, padx=10, pady=10)

    def get_serial_ports(self):
        """获取系统上的所有可用串口"""
        ports = []
        try:
            ports = serial.tools.list_ports.comports()
            ports = [port.device for port in ports]
        except Exception as e:
            self.show_in_text_area(f"获取串口列表失败: {e}")
        return ports

    def connect(self):
        try:
            if self.port_var.get():
                self.serial = serial.Serial(self.port_var.get(), self.baudrate_var.get(), timeout=1)
                self.is_running = True
                self.connect_button.config(state=tk.DISABLED)
                self.disconnect_button.config(state=tk.ACTIVE)
                self.start_read()
            else:
                self.show_in_text_area("请选择一个串口")
        except Exception as e:
            self.show_in_text_area(f"连接失败: {e}")

    def disconnect(self):
        if self.serial:
            self.serial.close()
        self.is_running = False
        self.connect_button.config(state=tk.NORMAL)
        self.disconnect_button.config(state=tk.DISABLED)

    def start_read(self):
        if self.is_running:
            threading.Thread(target=self.read_data).start()

    def read_data(self):
        while self.is_running:
            try:
                if self.serial.in_waiting > 0:
                    data = self.serial.readline().decode('utf-8').rstrip()
                    self.show_in_text_area(data)
                    if data == "特定数据":  # 替换为你的特定数据
                        self.send_data("特定响应")  # 替换为你的特定响应
            except Exception as e:
                self.show_in_text_area(f"读取数据失败: {e}")

    def send_data(self, data=None):
        if data is None:
            data = self.data_entry.get()
        try:
            if self.serial and self.serial.is_open:
                self.serial.write(data.encode('utf-8'))
                self.show_in_text_area(f"发送: {data}")
        except Exception as e:
            self.show_in_text_area(f"发送数据失败: {e}")

    def show_in_text_area(self, message):
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.see(tk.END)

root = tk.Tk()
app = SerialAssistant(root)
root.mainloop()