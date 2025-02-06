import tkinter as tk
import serial
import serial.tools.list_ports
import threading
import ttkbootstrap as ttk
import customtkinter
from CTkTable import CTkTable
import ctypes
import time
import os
import sys
from tkinter import messagebox
from datetime import datetime
sys.path.append("E:/Work/UWB/Code/UwbCOMCode")
from Crypto.Cipher import DES, DES3
from Crypto.Util.Padding import pad, unpad
from Algorithm.Ecb_Des import MyEcbDes

class UwbReaderAssistant:
    def __init__(self, master):
        self.master = master
        self.version = "_v1.0"
        self.master.title("UWBReader"+self.version)
        self.master.minsize(900, 250)
        self.master.geometry("900x450")
        icon_path = os.path.join(os.path.dirname(__file__), 'UWBReader.ico')
        self.master.wm_iconbitmap(icon_path)
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
        self.enter_id = 1
        self.exit_id = 1
        self.flag = 0
        self.sequence = "06FFFFFFFFFF05FFFFFFFFFF"

        self.defaultKey = bytes.fromhex("32D464AC81F1640A687D023BF99E35DF")
        self.posId      = "040900010001"
        self.EnterMoney = "00000000"     
        self.ExitMoney = "00000001"
        self.EnterEP = "03"
        self.ExitEP = "04"
        self.balance = "00002190"
        self.CardNo = ""
        self.MAC = "00000000"
        self.OnlineSeqNo = ""
        self.RandomNo = ""
        self.halt_data_res =  "0000FF100005FFFFFFFFFF06FFFFFFFFFF44CA0000F100"
        
        if self.Use_RSCode:     #XXX  RS码使用示例:
            self.halt_data_res =  bytes([0x00, 0x00, 0xFF, 0x10, 0x00, 0x05, 0xFF, 0xFF, 0xFF, 0xFF,0xFF, 0x06, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x44, 0xCA, 0x00, 0x00, 0xF1, 0x00])
            self.halt_data_res = self.RS_Encode(self.halt_data_res)
            # 加入误差
            error = "010203"
            self.read_data_res = self.read_data_res[:-29] + error + self.read_data_res[-23:]    
            print(f'read_data_res: {self.read_data_res}')

        self.create_widgets()
    
    def update_read_data_res(self, type):
        industry_code_map = {
            "公交": "01",
            "地铁": "02",
            "轮渡": "03",
            "BRT": "04"
        }
        current_time = datetime.now()
        self.DateTime = current_time.strftime("%Y%m%d%H%M%S")     # 出现长度错误后返回这儿将时间更新了，后续手机端读写时间不一致
        if type == 0:
            Enter_IndustryCode_val = industry_code_map.get(self.IndustryCode_val.get(), "BRT")
            Enter_Line_val = self.Line_val.get()
            Enter_Site_val = self.Site_val.get()
            if self.money_entry.get() == "":
                self.EnterMoney = self.money_entry.get()
                messagebox.showerror("please input enter money:")
                return 0
            # print(f"Enter_IndustryCode: {Enter_IndustryCode_val}  Enter_Line: {Enter_Line_val}  Enter_Site: {Enter_Site_val}")
            self.enter_read_data_res = "05FFFFFFFFFF06FFFFFFFFFF2AC20211805003020B01" + self.EnterMoney + self.posId + "0F"+ "3580DC00F030" + self.EnterEP + "0000" + self.posId \
                                        + Enter_IndustryCode_val + Enter_Line_val + Enter_Site_val + "000015" + self.EnterMoney + self.balance + self.DateTime + "584012215840FFFFFFFF000000000000"
            self.dcs = self.calculate_DCS(self.enter_read_data_res)
            self.enter_read_data_res = "0000FF5700" + self.enter_read_data_res + self.dcs + "00"                #XXX 长度57为self.
        elif type == 1:
            Exit_IndustryCode_val = industry_code_map.get(self.IndustryCode_val1.get(), "BRT")
            Exit_Line_val = self.Line_val1.get()
            Exit_Site_val = self.Site_val1.get()
            self.ExitMoney = self. money_exit.get()
            if self.ExitMoney == "":
                messagebox.showerror("please input exit money:")
                return 0
            print(f"Exit_IndustryCode: {Exit_IndustryCode_val}  Exit_Line: {Exit_Line_val}  Exit_Site: {Exit_Site_val}")
            self.exit_read_data_res = "05FFFFFFFFFF06FFFFFFFFFF2AC20211805003020B01" + self.ExitMoney + self.posId + "0F"+ "3580DC00F030" + self.ExitEP + "0000" + self.posId \
                                        + Exit_IndustryCode_val + Exit_Line_val + Exit_Site_val + "000015" + self.ExitMoney + self.balance + self.DateTime + "584012215840FFFFFFFF000000000000"
            self.dcs = self.calculate_DCS(self.exit_read_data_res)
            self.exit_read_data_res = "0000FF5700" + self.exit_read_data_res + self.dcs + "00"
        return 1
    
    def update_write_data_res(self):
        self.enter_write_data_res = "05FFFFFFFFFF06FFFFFFFFFF17C20115805401000F00000001"+self.DateTime      #+self.MAC+"08"+"F500"
        self.exit_write_data_res = "05FFFFFFFFFF06FFFFFFFFFF17C20115805401000F00000001"+self.DateTime
        self.Enter_macdata = self.EnterMoney + "09" + self.posId + self.DateTime + "80" + "0000000000"     # 这里的时间需要和APDU的时间一致
        self.Enter_macdata = bytes.fromhex(self.Enter_macdata)
        self.Exit_macdata = self.ExitMoney + "09" + self.posId + self.DateTime + "80" + "0000000000"
        self.Exit_macdata = bytes.fromhex(self.Exit_macdata)

    def create_widgets(self):
        for col in range(7):
            self.master.grid_columnconfigure(col, weight=1)
        self.master.grid_rowconfigure(2, weight=1)

        self.port_options = self.get_serial_ports()
        self.port_var = tk.StringVar(self.master)
        if self.port_options:  # 检查是否有可用的串口
            self.port_var.set(self.port_options[0])  # 默认选择第一个串口
        else:
            self.port_var.set('')  # 如果没有串口，设置为空字符串
        
        self.port_options1 = self.get_serial_ports()
        self.port_var1 = tk.StringVar(self.master)
        if self.port_options1:  # 检查是否有可用的串口
            self.port_var1.set(self.port_options1[0])  # 默认选择第一个串口
        else:
            self.port_var1.set('')  # 如果没有串口，设置为空字符串
        
        self.baudrate_var = tk.IntVar(self.master, 460800)  # 默认波特率9600
        self.baudrate_var1 = tk.IntVar(self.master, 460800)  # 默认波特率9600

        # self.port_label = customtkinter.CTkLabel(self.master, text="ENTER STATION", corner_radius = 10, fg_color= ("#6699CC"), font=("Roboto", 18), text_color=("#FFF8DC"))
        # self.port_label.grid(column=0, row=0, columnspan = 3, padx=75, pady=10,sticky='nsew')

        # self.port_label1 = customtkinter.CTkLabel(self.master, text="EXIT STATION", corner_radius = 10, fg_color= ("#6699CC"), font=("Roboto", 18), text_color=("#FFF8DC"))
        # self.port_label1.grid(column=4, row=0, columnspan = 3, padx=75, pady=10,sticky='nsew')

        def create_label(master, text, column, row, columnspan, padx, pady):
            label_style = {
                "corner_radius": 15,
                "fg_color": "#E0E0E0",
                "font": ("Roboto", 20, "bold"),
                "text_color": "#6A1B9A",
                "anchor": "center"
            }
            label = customtkinter.CTkLabel(master, text=text, **label_style)
            label.grid(column=column, row=row, columnspan=columnspan, padx=padx, pady=pady, sticky='nsew')
            return label

        # 创建标题
        self.port_label = create_label(self.master, "ENTER STATION", 0, 0, 3, 75, 10)
        self.port_label1 = create_label(self.master, "EXIT STATION", 4, 0, 3, 75, 10)

        ## Tab ##
        TabColor = ("#E0F2F8","#AED6F1")
        TextColor = ("#663300", "#663300")
        self.EnterTab = customtkinter.CTkTabview(self.master, fg_color=TabColor, segmented_button_selected_color=("pink", "purple"))
        self.EnterTab.grid(row=2, column=0, columnspan=3, rowspan=5, padx=10, pady=10,sticky='nsew')
        self.EnterTab.add("COM")
        self.EnterTab.add("Setting")
        self.EnterTab.add("Enter")
        self.EnterTab.set("COM")

        self.ExitTab = customtkinter.CTkTabview(master=self.master, fg_color=TabColor, segmented_button_selected_color=("pink", "purple"))
        self.ExitTab.grid(row=2, column=4, columnspan=3, rowspan = 5, padx=10, pady=10,sticky='nsew')
        self.ExitTab.add("COM")
        self.ExitTab.add("Setting")
        self.ExitTab.add("Exit")
        self.ExitTab.set("COM")

        EnterTabFrame = customtkinter.CTkFrame(self.EnterTab.tab("Enter"))
        EnterTabFrame.pack(padx=20, pady=20, fill="both", expand=True)
        ExitTabFrame = customtkinter.CTkFrame(self.ExitTab.tab("Exit"))
        ExitTabFrame.pack(padx=20, pady=20, fill="both", expand=True)

        ## Textbox ##
        self.text_area = customtkinter.CTkTextbox(EnterTabFrame, width=200, height=400,  fg_color=("#E6E6FF", "#A0C8CF"), text_color="black")
        self.text_area.pack(padx=1, pady=1, fill="both", expand=True)
        self.text_area1 = customtkinter.CTkTextbox(ExitTabFrame, width=200, height=400,  fg_color=("#E6E6FF", "#A0C8CF"), text_color="black")  
        self.text_area1.pack(padx=1, pady=1, fill="both", expand=True)
        
        ## Setting Enter ##
        industry_frame = customtkinter.CTkFrame(self.EnterTab.tab("Setting"),fg_color= TabColor)
        industry_frame.pack(padx=20, pady=10, fill="x")
        industry_code_label = customtkinter.CTkLabel(industry_frame, text="行业代码:", font=("Roboto", 15), text_color=TextColor)
        industry_code_label.pack(side="left", padx=(0, 10))  # 左对齐，右侧留出一些间距
        self.IndustryCode_val = tk.StringVar(self.master, "BRT")
        self.IndustryCode_menu = customtkinter.CTkOptionMenu(industry_frame, variable=self.IndustryCode_val, values=["公交", "地铁", "轮渡", "BRT"], font=("Roboto", 15))
        self.IndustryCode_menu.pack(side="left")

        line_frame = customtkinter.CTkFrame(self.EnterTab.tab("Setting"),fg_color= TabColor)
        line_frame.pack(padx=20, pady=10, fill="x")
        line_label = customtkinter.CTkLabel(line_frame, text="线路代码:", font=("Roboto", 15), text_color=TextColor)
        line_label.pack(side="left", padx=(0, 10))  # 左对齐，右侧留出一些间距
        self.Line_val = tk.StringVar(self.master, "0000")
        self.Line_menu = customtkinter.CTkOptionMenu(line_frame, variable=self.Line_val, values=["0000", "0001", "0002", "0003"], font=("Roboto", 15))
        self.Line_menu.pack(side="left")
        
        site_frame = customtkinter.CTkFrame(self.EnterTab.tab("Setting"),fg_color= TabColor)
        site_frame.pack(padx=20, pady=10, fill="x")
        site_label = customtkinter.CTkLabel(site_frame, text="站点代码:", font=("Roboto", 15), text_color=TextColor)
        site_label.pack(side="left", padx=(0, 10))  # 左对齐，右侧留出一些间距
        self.Site_val = tk.StringVar(self.master, "0000")
        self.Site_menu = customtkinter.CTkOptionMenu(site_frame, variable=self.Site_val, values=["0000", "0001", "0002", "0003"], font=("Roboto", 15))
        self.Site_menu.pack(side="left")

        money_frame = customtkinter.CTkFrame(self.EnterTab.tab("Setting"),fg_color= TabColor)
        money_frame.pack(padx=20, pady=10, fill="x")
        money_label = customtkinter.CTkLabel(money_frame, text="入站金额:", font=("Roboto", 15), text_color=TextColor)
        money_label.pack(side="left", padx=(0, 10))  # 左对齐，右侧留出一些间距
        self.money_entry = customtkinter.CTkEntry(money_frame, font=("Roboto", 15), placeholder_text="请输入金额")
        self.money_entry.insert(0, "00000000")
        self.money_entry.pack(side="left")

        ## Setting Exit ##
        industry_code_frame = customtkinter.CTkFrame(self.ExitTab.tab("Setting"),fg_color= TabColor)
        industry_code_frame.pack(padx=20, pady=10, fill="x")
        industry_code_label = customtkinter.CTkLabel(industry_code_frame, text="行业代码:", font=("Roboto", 15), text_color=TextColor)
        industry_code_label.pack(side="left", padx=(0, 10))  # 左对齐，右侧留出一些间距
        self.IndustryCode_val1 = tk.StringVar(self.master, "BRT")
        self.IndustryCode_menu1 = customtkinter.CTkOptionMenu(industry_code_frame, variable=self.IndustryCode_val1, values=["公交", "地铁", "轮渡", "BRT"], font=("Roboto", 15))
        self.IndustryCode_menu1.pack(side="left")

        line_frame1 = customtkinter.CTkFrame(self.ExitTab.tab("Setting"),fg_color= TabColor)
        line_frame1.pack(padx=20, pady=10, fill="x")
        line_label = customtkinter.CTkLabel(line_frame1, text="线路代码:", font=("Roboto", 15), text_color=TextColor)
        line_label.pack(side="left", padx=(0, 10))  # 左对齐，右侧留出一些间距
        self.Line_val1 = tk.StringVar(self.master, "0000")
        self.Line_menu1 = customtkinter.CTkOptionMenu(line_frame1, variable=self.Line_val1, values=["0000", "0001", "0002", "0003"], font=("Roboto", 15))
        self.Line_menu1.pack(side="left")

        site_frame1 = customtkinter.CTkFrame(self.ExitTab.tab("Setting"),fg_color= TabColor)
        site_frame1.pack(padx=20, pady=10, fill="x")
        site_label = customtkinter.CTkLabel(site_frame1, text="站点代码:", font=("Roboto", 15), text_color=TextColor)
        site_label.pack(side="left", padx=(0, 10))  # 左对齐，右侧留出一些间距
        self.Site_val1 = tk.StringVar(self.master, "0000")
        self.Site_menu1 = customtkinter.CTkOptionMenu(site_frame1, variable=self.Site_val1, values=["0000", "0001", "0002", "0003"], font=("Roboto", 15))
        self.Site_menu1.pack(side="left")

        money_frame1 = customtkinter.CTkFrame(self.ExitTab.tab("Setting"),fg_color= TabColor)
        money_frame1.pack(padx=20, pady=10, fill="x")
        money_label1 = customtkinter.CTkLabel(money_frame1, text="出站金额:", font=("Roboto", 15), text_color=TextColor)
        money_label1.pack(side="left", padx=(0, 10))  # 左对齐，右侧留出一些间距
        self.money_exit = customtkinter.CTkEntry(money_frame1, font=("Roboto", 15), placeholder_text="请输入金额")
        self.money_exit.insert(0, "00000001")
        self.money_exit.pack(side="left")

        ## COM Enter ##
        port_frame = customtkinter.CTkFrame(self.EnterTab.tab("COM"),fg_color= TabColor)
        port_frame.pack(padx=20, pady=10, fill="x")
        port_label = customtkinter.CTkLabel(port_frame, text="COM选择 :", font=("Roboto", 15), text_color=TextColor)
        port_label.pack(side="left", padx=(0, 22))  # 左对齐，右侧留出一些间距

        self.port_menu = customtkinter.CTkOptionMenu(port_frame, variable=self.port_var, values=[*self.port_options], font=("Roboto", 15))
        self.port_menu.pack(side="left")
        baudrate_frame = customtkinter.CTkFrame(self.EnterTab.tab("COM"),fg_color= TabColor)
        baudrate_frame.pack(padx=20, pady=10, fill="x")
        baudrate_label = customtkinter.CTkLabel(baudrate_frame, text="波特率选择 :", font=("Roboto", 15), text_color=TextColor)
        baudrate_label.pack(side="left", padx=(0, 10))  # 左对齐，右侧留出一些间距
        self.baudrate_menu = customtkinter.CTkOptionMenu(baudrate_frame, variable=self.baudrate_var, values=["460800", "115200", "3000000", "9600"], font=("Roboto", 15))
        self.baudrate_menu.pack(side="left")

        # self.clear_button = customtkinter.CTkButton(self.EnterTab.tab("COM"), text="Clear", command=self.clear_text_area, font=("Roboto", 15))
        # self.clear_button.pack(padx=20,pady=10)
        self.segemented_button = customtkinter.CTkSegmentedButton(self.EnterTab.tab("COM"), values=["Connect", "Disconnect"], command=self.segmented_button_callback, font=("Roboto", 15), selected_color=("pink", "purple"), width=200)
        self.segemented_button.pack(padx=20, pady=10, fill="x")
        self.segemented_button.set("Disconnect")

        ## COM Exit ##
        port_frame1 = customtkinter.CTkFrame(self.ExitTab.tab("COM"),fg_color= TabColor)
        port_frame1.pack(padx=20, pady=10, fill="x")
        port_label1 = customtkinter.CTkLabel(port_frame1, text="COM选择 :", font=("Roboto", 15), text_color=TextColor)
        port_label1.pack(side="left", padx=(0, 22))  # 左对齐，右侧留出一些间距
        self.port_menu1 = customtkinter.CTkOptionMenu(port_frame1, variable=self.port_var1, values=[*self.port_options1], font=("Roboto", 15))
        self.port_menu1.pack(side="left")

        baudrate_frame1 = customtkinter.CTkFrame(self.ExitTab.tab("COM"),fg_color= TabColor)
        baudrate_frame1.pack(padx=20, pady=10, fill="x")
        baudrate_label1 = customtkinter.CTkLabel(baudrate_frame1, text="波特率选择 :", font=("Roboto", 15), text_color=TextColor)
        baudrate_label1.pack(side="left", padx=(0, 10))  # 左对齐，右侧留出一些间距
        self.baudrate_menu1 = customtkinter.CTkOptionMenu(baudrate_frame1, variable=self.baudrate_var1, values=["460800", "115200", "3000000", "9600"], font=("Roboto", 15))
        self.baudrate_menu1.pack(side="left")
        # self.clear_button1 = customtkinter.CTkButton(self.ExitTab.tab("COM"), text="Clear", command=self.clear_text_area1, font=("Roboto", 15))
        # self.clear_button1.pack(padx=20,pady=10 )
        self.segemented_button1 = customtkinter.CTkSegmentedButton(self.ExitTab.tab("COM"), values=["Connect", "Disconnect"], command=self.segmented_button_callback1, font=("Roboto", 15), selected_color=("pink", "purple"), width=200)
        self.segemented_button1.pack(padx=20, pady=10, fill="x")
        self.segemented_button1.set("Disconnect")
    
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
        self.text_area.delete(1.0, tk.END)  
    def clear_text_area1(self):
        self.text_area1.delete(1.0, tk.END)  
    
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
            messagebox.showerror("Request Uart List error:", e)
        return ports

    def connect_enter(self):
        try:
            if self.port_var.get():
                self.EnterSerial = serial.Serial(self.port_var.get(), self.baudrate_var.get(), timeout=0.05)   # reader 30ms返回
                self.enter_running = True
                # self.enter_read()
                self.read_thread_enter = threading.Thread(target=self.read_data_enter)
                self.read_thread_enter.start()
        except Exception as e:
            messagebox.showerror("Connect Uart error:", e)
    
    def connect_exit(self):
        try:
            if self.port_var1.get():
                self.ExitSerial = serial.Serial(self.port_var1.get(), self.baudrate_var1.get(), timeout=0.05)   # reader 30ms返回
                self.exit_running = True
                # self.exit_read()
                self.read_thread_exit = threading.Thread(target=self.read_data_exit)
                self.read_thread_exit.start()
        except Exception as e:
            messagebox.showerror("Connect Uart error:", e)

    def disconnect_enter(self):
        try:
            self.enter_running = False
            if self.read_thread_enter:
                self.read_thread_enter.join()
            if self.EnterSerial:
                self.EnterSerial.close()
            
        except Exception as e:
            messagebox.showerror("Disconnect Uart error:", e)

    def disconnect_exit(self):
        self.exit_running = False
        if self.read_thread_exit:
            self.read_thread_exit.join()
        if self.ExitSerial:
            self.ExitSerial.close()
    
    def get_mac(self, write_data_res, type):
        try:
            macdata = self.Enter_macdata if type == 0 else self.Exit_macdata   #修改macdata，支持进出站的扣费不同

            if len(self.CardNo) != 20 or len(self.RandomNo) != 8 or len(self.OnlineSeqNo) != 4:
                print(f"Len ERROR: \nlen(self.CardNo) = {len(self.CardNo)} len(self.RandomNo) = {len(self.RandomNo)} len(self.OnlineSeqNo) = {len(self.OnlineSeqNo)}")
                print(f"CardNo: {self.CardNo}  RandomNo: {self.RandomNo}  OnlineSeqNo: {self.OnlineSeqNo}")
                return False
            print(f"RandomNo: {self.RandomNo}  OnlineSeqNo: {self.OnlineSeqNo}  CardNo: {self.CardNo}  DateTime: {self.DateTime}")
            factor = self.CardNo[-16:]
            xor_result = self.MyEcbDes.str_xor(factor, "FFFFFFFFFFFFFFFF")
            factor = factor + xor_result
            factor = bytes.fromhex(factor)
            loadKey = self.MyEcbDes.des3_encrypt(self.defaultKey, factor)[:16]
            # print("loadKey: ", loadKey.hex())
            sessionKey = self.MyEcbDes.des3_encrypt(loadKey, bytes.fromhex(self.RandomNo + self.OnlineSeqNo + "0001"))[:8]
            # print("sessionKey", sessionKey.hex())
            self.MAC = self.MyEcbDes.process_macdata(sessionKey, macdata)[:4].hex()
            # print(f"MAC: {self.MAC}")
            
            write_data_res =write_data_res + self.MAC + "08"
            self.dcs = self.calculate_DCS(write_data_res)
            write_data_res ="0000FF2500" + write_data_res + self.dcs + "00"
            print(f"write_data_res: {write_data_res}")
            if type == 0:
                self.enter_write_data_res = write_data_res
            else:
                self.exit_write_data_res = write_data_res
        except Exception as e:
            messagebox.showerror("MAC cacl error:", e)
            return False
        return True

    # def enter_read(self):
    #     if self.enter_running:
    #         threading.Thread(target=self.read_data_enter).start()
        
    # def exit_read(self):
    #     if self.exit_running:
    #         threading.Thread(target=self.read_data_exit).start()

    def EnterApduHandle(self, data, sequence):
        data_upper = data.upper()
        
        sequence_upper = sequence.upper()
        index = data_upper.find(sequence_upper)
        command = data_upper[index+26:index+28]
        if index != -1:
            if command == 'C9':    # send 8050,80dc
                self.CardNo = data_upper[index+122:index+142]
                if self.update_read_data_res(0) != 0:
                    self.send_enter_data(self.enter_read_data_res,1)
                    print("send enter read data")  
                    self.flag = 1
            elif command == 'C3' and self.flag == 1:   #send 8054
                self.balance = data_upper[index+34:index+42]
                self.OnlineSeqNo = data_upper[index+42:index+46]
                self.RandomNo = data_upper[index+56:index+64]
                print(f"data: {data}")
                self.update_write_data_res()
                if self.get_mac(self.enter_write_data_res,0) == True:
                    self.send_enter_data(self.enter_write_data_res,2)
                    print("send enter write data")
                self.flag += 1
            elif command == 'C3' and self.flag == 2:   #send halt
                self.send_enter_data(self.halt_data_res,3)
                print("send enter halt data")
                self.flag = 0
        else:
            pass
            # print("Sequence not found")
    
    def ExitApduHandle(self, data, sequence):
        data_upper = data.upper()
        sequence_upper = sequence.upper()
        index = data_upper.find(sequence_upper)
        command = data_upper[index+26:index+28]
        if index != -1:
            if command == 'C9':    # send 8050,80dc
                self.CardNo = data_upper[index+122:index+142]
                if self.update_read_data_res(1) != 0:
                    self.send_exit_data(self.exit_read_data_res,1)    
                    self.flag = 1
            elif command == 'C3' and self.flag == 1:   #send 8054
                self.balance = data_upper[index+34:index+42]
                self.OnlineSeqNo = data_upper[index+42:index+46]
                self.RandomNo = data_upper[index+56:index+64]
                print(f"RandomNo: {data_upper[index+56:index+64]}")
                self.update_write_data_res()
                if self.get_mac(self.exit_write_data_res,1) == True:
                    self.send_exit_data(self.exit_write_data_res,2)
                self.flag += 1
            elif command == 'C3' and self.flag == 2:   #send halt
                self.send_exit_data(self.halt_data_res,3)
                self.flag = 0
        else:
            pass
            # print("Sequence not found")
            
    def read_data_enter(self):
        while self.enter_running and self.EnterSerial:
            try:
                if data := self.EnterSerial.readline():
                    self.EnterApduHandle(data.hex(), self.sequence)
            except serial.SerialException as e:
                messagebox.showerror("Read data error:", e)
    
    def read_data_exit(self):
        while self.exit_running and self.ExitSerial:
            try:
                if data := self.ExitSerial.readline():
                    self.ExitApduHandle(data.hex(), self.sequence)
            except serial.SerialException as e:
                messagebox.showerror("Read data error:", str(e))
    
    def cacl_money(self, money):
        self.money = money

    def send_enter_data(self, hex_data, type):
        try:
            if len(hex_data) % 2 != 0:
                messagebox.showerror("data len is not even:", e)
                return
            byte_data = bytes.fromhex(hex_data)
            if self.EnterSerial and self.EnterSerial.is_open:
                self.EnterSerial.write(byte_data)
                if type == 2:
                    self.enter_write_data_res = "05FFFFFFFFFF06FFFFFFFFFF17C20115805401000F00000001"+self.DateTime
                elif type == 3:
                    self.show_in_text_area(str(self.enter_id) + " | " + datetime.now().strftime("%Y-%m-%d-%H:%M:%S") + " | " + "扣费: $" + str(int(self.money_entry.get(),16)/100) + " | " + "Enter OK")
                    self.enter_id += 1
                    print("------------------------------- OK -------------------------------")
            else:
                messagebox.showerror("Uart not opened:", e)
        except ValueError as e:
            messagebox.showerror("Send data error:", e)     
    
    def send_exit_data(self, hex_data,type):
        try:
            if len(hex_data) % 2 != 0:
                messagebox.showerror("data len is not even:", e)
                return

            byte_data = bytes.fromhex(hex_data)
            if self.ExitSerial and self.ExitSerial.is_open:
                self.ExitSerial.write(byte_data)
                if type == 2:
                    self.exit_write_data_res = "05FFFFFFFFFF06FFFFFFFFFF17C20115805401000F00000001"+self.DateTime
                elif type == 3:
                    self.show_in_text_area1(str(self.exit_id) + " | " + datetime.now().strftime("%Y-%m-%d-%H:%M:%S") + "  |  " + "扣费: ￥" + str(int(self.money_exit.get(),16)/100) + "  |  " + "Exit OK")
                    self.exit_id += 1
                    print("------------------------------- OK -------------------------------")
            else:
                messagebox.showerror("Uart not opened:", e)
        except ValueError as e:
            messagebox.showerror("Send data error:", e)

    def show_in_text_area(self, message):
        print("enter show_in_text_area")
        self.text_area.insert(tk.END, message + "\n" + "\n")
        self.text_area.see(tk.END)
    
    def show_in_text_area1(self, message):
        self.text_area1.insert(tk.END, message + "\n" + "\n")
        self.text_area1.see(tk.END)

    def show_about(self):
        about_message = f"""
        UWBReader {self.version}

        版权所有 © 2025 可为信息技术有限公司
        Author: @QLL
        Email: Tommy.yang@cardshare.cn
        """
        messagebox.showinfo("关于", about_message)

    def change_theme(self, theme ):
        if theme in ("light", "dark", "System"):
            customtkinter.set_appearance_mode(theme)
        else:
            file = os.path.join(os.path.dirname(__file__), "themes", theme + ".json")
            if os.path.exists(file):
                customtkinter.set_default_color_theme("E:/Work/UWB/Code/UwbCOMCode/tools/themes/MoonlitSky.json")

if __name__ == "__main__":
    customtkinter.set_appearance_mode("light")  # Modes: System (default), light, dark
    file = os.path.join(os.path.dirname(__file__), "themes", "MyMoo" + ".json")   # MoonlitSkynew  TestCardNew
    customtkinter.set_default_color_theme(file)
    # customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
    root = customtkinter.CTk()
    app = UwbReaderAssistant(root)

    menubar = tk.Menu(root)  
    root.config(menu=menubar)

    theme_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="主题", menu=theme_menu)
    theme_menu.add_command(label="浅色模式", command=lambda: app.change_theme("light"))
    theme_menu.add_command(label="深色模式", command=lambda: app.change_theme("dark"))
    theme_menu.add_command(label="跟随系统", command=lambda: app.change_theme("System"))

    about_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="关于", menu=about_menu)
    about_menu.add_command(label = "关于", command=app.show_about)

    root.mainloop()