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
        self.read_data_res = "0000FFA70005FFFFFFFFFF06FFFFFFFFFF28C20211805003020B01000000010409000100010F8580DC12D08027127D010100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001901023B7227000000000000000000000000000000000000000000001700"
        self.write_data_res = "0000FF250005FFFFFFFFFF06FFFFFFFFFF2AC20115805401000F0000000120240821185844B2568CE5087600"


        self.sequence = "06FFFFFFFFFF05FFFFFFFFFF"

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

    def Apdu_Handle(self, data, sequence):
        data_upper = data.upper()
        sequence_upper = sequence.upper()
        # 使用find方法查找sequence_upper在data_upper中的下标
        index = data_upper.find(sequence_upper)
        if index != -1:
            print(f"Sequence found at index: {index}")
            # 根据你的逻辑处理找到的序列
            if data_upper[index+26:index+28] == 'C9':
                # print(data_upper[index:index+30])
                self.send_data(self.read_data_res) 
            elif data_upper[index+26:index+28] == 'C3':
                # print(data_upper[index:index+30])
                self.send_data(self.write_data_res)  
        else:
            print("Sequence not found") 
    def read_data(self):
        while self.is_running:
            try:
                if data := self.serial.readline():
                    self.show_in_text_area(data.hex())
                    self.Apdu_Handle(data.hex(), self.sequence)
            except Exception as e:
                self.show_in_text_area(f"读取数据失败: {e}")

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