import tkinter as tk
from tkinter import scrolledtext
import serial
import serial.tools.list_ports
import threading
import ttkbootstrap as ttk
import customtkinter
import ctypes
import time

class SerialAssistant:
    def __init__(self, master):
        self.master = master
        self.master.title("Reader")
        self.master.minsize(650, 600)
        self.master.geometry("650x600")
        self.my_lib = ctypes.WinDLL("./tools/libRSCode.dll")
        self.my_lib.initialize_ecc()
        self.my_lib.encode_data.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte)]
        self.my_lib.encode_data.restype = None

        self.serial = None
        self.is_running = False
        
        # self.read_data_res = "0000FFA70005FFFFFFFFFF06FFFFFFFFFF28C20211805003020B01000000010409000100010F8580DC12D08027127D010100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001901023B7227000000000000000000000000000000000000000000001700778AB54891E0D22DF4AE"                      
        # self.write_data_res = "0000FF250005FFFFFFFFFF06FFFFFFFFFF2AC20115805401000F0000000120240821185844B2568CE5087600FFF6DBA8F9B8CBEBB13A"
        # self.halt_data_res =  "0000FF100005FFFFFFFFFF06FFFFFFFFFF44CA0000F100F5D4543F960BEFB499F1"

        self.read_data_res = bytes([0x00,0x00,0xFF,0xA7,0x00,0x05,0xFF,0xFF,0xFF,0xFF,0xFF,0x06,0xFF,0xFF,0xFF,0xFF,0xFF,0x28,0xC2,0x02,0x11,0x80,0x50,0x03,0x02,0x0B,
                                    0x01,0x00,0x00,0x00,0x01,0x04,0x09,0x00,0x01,0x00,0x01,0x0F,0x85,0x80,0xDC,0x12,0xD0,0x80,0x27,0x12,0x7D,0x01,0x01,0x00,0x00,0x00,
                                    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                                    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                                    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                                    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x19,0x01,0x02,0x3B,0x72,0x27,0x00,0x00,0x00,0x00,0x00,0x00,
                                    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x17,0x00])
        self.write_data_res = bytes([0x00,0x00,0xFF,0x25,0x00,0x05,0xFF,0xFF,0xFF,0xFF,0xFF,0x06,0xFF,0xFF,0xFF,0xFF,0xFF,0x2A,0xC2,0x01,0x15,0x80,0x54,0x01,0x00,0x0F,
                                     0x00,0x00,0x00,0x01,0x20,0x24,0x08,0x21,0x18,0x58,0x44,0xB2,0x56,0x8C,0xE5,0x08,0x76,0x00])
        self.halt_data_res =  bytes([0x00, 0x00, 0xFF, 0x10, 0x00, 0x05, 0xFF, 0xFF, 0xFF, 0xFF,0xFF, 0x06, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x44, 0xCA, 0x00, 0x00, 0xF1, 0x00])
        self.read_data_res = self.RS_Encode(self.read_data_res)
        self.write_data_res = self.RS_Encode(self.write_data_res)
        self.halt_data_res = self.RS_Encode(self.halt_data_res)

        old_part = self.read_data_res[-29:-23]
        new_part = "010203"
        self.read_data_res = self.read_data_res[:-29] + new_part + self.read_data_res[-23:]
        print(f'read_data_res: {self.read_data_res}')


        self.flag = 0
        self.sequence = "06FFFFFFFFFF05FFFFFFFFFF"

        # GUI 设置
        master.grid_columnconfigure(0, weight=1)
        master.grid_columnconfigure(1, weight=1)
        master.grid_columnconfigure(2, weight=1)
        master.grid_columnconfigure(3, weight=1)
        master.grid_columnconfigure(4, weight=1)
        master.grid_columnconfigure(5, weight=1)
        self.text_area = customtkinter.CTkTextbox(master, width=400, height=450,  fg_color=("#A0C8CF"))
        self.text_area.grid(column=0, row=0, columnspan=6, padx=10, pady=10,sticky='nsew')

        self.port_label = customtkinter.CTkLabel(master, text="COM Settings:", corner_radius = 10, fg_color= ("#A0C8CF"), font=("Roboto", 15))
        self.port_label.grid(column=0, row=1, padx=10, pady=10,sticky='nsew')

        self.port_options = self.get_serial_ports()
        self.port_var = tk.StringVar(master)
        if self.port_options:  # 检查是否有可用的串口
            self.port_var.set(self.port_options[0])  # 默认选择第一个串口
        else:
            self.port_var.set('')  # 如果没有串口，设置为空字符串
        self.port_menu = customtkinter.CTkOptionMenu(master, variable=self.port_var, values=[*self.port_options], font=("Roboto", 15))
        self.port_menu.grid(column=1, row=1, padx=10, pady=10,sticky='nsew')

        self.baudrate_var = tk.IntVar(master, 460800)  # 默认波特率9600
        self.baudrate_menu = customtkinter.CTkOptionMenu(master, variable=self.baudrate_var, values = ["460800", "115200", "3000000", "9600"], font=("Roboto", 15))
        self.baudrate_menu.grid(column=2, row=1, padx=10, pady=10,sticky='nsew')

        self.segemented_button = customtkinter.CTkSegmentedButton(master, values=["Connect", "Disconnect"], command=self.segmented_button_callback, font=("Roboto", 15), width=280)
        self.segemented_button.grid(column=3, columnspan=2, row=1, padx=10, pady=10,sticky='nsew')
        self.segemented_button.set("Disconnect")

        self.send_button = customtkinter.CTkButton(master, text="Send", command=self.send_data, font=("Roboto", 15))
        self.send_button.grid(column=0, row=2, padx=10, pady=10,sticky='nsew')

        self.data_entry = customtkinter.CTkEntry(master,placeholder_text="Please input data...", font=("Roboto", 15))
        self.data_entry.grid(column=1, row=2, columnspan=3, padx=10, pady=10,sticky='nsew')

        self.clear_button = customtkinter.CTkButton(master, text="Clear", command=self.clear_text_area, font=("Roboto", 15))
        self.clear_button.grid(column=4, row=2, padx=10, pady=10, sticky='nsew')

        # self.update_senddata()
    
    def RS_Encode(self, data):
        codeword = (ctypes.c_ubyte * (len(data) + 10))()
        self.my_lib.encode_data((ctypes.c_ubyte * len(data)).from_buffer_copy(data), len(data), codeword)
        # result = bytes(codeword)
        hex_string = ''.join(f'{byte:02x}' for byte in bytes(codeword))
        print("Encoded data:", hex_string)
        return hex_string
    
    def clear_text_area(self):
        self.text_area.delete(1.0, tk.END)  # 清除文本框内容
    
    def segmented_button_callback(self, value):
        if value == "Connect":
            self.connect()
        elif value == "Disconnect":
            self.disconnect()

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
                self.serial = serial.Serial(self.port_var.get(), self.baudrate_var.get(), timeout=0.05)   # reader 50ms返回
                self.is_running = True
                # self.connect_button.configure(state=tk.DISABLED)
                # self.disconnect_button.configure(state=tk.ACTIVE)
                self.start_read()
                self.show_in_text_area(f"串口已打开: {self.port_var.get()} {self.baudrate_var.get()}")
            else:
                self.show_in_text_area("请选择一个串口")
        except Exception as e:
            self.show_in_text_area(f"连接失败: {e}")

    def disconnect(self):
        if self.serial:
            self.serial.close()
        self.is_running = False
        self.show_in_text_area(f"串口已关闭")
        # self.connect_button.configure(state=tk.NORMAL)
        # self.disconnect_button.configure(state=tk.DISABLED)

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
            print(data_upper[index+26:index+28])
            # print(f"self.flag = {self.flag}")
            if data_upper[index+26:index+28] == 'C9':    # send 8050,80dc
                self.show_in_text_area(f"接收读卡:\n{data}")
                self.send_data(self.read_data_res,1)
                self.current_time = time.time()
                print(f"Send Read data time={self.current_time} \n")        
                self.flag = 1
            elif data_upper[index+26:index+28] == 'C3' and self.flag == 1:   #send 8054
                self.show_in_text_area(f"接收8050-80DC返回:\n{data}")
                print(data_upper[index:index+30])
                self.send_data(self.write_data_res,2)
                self.current_time = time.time()
                print(f"Send 8050 data time={self.current_time} \n")
                self.flag += 1
            elif data_upper[index+26:index+28] == 'C3' and self.flag == 2:   #send halt
                self.show_in_text_area(f"接收8054返回:\n{data}")
                self.send_data(self.halt_data_res,3)
                self.current_time = time.time()
                print(f"Send 8054 data time={self.current_time} \n")
                self.flag = 0
        else:
            print("Sequence not found")
    def read_data(self):
        while self.is_running and self.serial:
            try:
                if data := self.serial.readline():
                    self.current_time = time.time()
                    print(f"Read Data time={self.current_time}")
                    self.Apdu_Handle(data.hex(), self.sequence)
                    
            except Exception as e:
                self.show_in_text_area(f"Read data failed!!!: {e}")

    def send_data(self, hex_data,type):
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
                if type == 1:
                    self.show_in_text_area(f"发送8050|80DC:\n{hex_data}")
                elif type == 2:
                    self.show_in_text_area(f"发送8054:\n{hex_data}")
                elif type == 3:
                    self.show_in_text_area(f"发送HALT:\n{hex_data}")
            else:
                self.show_in_text_area("错误：串口未打开")
        except ValueError as e:
            self.show_in_text_area(f"发送数据失败：{e}")

    def show_in_text_area(self, message):
        self.text_area.insert(tk.END, message + "\n" + "\n")
        self.text_area.see(tk.END)

customtkinter.set_appearance_mode("light")  # Modes: System (default), light, dark
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
root = customtkinter.CTk()
app = SerialAssistant(root)
root.mainloop()