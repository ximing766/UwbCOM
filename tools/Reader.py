import tkinter as tk
from tkinter import scrolledtext
import serial
import serial.tools.list_ports
import threading
import ttkbootstrap as ttk
import time

class SerialAssistant:
    def __init__(self, master):
        self.master = master
        self.master.title("Reader")

        self.serial = None
        self.is_running = False
        self.read_data_res = "0000FFA70005FFFFFFFFFF06FFFFFFFFFF28C20211805003020B01000000010409000100010F8580DC12D08027127D010100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001901023B7227000000000000000000000000000000000000000000001700"
        self.write_data_res = "0000FF250005FFFFFFFFFF06FFFFFFFFFF2AC20115805401000F0000000120240821185844B2568CE5087600"
        self.halt_data_res =  "0000FF100005FFFFFFFFFF06FFFFFFFFFF44CA0000F100"
        self.flag = 0

        self.sequence = "06FFFFFFFFFF05FFFFFFFFFF"

        # GUI 设置
        master.grid_columnconfigure(0, weight=1)
        master.grid_columnconfigure(1, weight=1)
        master.grid_columnconfigure(2, weight=1)
        master.grid_columnconfigure(3, weight=1)
        master.grid_columnconfigure(4, weight=1)
        master.grid_columnconfigure(5, weight=1)
        self.text_area = ttk.ScrolledText(master, width=100, height=40)
        self.text_area.grid(column=0, row=0, columnspan=6, padx=10, pady=10,sticky='nsew')

        self.port_label = ttk.Label(master, text="选择串口:",bootstyle="primary")
        self.port_label.grid(column=0, row=1, padx=10, pady=10,sticky='nsew')

        self.baudrate_label = ttk.Label(master, text="波特率:",bootstyle="primary")
        self.baudrate_label.grid(column=2, row=1, padx=10, pady=10,sticky='nsew')

        self.port_options = self.get_serial_ports()
        self.port_var = tk.StringVar(master)
        if self.port_options:  # 检查是否有可用的串口
            self.port_var.set(self.port_options[0])  # 默认选择第一个串口
        else:
            self.port_var.set('')  # 如果没有串口，设置为空字符串
        self.port_menu = ttk.OptionMenu(master, self.port_var, *self.port_options,bootstyle="primary")
        self.port_menu.grid(column=1, row=1, padx=10, pady=10,sticky='nsew')

        self.baudrate_var = tk.IntVar(master, 115200)  # 默认波特率9600
        self.baudrate_menu = ttk.OptionMenu(master, self.baudrate_var, 115200, 3000000, 9600,bootstyle="primary")
        self.baudrate_menu.grid(column=3, row=1, padx=10, pady=10,sticky='nsew')

        self.connect_button = ttk.Button(master, text="连接", command=self.connect,bootstyle="primary")
        self.connect_button.grid(column=4, row=1, padx=10, pady=10,sticky='nsew')

        self.disconnect_button = ttk.Button(master, text="断开连接", command=self.disconnect,bootstyle="primary")
        self.disconnect_button.grid(column=5, row=1, padx=10, pady=10,sticky='nsew')

        self.disconnect_button.config(state=tk.DISABLED)

        self.send_button = ttk.Button(master, text="发送数据", command=self.send_data,bootstyle="primary")
        self.send_button.grid(column=0, row=2, padx=10, pady=10,sticky='nsew')

        self.data_entry = ttk.Entry(master,bootstyle="primary")
        self.data_entry.grid(column=1, row=2, columnspan=5, padx=10, pady=10,sticky='nsew')

        # self.update_senddata()

    def update_senddata(self):
        self.send_data(self.halt_data_res)
        self.master.after(500, self.update_senddata)  # 每隔1秒调用一次
            
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
                self.serial = serial.Serial(self.port_var.get(), self.baudrate_var.get(), timeout=0.05)
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

    def Apdu_Handle(self, data, sequence):
        data_upper = data.upper()
        sequence_upper = sequence.upper()
        # 使用find方法查找sequence_upper在data_upper中的下标
        index = data_upper.find(sequence_upper)
        if index != -1:
            # print(f"Sequence found at index: {index}")
            # 根据你的逻辑处理找到的序列
            if data_upper[index+26:index+28] == 'C9' and self.flag == 0:    # return 8050,80dc
                # print(data_upper[index:index+30])
                self.send_data(self.read_data_res)
                self.current_time = time.time()
                print(f"Send data time={self.current_time}")        
                self.flag += 1
            elif data_upper[index+26:index+28] == 'C3' and self.flag == 1:   #return 8054
                # print(data_upper[index:index+30])
                self.send_data(self.write_data_res)
                self.current_time = time.time()
                print(f"Send data time={self.current_time}")
                self.flag += 1
            elif data_upper[index+26:index+28] == 'C3' and self.flag == 2:   #return halt
                self.send_data(self.halt_data_res)
                self.current_time = time.time()
                print(f"Send data time={self.current_time}")
                self.flag = 0
        else:
            print("Sequence not found") 
    def read_data(self):
        while self.is_running:
            try:
                if data := self.serial.readline():
                    self.Apdu_Handle(data.hex(), self.sequence)
                    self.current_time = time.time()
                    print(f"Read Data time={self.current_time}")
                    self.show_in_text_area(data.hex())
            except Exception as e:
                self.show_in_text_area(f"Read data failed!!!: {e}")

    def send_data(self, hex_data=None):
        if hex_data is None:
            hex_data = self.data_entry.get()
        try:
            if len(hex_data) % 2 != 0:
                self.show_in_text_area("Error:16进制数据长度应为偶数")
                return

            # 将16进制字符串转换为字节
            byte_data = bytes.fromhex(hex_data)

            if self.serial and self.serial.is_open:
                self.serial.write(byte_data)
                self.show_in_text_area(f"发送: {hex_data}")
            else:
                self.show_in_text_area("错误：串口未打开")
        except ValueError as e:
            self.show_in_text_area(f"发送数据失败：{e}")

    def show_in_text_area(self, message):
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.see(tk.END)

root = tk.Tk()
app = SerialAssistant(root)
root.mainloop()