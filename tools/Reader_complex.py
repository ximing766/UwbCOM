import tkinter as tk
import serial
import serial.tools.list_ports
import threading
import ttkbootstrap as ttk
import customtkinter
import ctypes
import time
import sys
from datetime import datetime
sys.path.append("E:/Work/UWB/Code/UwbCOMCode")
from Crypto.Cipher import DES, DES3
from Crypto.Util.Padding import pad, unpad
from Algorithm.Ecb_Des import MyEcbDes

class UwbReaderAssistant:
    def __init__(self, master):
        self.master = master
        self.master.title("Reader")
        self.master.minsize(850, 530)
        self.master.geometry("650x530")
        self.my_lib = ctypes.WinDLL("./tools/libRSCode.dll")
        self.my_lib.initialize_ecc()
        self.my_lib.encode_data.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte)]
        self.my_lib.encode_data.restype = None
        self.Use_RSCode  = False
        self.MyEcbDes = MyEcbDes()

        self.EnterSerial = None
        self.ExitSerial = None
        self.enter_running = False
        self.exit_running = False

        self.defaultKey = bytes.fromhex("32D464AC81F1640A687D023BF99E35DF")
        self.posId      = "040900010001"
        self.EnterMoney = "00000002"     #FIXME 两次交易的金额必须相同
        self.ExitMoney = "00000002"
        self.EnterEP = "03"
        self.ExitEP = "04"
        self.IndustryCode = "04"
        self.Line = "0000"
        self.Site = "0000"
        self.balance = "00002190"

        self.CardNo = ""
        self.MAC = "00000000"
        current_time = datetime.now()
        self.DateTime = current_time.strftime("%Y%m%d%H%M%S")
        self.OnlineSeqNo = ""
        self.RandomNo = ""
        self.Enter_macdata = self.EnterMoney + "09" + self.posId + self.DateTime + "80" + "0000000000"
        self.Enter_macdata = bytes.fromhex(self.Enter_macdata)
        self.Exit_macdata = self.ExitMoney + "09" + self.posId + self.DateTime + "80" + "0000000000"
        self.Exit_macdata = bytes.fromhex(self.Exit_macdata)
                          
        # self.enter_read_data_res = "05FFFFFFFFFF06FFFFFFFFFF2AC20311805003020B01" + self.EnterMoney + self.posId + "0F"+"8580DC12D08027127D010100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001901023B722700000000000000000000000000000000000000000000" + \
        #                             "3580DC00F030" + self.EnterEP + "0000" + "000279001102" + self.IndustryCode + self.Line+self.Site + "000015" + self.EnterMoney + self.balance + self.DateTime + "584012215840FFFFFFFF000000000000"
        
        self.enter_read_data_res = "05FFFFFFFFFF06FFFFFFFFFF2AC20211805003020B01" + self.EnterMoney + self.posId + "0F"+ "3580DC00F030" + self.EnterEP + "0000" + self.posId \
                                    + self.IndustryCode + self.Line+self.Site + "000015" + "00000000" + self.balance + self.DateTime + "584012215840FFFFFFFF000000000000"
        self.dcs = self.calculate_DCS(self.enter_read_data_res)
        # self.enter_read_data_res = "0000FFDD00" + self.enter_read_data_res + self.dcs + "00"
        self.enter_read_data_res = "0000FF5700" + self.enter_read_data_res + self.dcs + "00"   #XXX 长度57为self.enter_read_data_res的长度
        self.enter_write_data_res = "05FFFFFFFFFF06FFFFFFFFFF17C20115805401000F00000001"+self.DateTime  #+self.MAC+"08"+"F500"
       
        self.exit_read_data_res = "05FFFFFFFFFF06FFFFFFFFFF2AC20211805003020B01" + self.ExitMoney + self.posId + "0F"+ "3580DC00F030" + self.ExitEP + "0000" + self.posId \
                                    + self.IndustryCode + self.Line+self.Site + "000015" + "00000000" + self.balance + self.DateTime + "584012215840FFFFFFFF000000000000"
        self.dcs = self.calculate_DCS(self.exit_read_data_res)
        self.exit_read_data_res = "0000FF5700" + self.exit_read_data_res + self.dcs + "00"
        self.exit_write_data_res = "05FFFFFFFFFF06FFFFFFFFFF17C20115805401000F00000001"+self.DateTime


        self.halt_data_res =  "0000FF100005FFFFFFFFFF06FFFFFFFFFF44CA0000F100"
        print("Data:",self.exit_read_data_res)
        
        if self.Use_RSCode:
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
            
            # 添加RS编码
            self.read_data_res = self.RS_Encode(self.read_data_res)
            self.write_data_res = self.RS_Encode(self.write_data_res)
            self.halt_data_res = self.RS_Encode(self.halt_data_res)
            
            # 加入误差
            error = "010203"
            self.read_data_res = self.read_data_res[:-29] + error + self.read_data_res[-23:]    
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

        self.port_options = self.get_serial_ports()
        self.port_var = tk.StringVar(master)
        if self.port_options:  # 检查是否有可用的串口
            self.port_var.set(self.port_options[0])  # 默认选择第一个串口
        else:
            self.port_var.set('')  # 如果没有串口，设置为空字符串
        
        self.port_options1 = self.get_serial_ports()
        self.port_var1 = tk.StringVar(master)
        if self.port_options1:  # 检查是否有可用的串口
            self.port_var1.set(self.port_options1[0])  # 默认选择第一个串口
        else:
            self.port_var1.set('')  # 如果没有串口，设置为空字符串

        self.text_area = customtkinter.CTkTextbox(master, width=200, height=400,  fg_color=("#A0C8CF"))
        self.text_area.grid(column=0, row=0, columnspan=3, padx=10, pady=10,sticky='nsew')

        self.text_area1 = customtkinter.CTkTextbox(master, width=200, height=400,  fg_color=("#A0C8CF"))
        self.text_area1.grid(column=3, row=0, columnspan=3, padx=10, pady=10,sticky='nsew')

        self.port_label = customtkinter.CTkLabel(master, text="Enter COM:", corner_radius = 10, fg_color= ("#A0C8CF"), font=("Roboto", 15))
        self.port_label.grid(column=0, row=1, padx=10, pady=10,sticky='nsew')

        self.port_label1 = customtkinter.CTkLabel(master, text="Exit COM:", corner_radius = 10, fg_color= ("#A0C8CF"), font=("Roboto", 15))
        self.port_label1.grid(column=3, row=1, padx=10, pady=10,sticky='nsew')

        self.port_menu = customtkinter.CTkOptionMenu(master, variable=self.port_var, values=[*self.port_options], font=("Roboto", 15))
        self.port_menu.grid(column=1, row=1, padx=10, pady=10,sticky='nsew')
        
        self.port_menu1 = customtkinter.CTkOptionMenu(master, variable=self.port_var1, values=[*self.port_options1], font=("Roboto", 15))
        self.port_menu1.grid(column=4, row=1, padx=10, pady=10,sticky='nsew')

        self.baudrate_var = tk.IntVar(master, 460800)  # 默认波特率9600
        self.baudrate_menu = customtkinter.CTkOptionMenu(master, variable=self.baudrate_var, values = ["460800", "115200", "3000000", "9600"], font=("Roboto", 15))
        self.baudrate_menu.grid(column=2, row=1, padx=10, pady=10,sticky='nsew')

        self.baudrate_var1 = tk.IntVar(master, 460800)  # 默认波特率9600
        self.baudrate_menu1 = customtkinter.CTkOptionMenu(master, variable=self.baudrate_var1, values = ["460800", "115200", "3000000", "9600"], font=("Roboto", 15))
        self.baudrate_menu1.grid(column=5, row=1, padx=10, pady=10,sticky='nsew')

        self.segemented_button = customtkinter.CTkSegmentedButton(master, values=["Connect", "Disconnect"], command=self.segmented_button_callback, font=("Roboto", 15), width=280)
        self.segemented_button.grid(column=0, columnspan=2, row=2, padx=10, pady=10,sticky='nsew')
        self.segemented_button.set("Disconnect")

        self.segemented_button1 = customtkinter.CTkSegmentedButton(master, values=["Connect", "Disconnect"], command=self.segmented_button_callback1, font=("Roboto", 15), width=280)
        self.segemented_button1.grid(column=3, columnspan=2, row=2, padx=10, pady=10,sticky='nsew')
        self.segemented_button1.set("Disconnect")

        self.clear_button = customtkinter.CTkButton(master, text="Clear", command=self.clear_text_area, font=("Roboto", 15))
        self.clear_button.grid(column=2, row=2, padx=10, pady=10, sticky='nsew')

        self.clear_button1 = customtkinter.CTkButton(master, text="Clear", command=self.clear_text_area, font=("Roboto", 15))
        self.clear_button1.grid(column=5, row=2, padx=10, pady=10, sticky='nsew')
    
    def calculate_DCS(self,hex_string):
        data = bytes.fromhex(hex_string)
        sum_bytes = sum(data)
        low_byte_sum = sum_bytes % 256
        complement = (256 - low_byte_sum) % 256
        complement_hex_str = f"{complement:02x}"
        return complement_hex_str
    
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
            self.connect_enter()
        elif value == "Disconnect":
            self.disconnect_enter()

    def segmented_button_callback1(self, value):
        if value == "Connect":
            self.connect_exit()
        elif value == "Disconnect":
            self.disconnect_exit()
            
    def get_serial_ports(self):
        ports = []
        try:
            ports = serial.tools.list_ports.comports()
            ports = [port.device for port in ports]
        except Exception as e:
            self.show_in_text_area(f"获取串口列表失败: {e}")
        return ports

    def connect_enter(self):
        try:
            if self.port_var.get():
                self.EnterSerial = serial.Serial(self.port_var.get(), self.baudrate_var.get(), timeout=0.05)   # reader 30ms返回
                self.enter_running = True
                self.enter_read()
                self.show_in_text_area(f"串口已打开: {self.port_var.get()} {self.baudrate_var.get()}")
            else:
                self.show_in_text_area("请选择一个串口")
        except Exception as e:
            self.show_in_text_area(f"连接失败: {e}")
    
    def connect_exit(self):
        try:
            if self.port_var1.get():
                self.ExitSerial = serial.Serial(self.port_var1.get(), self.baudrate_var1.get(), timeout=0.05)   # reader 30ms返回
                self.exit_running = True
                self.exit_read()
                self.show_in_text_area1(f"串口已打开: {self.port_var1.get()} {self.baudrate_var1.get()}")
            else:
                self.show_in_text_area1("请选择一个串口")
        except Exception as e:
            self.show_in_text_area(f"连接失败: {e}")

    def disconnect_enter(self):
        if self.EnterSerial:
            self.EnterSerial.close()
        self.enter_running = False
        self.show_in_text_area(f"串口已关闭")

    def disconnect_exit(self):
        if self.ExitSerial:
            self.ExitSerial.close()
        self.exit_running = False
        self.show_in_text_area1(f"串口已关闭")
    
    def get_mac(self, write_data_res, type):
        try:
            if len(self.CardNo) != 20 or len(self.RandomNo) != 8 or len(self.OnlineSeqNo) != 4:
                print("Len error: \nlen(self.CardNo) = %d\n len(self.RandomNo) = %d\n len(self.OnlineSeqNo) = %d", len(self.CardNo), len(self.RandomNo), len(self.OnlineSeqNo))
                return False
            print(f"Cacl MAC:\nRandomNo: {self.RandomNo}  OnlineSeqNo: {self.OnlineSeqNo}  CardNo: {self.CardNo}  DateTime: {self.DateTime}")
            factor = self.CardNo[-16:]
            xor_result = self.MyEcbDes.str_xor(factor, "FFFFFFFFFFFFFFFF")
            factor = factor + xor_result
            factor = bytes.fromhex(factor)
            loadKey = self.MyEcbDes.des3_encrypt(self.defaultKey, factor)[:16]
            print("loadKey: ", loadKey.hex())
            sessionKey = self.MyEcbDes.des3_encrypt(loadKey, bytes.fromhex(self.RandomNo + self.OnlineSeqNo + "0001"))[:8]
            print("sessionKey", sessionKey.hex())
            self.MAC = self.MyEcbDes.process_macdata(sessionKey, self.Enter_macdata)[:4].hex()
            print(f"MAC: {self.MAC}")
            
            write_data_res =write_data_res + self.MAC + "08"
            self.dcs = self.calculate_DCS(write_data_res)
            write_data_res ="0000FF2500" + write_data_res + self.dcs + "00"
            print(f"write_data_res: {write_data_res}")
            if type == 0:
                self.enter_write_data_res = write_data_res
            else:
                self.exit_write_data_res = write_data_res
        except Exception as e:
            print(f"MAC计算失败: {e}")
            return False
        return True

    def enter_read(self):
        if self.enter_running:
            threading.Thread(target=self.read_data_enter).start()
        
    def exit_read(self):
        if self.exit_running:
            threading.Thread(target=self.read_data_exit).start()

    def EnterApduHandle(self, data, sequence):
        data_upper = data.upper()
        sequence_upper = sequence.upper()
        index = data_upper.find(sequence_upper)
        command = data_upper[index+26:index+28]
        if index != -1:
            if command == 'C9':    # send 8050,80dc
                self.CardNo = data_upper[index+122:index+142]
                self.show_in_text_area(f"接收读卡:\n{data}")
                self.send_enter_data(self.enter_read_data_res,1)    
                self.flag = 1
            elif command == 'C3' and self.flag == 1:   #send 8054
                self.show_in_text_area(f"接收8050-80DC返回:\n{data}")
                self.balance = data_upper[index+34:index+42]
                self.OnlineSeqNo = data_upper[index+42:index+46]
                self.RandomNo = data_upper[index+56:index+64]
                if self.get_mac(self.enter_write_data_res,0) == True:
                    self.send_enter_data(self.enter_write_data_res,2)
                self.flag += 1
            elif command == 'C3' and self.flag == 2:   #send halt
                self.show_in_text_area(f"接收8054返回:\n{data}")
                self.send_enter_data(self.halt_data_res,3)
                self.flag = 0
        else:
            print("Sequence not found")
    
    def ExitApduHandle(self, data, sequence):
        data_upper = data.upper()
        sequence_upper = sequence.upper()
        index = data_upper.find(sequence_upper)
        command = data_upper[index+26:index+28]
        if index != -1:
            if command == 'C9':    # send 8050,80dc
                self.CardNo = data_upper[index+122:index+142]
                self.show_in_text_area1(f"接收读卡:\n{data}")
                self.send_exit_data(self.exit_read_data_res,1)    
                self.flag = 1
            elif command == 'C3' and self.flag == 1:   #send 8054
                self.show_in_text_area1(f"接收8050-80DC返回:\n{data}")
                self.balance = data_upper[index+34:index+42]
                self.OnlineSeqNo = data_upper[index+42:index+46]
                self.RandomNo = data_upper[index+56:index+64]
                if self.get_mac(self.exit_write_data_res,1) == True:
                    self.send_exit_data(self.exit_write_data_res,2)
                self.flag += 1
            elif command == 'C3' and self.flag == 2:   #send halt
                self.show_in_text_area1(f"接收8054返回:\n{data}")
                self.send_exit_data(self.halt_data_res,3)
                self.flag = 0
        else:
            print("Sequence not found")
            
    def read_data_enter(self):
        while self.enter_running and self.EnterSerial:
            try:
                if data := self.EnterSerial.readline():
                    self.EnterApduHandle(data.hex(), self.sequence)
            except Exception as e:
                self.show_in_text_area(f"Read data failed!!!: {e}")
    
    def read_data_exit(self):
        while self.exit_running and self.ExitSerial:
            try:
                if data := self.ExitSerial.readline():
                    self.ExitApduHandle(data.hex(), self.sequence)
            except Exception as e:
                self.show_in_text_area1(f"Read data failed!!!: {e}")

    def send_enter_data(self, hex_data, type):
        try:
            if len(hex_data) % 2 != 0:
                self.show_in_text_area("Error:16进制数据长度应为偶数")
                return

            byte_data = bytes.fromhex(hex_data)
            if self.EnterSerial and self.EnterSerial.is_open:
                self.EnterSerial.write(byte_data)
                if type == 1:
                    self.show_in_text_area(f"发送8050|80DC:\n{hex_data}")
                elif type == 2:
                    self.show_in_text_area(f"发送8054:\n{hex_data}")
                    self.enter_write_data_res = "05FFFFFFFFFF06FFFFFFFFFF17C20115805401000F00000001"+self.DateTime
                elif type == 3:
                    self.show_in_text_area(f"发送HALT:\n{hex_data}")
            else:
                self.show_in_text_area("错误：串口未打开")
        except ValueError as e:
            self.show_in_text_area(f"发送数据失败：{e}")
    
    def send_exit_data(self, hex_data,type):
        try:
            if len(hex_data) % 2 != 0:
                self.show_in_text_area("Error:16进制数据长度应为偶数")
                return

            byte_data = bytes.fromhex(hex_data)
            if self.ExitSerial and self.ExitSerial.is_open:
                self.ExitSerial.write(byte_data)
                if type == 1:
                    self.show_in_text_area1(f"发送8050|80DC:\n{hex_data}")
                elif type == 2:
                    self.show_in_text_area1(f"发送8054:\n{hex_data}")
                    self.exit_write_data_res = "05FFFFFFFFFF06FFFFFFFFFF17C20115805401000F00000001"+self.DateTime
                elif type == 3:
                    self.show_in_text_area1(f"发送HALT:\n{hex_data}")
            else:
                self.show_in_text_area1("错误：串口未打开")
        except ValueError as e:
            self.show_in_text_area1(f"发送数据失败：{e}")

    def show_in_text_area(self, message):
        self.text_area.insert(tk.END, message + "\n" + "\n")
        self.text_area.see(tk.END)
    
    def show_in_text_area1(self, message):
        self.text_area1.insert(tk.END, message + "\n" + "\n")
        self.text_area1.see(tk.END)

customtkinter.set_appearance_mode("light")  # Modes: System (default), light, dark
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
root = customtkinter.CTk()
app = UwbReaderAssistant(root)
root.mainloop()