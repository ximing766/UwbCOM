
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.icons import Emoji 
import serial
import threading
from tkinter import scrolledtext
from tkinter import messagebox
import serial.tools.list_ports
from PIL import Image, ImageTk
import math
import random
import queue
import time
import warnings
import json
import os
import configparser
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import ElasticNet
import numpy as np
from Algorithm.lift_uwb_dynamic_detect_plan import UWBLiftAnimationPlan1,UWBLiftAnimationPlan2
from Algorithm.KF_classify import KalmanFilter
from Algorithm.location.ultdoa_dynamic_location import CoordinatePlotter
from Algorithm.location.Chan_lse import ChanALG_LSE
from Algorithm.location.Chan_equation import ChanEALG

class SerialAssistant:
    def __init__(self, master):
        self.master = master

        self.config = configparser.ConfigParser()
        self.config.read('./config/init.ini')
        print(self.config.get('DEFAULT', 'Version',fallback = 'unknow'))
        self.version = self.config['DEFAULT']['Version']
        self.Window = self.config['DEFAULT']['Window']

        self.master.title(self.version)
        self.master.minsize(800, 800)
        self.master.geometry(self.Window)
        icon_path = os.path.join(os.path.dirname(__file__), 'UWB.ico')
        self.master.wm_iconbitmap(icon_path)

        # 设置串口参数
        self.port         = "COM1"
        self.baudrate     = 115200
        self.serial_open  = False
        self.serial_ports = []
        self.bytesize     = serial.EIGHTBITS            
        self.parity       = serial.PARITY_NONE          
        self.stopbits     = serial.STOPBITS_ONE         
        
        self.distance_list = [{
            "GateDistance"  : 0,
            "MasterDistance": 0,
            "SlaverDistance": 0,
            "CoorX_Arr"     : np.array([]),
            "CoorY_Arr"     : np.array([]),
            "Start_X"       : None,
            "Start_Y"       : None,
            "ZScoreFlag"    : 0,                       # Z-Score异常值处理标志, 记录未经过Z-Score处理过的新坐标数量
            "nLos"          : 0,                      
            "lift_deep"     : 0,
            "KF"            : KalmanFilter(0.5, 2, 2), 
            "KF_predict"    : [0, 0],
        } for _ in range(20)]  
        #self.distance_list = [self.initial_dict.copy() for _ in range(20)]  #初始化20个用户的数据
        self.user_oval = {}

        ## ** User Define ** ##
        #Emoji._ITEMS[i].name                               "🤨"
        print(Emoji._ITEMS[-20])
        self.face = Emoji.get("winking face")
        self.init_draw            = 0                       #限制除用户外，其它图形多次作图
        self.flag_str             = ""                      #判断需要获取的卡信息种类
        self.Master2SlverDistance = 0                       #画图用的闸间距
        self.radius               = 0                       #UWB初始扫描半径
        self.lift_deep            = 0                       #电梯深度
        self.lift_height          = 0                       #电梯高度
        self.red_height           = 0
        self.blue_height          = 250
        
        self.queue_com1           = queue.Queue()           #存储不同COM的ULTDOA数据, 默认com1为主Anchor
        self.queue_com2           = queue.Queue()
        self.queue_com3           = queue.Queue()
        self.DSi_M                = []                      #Slver_i到Master的距离
        self.Q                    = []                      #Q值
        self.Anchor_position      = []                      #所有点坐标
        self.master_position      = []                      #主Anchor坐标
        self.slave1_position      = []                      #从Anchor坐标
        self.slave2_position      = []

        self.x                    = 0
        self.y                    = 0
        self.cor                  = []
        self.Use_KF               = False                    #使用卡尔曼滤波器还是弹性网络

        self.CallCount            = 0
        self.current_time         = 0
        self.last_call_time       = 0
        self.max_moves            = 10
        self.move_times           = 0
        self.x_move               = 0
        self.y_move               = 0

        #self.master.configure(background='pink')
        print(Emoji._ITEMS[-106:])

        # 创建界面
        self.create_widgets()

        #实时更新串口选择框
        self.update_combobox_periodically()
    
    def get_serial_ports(self):
        ports        = serial.tools.list_ports.comports()
        serial_ports = [port.device for port in ports]
        return serial_ports
    
    def update_combobox(self):
        serial_ports = self.get_serial_ports()
        if serial_ports != self.serial_ports:
            self.serial_ports = serial_ports
            self.combo['values'] = self.serial_ports
            if self.serial_ports:
                self.combo.current(0)
    
    def update_combobox_periodically(self):
        self.update_combobox()
        self.master.after(1000, self.update_combobox_periodically)  # 每隔1秒调用一次

    def create_widgets(self):
        '''
        description: 串口设置区域
        
        '''        
        frame_settings = ttk.LabelFrame(self.master, text="串口设置",bootstyle="info")
        frame_settings.grid(row=0, column=0, padx=5, pady=5,sticky='nsew')
        frame_settings.grid_columnconfigure(0, weight=1)
        frame_settings.grid_columnconfigure(1, weight=1)
        frame_settings.grid_columnconfigure(2, weight=1)
        frame_settings.grid_columnconfigure(3, weight=1)
        frame_settings.grid_columnconfigure(4, weight=1)
        frame_settings.grid_columnconfigure(5, weight=1)

        ttk.Label(frame_settings, text="COM" + Emoji._ITEMS[-106:][7].char,bootstyle="danger").grid(row=0, column=0, padx=1, pady=5,sticky='w')
        self.port_var = tk.StringVar()

        self.combo = ttk.Combobox(frame_settings, values=self.get_serial_ports(),bootstyle="primary")
        self.update_combobox()
        self.combo.grid(row=0, column=1, padx=1, pady=5,sticky='we')

        ttk.Label(frame_settings, text="Baud" + Emoji._ITEMS[-106:][-4].char,bootstyle="danger").grid(row=1, column=0, padx=1, pady=5,sticky='w')
        self.baudrate_var = tk.IntVar()
        
        self.baudCombo = ttk.Combobox(frame_settings,values=['3000000','115200','9600'],bootstyle="primary")
        self.baudCombo.current(0)
        self.baudCombo.grid(row=1, column=1, padx=1, pady=5,sticky='we')

        button_width = 8
        entry_width  = 20

        self.serial_bt = ttk.Button(frame_settings, text="打开串口", command=self.open_serial, width=button_width,bootstyle="primary")
        self.serial_bt.grid(row=0, column=2, padx=5, pady=5,sticky='ns')

        self.modeCombo = ttk.Combobox(frame_settings,values=['GATE','LIFT','UL-TDOA','DL-TDOA'],width=button_width,bootstyle="primary")
        self.modeCombo.current(0)
        self.modeCombo.grid(row=1, column=2, padx=5, pady=5,sticky='ns')
        self.modeCombo.bind("<<ComboboxSelected>>", self.on_mode_change)

        card_Button     = ttk.Button(frame_settings, text="卡  号", command=lambda:self.send_data(11111), width=button_width,bootstyle="primary").grid(row=0, column=4, padx=5, pady=5,sticky='ns')   #这块数据下行
        self.text_area1 = ttk.Entry(frame_settings,width=entry_width,bootstyle="info")
        self.text_area1.grid(row=0, column=3, padx=5, pady=5, sticky='nsew')
        
        other_Button    = ttk.Button(frame_settings, text="有效期", command=lambda:self.send_data(22222), width=button_width,bootstyle="primary").grid(row=1, column=4, padx=5, pady=5,sticky='ns')
        self.text_area2 = ttk.Entry(frame_settings,width=entry_width,bootstyle="info")
        self.text_area2.grid(row=1, column=3, padx=5, pady=5, sticky='nsew') 
        
        other_Button1   = ttk.Button(frame_settings, text="余  额", command=lambda:self.send_data(33333), width=button_width,bootstyle="primary").grid(row=0, column=6, padx=5, pady=5,sticky='ns')
        self.text_area3 = ttk.Entry(frame_settings,width=entry_width,bootstyle="info")
        self.text_area3.grid(row=0, column=5, padx=5, pady=5, sticky='nsew') 
        
        other_Button2   = ttk.Button(frame_settings, text="交易记录", command=lambda:self.send_data(44444), width=button_width,bootstyle="primary").grid(row=1, column=6, padx=5, pady=5,sticky='ns')
        self.text_area4 = ttk.Entry(frame_settings,width=entry_width,bootstyle="info")
        self.text_area4.grid(row=1, column=5, padx=5, pady=5, sticky='nsew')
        
        '''
        description: 通信区域
        '''        
        # 通信区总框架
        frame_comm = ttk.LabelFrame(self.master, text="通信区",width = 100 ,height=10,bootstyle="info")
        frame_comm.grid(row=1, column=0, padx=5, pady=5,sticky='nsew')
        frame_comm.grid_columnconfigure(0, weight=1)
        frame_comm.grid_columnconfigure(1, weight=1)
        frame_comm.grid_rowconfigure(0, weight=1)
        #frame_comm.grid_propagate(False)  # 防止父容器根据子控件的大小自动调整自身大小
        
        # 总框架左侧单独一个文本框
        self.text_box = ttk.ScrolledText(frame_comm, width=60, height=10)
        self.text_box.grid(row=0, column=0, padx=1, pady=1,sticky='nsew')
        
         #右侧总宽度
        frame_comm_sub_width = 40
        # 总框架右侧子总框
        frame_comm_sub = ttk.Frame(frame_comm, width=frame_comm_sub_width,height=10)        
        frame_comm_sub.grid(row=0, column=1, padx=1, pady=1,sticky='nsew')
        frame_comm_sub.grid_rowconfigure(0,weight=1)
        frame_comm_sub.grid_rowconfigure(1,weight=1)
        frame_comm_sub.grid_columnconfigure(0, weight=1)

        # 子总框上侧功能框
        frame_sub_func_height = 5
        frame_sub_func        = ttk.Frame(frame_comm_sub, width=frame_comm_sub_width,height=frame_sub_func_height,bootstyle="info")
        frame_sub_func.grid(row=0, column=0, padx=1, pady=1,sticky='nsew')
        frame_sub_func.grid_rowconfigure(0,weight=1)
        frame_sub_func.grid_columnconfigure(0, weight=1)   

        # 创建第二个文本框并放置在同一行
        self.text_box2 = scrolledtext.ScrolledText(frame_sub_func, width=45,height=frame_sub_func_height)
        self.text_box2.grid(row=0, column=0, padx=1, pady=1,sticky='nsew')
        
        frame_bt_width = 5
        # 基础功能框架
        frame_bt = ttk.Frame(frame_sub_func, width=frame_bt_width,height=frame_sub_func_height,bootstyle="info")
        frame_bt.grid(row=0, column=1, padx=1, pady=1,sticky='nsew')
        frame_bt.grid_rowconfigure(0,weight=1)
        frame_bt.grid_rowconfigure(1,weight=1)
        frame_bt.grid_rowconfigure(2,weight=1)
        frame_bt.grid_columnconfigure(0, weight=1)

        # 创建并放置清除第一个文本框内容的按钮
        clear_button = ttk.Button(frame_bt, text="清除", command=lambda:self.clearAndSave_text(1),width=frame_bt_width,bootstyle="info")
        clear_button.grid(row=0, column=0, padx=1, pady=1,sticky='nsew')
        
        # 创建并放置清除第一个文本框内容的按钮
        clear_button3 = ttk.Button(frame_bt, text="保存1", command=lambda:self.clearAndSave_text(3),width=frame_bt_width,bootstyle="info")
        clear_button3.grid(row=1, column=0, padx=1, pady=1,sticky='nsew')

        # 创建并放置清除第二个文本框内容的按钮
        clear_button4 = ttk.Button(frame_bt, text="保存2", command=lambda:self.clearAndSave_text(4),width=frame_bt_width,bootstyle="info")
        clear_button4.grid(row=2, column=0, padx=1, pady=1,sticky='nsew')

        # 子总框下侧功能框(更具进度条的值，更新演示图中电梯的高度和深度,半径)
        frame_sub_lift = ttk.LabelFrame(frame_comm_sub, width=frame_comm_sub_width, height=15,text="Elevator scheme demonstration",bootstyle="info")
        frame_sub_lift.grid(row=1, column=0, padx=1, pady=1,sticky='nsew')
        frame_sub_lift.grid_rowconfigure(0,weight=1)
        frame_sub_lift.grid_rowconfigure(1,weight=1)
        frame_sub_lift.grid_rowconfigure(2,weight=1)
        frame_sub_lift.grid_columnconfigure(1, weight=1)

        # 添加第一个进度条
        progressbar1 = ttk.Scale(frame_sub_lift, orient="horizontal", length=100, from_=0, to=10,bootstyle="info")
        progressbar1.grid(row=0, column=1, padx=1, pady=1, sticky='nsew')
        progressbar1.set(2.0)

        # 添加一个标签来显示第一个进度条的值
        progressbar1_value = tk.StringVar(value=f"LIFT_D : {progressbar1.get():.1f}")
        progressbar1_label = ttk.Label(frame_sub_lift, textvariable=progressbar1_value)
        progressbar1_label.grid(row=0, column=0, padx=1, pady=1, sticky='nsew')

        # 赋值给self.lift_deep
        def update_progressbar1_value(event):
            value = f"LIFT_D : {progressbar1.get():.1f}"
            progressbar1_value.set(value)
            self.lift_deep = float(value.split(":")[1].strip())

        progressbar1.bind("<Motion>", update_progressbar1_value)
        progressbar1.bind("<ButtonRelease-1>", update_progressbar1_value)

        # 添加第二个进度条
        progressbar2 = ttk.Scale(frame_sub_lift, orient="horizontal", length=100, from_=0, to=10,bootstyle="warning")
        progressbar2.grid(row=1, column=1, padx=1, pady=1, sticky='nsew')
        progressbar2.set(3.0)

        # 赋值给self.lift_height
        progressbar2_value = tk.StringVar(value=f"LIFT_H : {progressbar2.get():.1f}")
        progressbar2_label = ttk.Label(frame_sub_lift, textvariable=progressbar2_value)
        progressbar2_label.grid(row=1, column=0, padx=1, pady=1, sticky='nsew')

        # 更新第二个进度条标签的值
        def update_progressbar2_value(event):
            value = f"LIFT_H : {progressbar2.get():.1f}"
            progressbar2_value.set(value)
            self.lift_height = float(value.split(":")[1].strip())

        progressbar2.bind("<Motion>", update_progressbar2_value)
        progressbar2.bind("<ButtonRelease-1>", update_progressbar2_value)

        # 添加第三个进度条
        progressbar3 = ttk.Scale(frame_sub_lift, orient="horizontal", length=100, from_=0, to=10)
        progressbar3.grid(row=2, column=1, padx=1, pady=1, sticky='nsew')
        progressbar3.set(2.0)

        # 添加一个标签来显示第三个进度条的值
        self.progressbar3_value = tk.StringVar(value=f"UWB_R : {progressbar3.get():.1f}")
        progressbar3_label      = ttk.Label(frame_sub_lift, textvariable=self.progressbar3_value)
        progressbar3_label.grid(row=2, column=0, padx=1, pady=1, sticky='nsew')

        # 更新第三个进度条标签的值
        def update_progressbar3_value(event):
            value = f"UWB_R : {progressbar3.get():.1f}"
            self.progressbar3_value.set(value)
            # 赋值给self.radius
            self.radius = float(value.split(":")[1].strip())

        progressbar3.bind("<Motion>", update_progressbar3_value)
        progressbar3.bind("<ButtonRelease-1>", update_progressbar3_value)

        animation_button1 = ttk.Button(frame_sub_lift, text="演示 1", command=self.run_UWB_Lift_Animation_plan_1, width=5,bootstyle="info")
        animation_button1.grid(row=0, column=2, padx=1, pady=0,sticky='nsew')
        
        animation_button2 = ttk.Button(frame_sub_lift, text="演示 2", command=self.run_UWB_Lift_Animation_plan_2, width=5,bootstyle="info")
        animation_button2.grid(row=1, column=2, padx=1, pady=1,sticky='nsew')

        animation_button2 = ttk.Button(frame_sub_lift, text="占 位", command=self.run_UWB_Lift_Animation_plan_2, width=5,bootstyle="info")
        animation_button2.grid(row=2, column=2, padx=1, pady=1,sticky='nsew')

        '''
        description: 画布区域
        '''        
        frame_draw = ttk.LabelFrame(self.master,text = "画布区",bootstyle="info")
        frame_draw.grid(row=3, column=0, padx=5, pady=5,sticky='nsew')
        frame_draw.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(frame_draw,bg="white",height=400)
        self.canvas.grid(row=0, column=0, padx=5, pady=5,sticky='nsew')

        #绘制画布边界
        #self.canvas.create_rectangle(0+2,0+2, 800-1, 400-1, width=1, outline="black")
        self.master.grid_columnconfigure(0, weight=1)

        '''
        others
        '''

    def update_serial_button(self):
        if self.serial_open:
            self.serial_bt.config(text="关闭串口", command=self.close_serial,bootstyle="danger-outline")
        else:
            self.serial_bt.config(text="打开串口", command=self.open_serial,bootstyle="primary")

    def open_serial(self):
        try:
            self.serial      = serial.Serial(self.combo.get(), self.baudCombo.get(), timeout=1)
            self.read_thread = threading.Thread(target=self.read_data)
            self.read_thread.start()
            self.serial_open = True
            self.update_serial_button()

        except Exception as e:
            self.text_box.insert(tk.END, f"打开串口失败: {e}\n")

    def close_serial(self):
        if self.serial: 
            self.serial.close()
            self.text_box.insert(tk.END, "串口已关闭\n")

            self.canvas.delete("all")       #清空画布
            self.Master2SlverDistance = 0   #初始化闸间距, 防止下次打开串口时，画图出错
            self.serial_open          = False
            self.update_serial_button()
                                                 
    def clearAndSave_text(self,flag):
        if flag == 1:
            self.text_box.delete(1.0, tk.END)
            self.text_box2.delete(1.0,tk.END)
            self.text_area1.delete(0,tk.END)
            self.text_area2.delete(0,tk.END)
            self.text_area3.delete(0,tk.END)
            self.text_area4.delete(0,tk.END)
        elif flag == 3:
            content = self.text_box.get("1.0",tk.END)
            print(content)
            filename = "Distance_content.txt";
            with open(filename,"w" ,encoding="utf-8") as file:
                file.write(content)
            messagebox.showinfo("tips","save file to root dir success!");
            
        elif flag == 4:
            content  = self.text_box2.get(1.0,tk.END)
            filename = "Corr_content.csv"
            with open(filename,"w") as file:
                file.write(content)
            messagebox.showinfo("tips","save file to root dir success!");
    
    def send_data(self,flag):
        self.flag_str = str(flag)
        print("flag is :",self.flag_str)
        self.serial.write(self.flag_str.encode())
        
    def show_cardData(self,data):
        data = data.strip()
        if self.flag_str == "11111":
            cardNumber = data[210:320][:20]
            #self.text_area1.delete(tk.END)
            self.text_area1.delete(0, tk.END)
            self.text_area1.insert(tk.END, cardNumber)     #卡号
            self.flag_str = ""
            
        elif self.flag_str == "22222":
            validPeriod = data[210:320][20:36]
            self.text_area2.delete('1.0', tk.END)
            self.text_area2.insert(tk.END, validPeriod)     #有效期
            self.flag_str = ""
            
        elif self.flag_str == "33333":
            balance = int(data[210:320][48:52],16)
            self.text_area3.delete('1.0', tk.END)
            self.text_area3.insert(tk.END, str(balance / 100))         #余额
            self.flag_str = ""
            
        elif self.flag_str == "44444":
            transactionRecord = data[210:320][92:106]
            self.text_area4.delete('1.0', tk.END)
            self.text_area4.insert(tk.END, transactionRecord)       #交易记录
            self.flag_str = ""
        
        else:    #没有点击事件仍然收到了MOT则为红区，显示所有信息
            json_data = json.loads(data)
            cardNumber = json_data['CardNumber']
            self.text_area1.delete(0, tk.END)
            self.text_area1.insert(tk.END, cardNumber)     #卡号
            balance = json_data['Balance']
            self.text_area3.delete(0, tk.END)
            self.text_area3.insert(tk.END, str(balance / 100) + '￥')         #余额

        
    def change_filter(self,flag):
        self.Use_KF = flag
        if flag == True:
            messagebox.showinfo("tips","filter has been changed to KalmanFilter" );
        else:
            messagebox.showinfo("tips","filter has been changed to ElasticNet" );
    
    #ULTDOA方案数据处理函数
    def UL_read_data(self,port,baudrate,queue):
        ser = serial.Serial(port, baudrate, timeout=1)
        while True:
            try:
                if ser.in_waiting > 0:
                    data = ser.readline().decode('utf-8').strip()
                    # 将数据添加到队列中，以便在主线程中更新UI
                    queue.put(data)
            except serial.SerialException as e:
                print(f"Error reading from {port}: {e}")
                break
        pass
    
    #TWR方案数据处理函数
    def read_data(self):
        self.PosInfo = "@POSITION"
        self.CardInfo = "@CARDINFO";
        while self.serial and self.serial.is_open:

            self.current_time = time.time()
            if self.last_call_time is None:
                self.last_call_time = self.current_time
            elif self.current_time - self.last_call_time >= 1:
                print(f"@ Location has been updated {self.CallCount} times in the last second.")
                self.CallCount = 0 
                self.last_call_time = self.current_time

            try:
                if (data := self.serial.readline()):
                    data = data.decode('utf-8',errors='replace')
                    if self.CardInfo in data:
                        # print(data)
                        self.show_cardData(data)                                            
                    if self.PosInfo in data:               
                        # print(data)
                        try:
                            json_data = json.loads(data)
                        except json.JSONDecodeError as e:
                            print("解析错误：", e)
                        idx = json_data['idx']
                        if 0 <= idx < len(self.distance_list):
                            self.distance_list[idx]['MasterDistance'] = json_data['Master']
                            self.distance_list[idx]['SlaverDistance'] = json_data['Slave']
                            self.distance_list[idx]['GateDistance']   = json_data['Gate']
                            self.distance_list[idx]['nLos']           = json_data['nLos']
                            self.distance_list[idx]['lift_deep']      = json_data['LiftDeep']
                            if json_data['RedAreaH'] != self.red_height or json_data['BlueAreaH'] != self.blue_height:
                                self.red_height                           = json_data['RedAreaH']
                                self.blue_height                          = json_data['BlueAreaH']
                                print(f"RedAreaH: {self.red_height}  BlueAreaH: {self.blue_height}")
                                self.draw_basic()
                        else:
                            print(f"Invalid index: {idx}")
                            continue
                        self.text_box.insert(tk.END, "用户 " + str(idx) + "  |  " + "nLos: " + str(self.distance_list[idx]['nLos'])  +  "  |  " +"主,从,门:  " \
                                             + str(self.distance_list[idx]['MasterDistance']) + " ," + str(self.distance_list[idx]['SlaverDistance']) +" ,"  \
                                                + str(self.distance_list[idx]['GateDistance']) + " <cm>" + "\n")
                        self.text_box.see(tk.END)
                        
                        if self.Master2SlverDistance == 0:
                            self.Master2SlverDistance = self.distance_list[idx]['GateDistance']
                            self.on_mode_change()
                    
                        if self.distance_list[idx]['MasterDistance'] != 0 and self.distance_list[idx]['SlaverDistance'] != 0 and self.distance_list[idx]['GateDistance'] !=0:
                            self.x = 400 + int(((self.distance_list[idx]['SlaverDistance']**2 - self.distance_list[idx]['MasterDistance']**2) / (2*self.distance_list[idx]['GateDistance'])))
                            self.y = int(math.sqrt(abs(self.distance_list[idx]['MasterDistance']**2 - (self.x - (400 + self.distance_list[idx]['GateDistance']/2))**2)))
                            
                            if self.modeCombo.get() == "LIFT":
                                self.y = math.sqrt(abs(self.y**2 - 35*35))  

                            self.y = self.y + 60 
                            self.text_box2.insert(tk.END,f"<user,x,y> {idx} , {self.x-400:.0f} , {self.y-60:.0f}\n")
                            self.text_box2.see(tk.END)
                            
                            if self.Use_KF == True:
                                #卡尔曼滤波方案
                                self.cor = [self.x,self.y]
                                user_kf  = self.distance_list[idx]['KF']
                                z        = np.matrix(self.cor).T
                                user_kf.predict()
                                prediction = user_kf.update(z)
                                prediction = prediction.T.tolist()[0]
                                print(f"KF_Filter : user {idx} prediction = {int(prediction[0]-400),int(prediction[1]-60)}")
                                self.distance_list[idx]["KF_predict"] = prediction
                                self.draw_user_KF(self.distance_list[idx]["KF_predict"],idx)  
                            else:
                                #弹性网络方案
                                self.distance_list[idx]['ZScoreFlag'] += 1
                                self.distance_list[idx]['CoorX_Arr']   = np.append(self.distance_list[idx]['CoorX_Arr'],self.x)
                                self.distance_list[idx]['CoorY_Arr']   = np.append(self.distance_list[idx]['CoorY_Arr'],self.y)
                                
                                if len(self.distance_list[idx]['CoorX_Arr']) == 20:                                                                
                                    #异常值去除:Z-Score  ：每20轮调用一次，一次处理20组coornidate。保证所有数据都能被处理的同时，最大程度消减新coornidate移动带来的偏差。
                                    if self.distance_list[idx]['ZScoreFlag'] == len(self.distance_list[idx]['CoorX_Arr']):
                                        self.distance_list[idx]['CoorX_Arr'] ,self.distance_list[idx]['CoorY_Arr'] = self.Z_Score(self.distance_list[idx]['CoorX_Arr'],self.distance_list[idx]['CoorY_Arr'])
                                        self.distance_list[idx]['ZScoreFlag'] = 0
                                    
                                    if len(self.distance_list[idx]['CoorX_Arr']) < 20:
                                        print('Z-Socre reduce some data,return.',len(self.distance_list[idx]['CoorX_Arr']))
                                    else:
                                        self.CallCount += 1
                                        #滤波:Moving-Average   19
                                        self.distance_list[idx]['CoorX_Arr'] = self.moving_average(self.distance_list[idx]['CoorX_Arr'],2).astype(int)
                                        self.distance_list[idx]['CoorY_Arr'] = self.moving_average(self.distance_list[idx]['CoorY_Arr'],2).astype(int)

                                        #创建回归曲线模型，预测用户坐标位置
                                        self.predict_x,self.predict_y = self.predict_coor(self.distance_list[idx]['CoorX_Arr'],self.distance_list[idx]['CoorY_Arr'])
                                        
                                        #添加预测数据到数组末尾  20
                                        self.distance_list[idx]['CoorX_Arr'] = np.append(self.distance_list[idx]['CoorX_Arr'],self.predict_x)    
                                        self.distance_list[idx]['CoorY_Arr'] = np.append(self.distance_list[idx]['CoorY_Arr'],self.predict_y)
                                        # print("draw user!!!")
                                        self.draw_user_EN(self.distance_list,idx)  

                                        #删除一部分，添加新的运动趋势
                                        self.distance_list[idx]['CoorX_Arr'] = np.delete(self.distance_list[idx]['CoorX_Arr'],[0])           
                                        self.distance_list[idx]['CoorY_Arr'] = np.delete(self.distance_list[idx]['CoorY_Arr'],[0])
                                else:
                                    pass
                        else:
                            print("E : Y is calculated negative!!!")
            except serial.SerialException:
                self.text_box.insert(tk.END, "串口连接已断开\n")
                break

            #time.sleep(0.05)
    def check_nLos(self):
        for idx, item in enumerate(self.distance_list):
            if item.get('nLos') == 1:
                # print(f"Found nLos == 1 at index {idx}")
                return True
        return False
    
    '''
    description: 
    param {*} uniform_speed  1:匀速运动  2:减速运动 待开发 3:加速运动 待开发
    '''    
    def move_oval(self,canvas, oval, start_x, start_y, end_x, end_y, uniform_speed=1):
        if uniform_speed == 1:
            self.x_move = (end_x - start_x) / 10
            self.y_move = (end_y - start_y) / 10
        
        canvas.move(oval, self.x_move, self.y_move)
        self.move_times += 1
        print(f"X_move = {self.x_move} Y_move = {self.y_move} moveing...{self.move_times}")
        if self.move_times < self.max_moves and abs(start_x + self.x_move - end_x) > 0.1 and abs(start_y + self.y_move - end_y) > 0.1:
            canvas.after(10, self.move_oval, canvas, oval, start_x + self.x_move, start_y + self.y_move, end_x, end_y, 0)
        else:
            self.move_times = 0
            canvas.coords(oval, end_x - 5, end_y - 5, end_x + 5, end_y + 5)

    def draw_user_EN(self,user,idx):
        colors = ['purple',  'teal','magenta', 'green', 'blue', 'yellow', 'orange', 'purple', 'pink', 'brown', 'gray', 'cyan', 'red', 'navy', 'maroon', 'olive', 'lime', 'aqua', 'indigo' ,'plum']
        tags   = "user" + str(idx)
        # self.canvas.delete(tags)
        #用户被遮挡，绘制扩展区域
        selected_mode = self.modeCombo.get()
        if  selected_mode == "GATE":
            if self.check_nLos() == True:  #只要有一个用户被遮挡，就绘制扩展区域
                if not self.canvas.find_withtag("nLos"): #防止重复绘制
                    if self.red_height == 0:
                        self.canvas.create_arc(400-self.Master2SlverDistance/2 - 7.5, 60-self.Master2SlverDistance/2 -7.5, 400+self.Master2SlverDistance/2 + 7.5, \
                                            60+self.Master2SlverDistance/2 +7.5, start=180, extent=180, fill='plum',outline="plum",tags="nLos") #FFA54F
                        
                        self.canvas.create_arc(400-self.Master2SlverDistance/2, 60-self.Master2SlverDistance/2, 400+self.Master2SlverDistance/2,  \
                                            60+self.Master2SlverDistance/2, start=180, extent=180, fill='#FF6347',outline="#FF6347")
                        if self.canvas.find_withtag(tags):
                            self.canvas.delete(tags)
                            self.user_oval[f'user_{idx}_oval'] = self.canvas.create_oval(user[idx]['Start_X']-5, user[idx]['Start_X']-5, user[idx]['Start_X']+5,  
                                                                         user[idx]['Start_X']+5, outline=colors[idx], fill=colors[idx],tags=("user" + str(idx)))
                    else:
                        self.canvas.create_arc(400-self.Master2SlverDistance/2 - 7.5, 60-self.red_height/2 -7.5, 400+self.Master2SlverDistance/2 + 7.5, \
                                            60+self.red_height/2 +7.5, start=180, extent=180, fill='plum',outline="plum",tags="nLos") #FFA54F
                        
                        self.canvas.create_arc(400-self.Master2SlverDistance/2, 60-self.red_height/2, 400+self.Master2SlverDistance/2,  \
                                            60+self.red_height/2, start=180, extent=180, fill='#FF6347',outline="#FF6347")
                        
                        if self.canvas.find_withtag(tags):
                            self.canvas.delete(tags)
                            self.user_oval[f'user_{idx}_oval'] = self.canvas.create_oval(user[idx]['Start_X']-5, user[idx]['Start_Y']-5, user[idx]['Start_X']+5,  
                                                                         user[idx]['Start_Y']+5, outline=colors[idx], fill=colors[idx],tags=("user" + str(idx)))
                        
            elif self.canvas.find_withtag("nLos"):
                self.canvas.delete("nLos")
        #首次创建User
        if not self.canvas.find_withtag(tags): 
            print(f'Create user_{idx}')
            self.user_oval[f'user_{idx}_oval'] = self.canvas.create_oval(user[idx]['CoorX_Arr'][-1]-5, user[idx]['CoorY_Arr'][-1]-5, user[idx]['CoorX_Arr'][-1]+5,  
                                                                         user[idx]['CoorY_Arr'][-1]+5, outline=colors[idx], fill=colors[idx],tags=("user" + str(idx)))
        else:
            self.move_oval(self.canvas,self.user_oval[f'user_{idx}_oval'],user[idx]['Start_X'],user[idx]['Start_Y'],user[idx]['CoorX_Arr'][-1],user[idx]['CoorY_Arr'][-1])
            # print(f'Begin X: {user[idx]["Start_X"]}, Begin Y: {user[idx]["Start_Y"]}, End X: {user[idx]["CoorX_Arr"][-1]}, End Y: {user[idx]["CoorY_Arr"][-1]}')
        user[idx]['Start_X'] = user[idx]['CoorX_Arr'][-1]
        user[idx]['Start_Y'] = user[idx]['CoorY_Arr'][-1]
    
    def draw_user_KF(self,user,idx):
        colors = ['olive', 'lime', 'aqua', 'indigo' ,'plum','purple',  'teal','magenta', 'green', 'blue', 'yellow', 'orange', 'pink', 'brown', 'gray', 'cyan', 'red', 'navy', 'maroon']
        tags   = "user" + str(idx)
        # self.canvas.delete(tags)

        # #用户被遮挡，绘制扩展区域
        # selected_mode = self.modeCombo.get()
        # if  selected_mode == "GATE":
        #     if self.check_nLos() == True:  #只要有一个用户被遮挡，就绘制扩展区域
        #         if not self.canvas.find_withtag("nLos"): #防止重复绘制
        #             self.canvas.create_arc(400-self.Master2SlverDistance/2 - 12.5, 60-self.Master2SlverDistance/2 -12.5, 400+self.Master2SlverDistance/2 + 12.5, \
        #                                 60+self.Master2SlverDistance/2 +12.5, start=180, extent=180, fill='plum',outline="plum",tags="nLos") #FFA54F
        #             self.canvas.create_arc(400-self.Master2SlverDistance/2, 60-self.Master2SlverDistance/2, 400+self.Master2SlverDistance/2,  \
        #                                 60+self.Master2SlverDistance/2, start=180, extent=180, fill='#FF6347',outline="#FF6347")
        #     elif self.canvas.find_withtag("nLos"):
        #         self.canvas.delete("nLos")

        if not self.canvas.find_withtag(tags): 
            self.user_oval[f'user_{idx}_oval'] = self.canvas.create_oval(user[0]-5, user[1]-5, user[0]+5, user[1]+5,outline=colors[idx], fill=colors[idx],tags=("user" + str(idx)))
        else:
            self.move_oval(self.canvas,self.user_oval[f'user_{idx}_oval'],self.distance_list[idx]['Start_X'],self.distance_list[idx]['Start_Y'],user[0],user[1])
        self.distance_list[idx]['Start_X'] = int(user[0])
        self.distance_list[idx]['Start_Y'] = int(user[1])
    
    def draw_basic(self):
        self.canvas.delete("all")
        # 绘制闸机(left)  以400为x原点，右下角坐标:[400-self.Master2SlverDistance/2,60]  左上角坐标[(400-self.Master2SlverDistance/2-30),10]
        # 参数: 左上角x, 左上角y, 右下角x, 右下角y, 线宽, 线条颜色, 填充颜色
        self.canvas.create_rectangle(400-self.Master2SlverDistance/2-30,10, 400-self.Master2SlverDistance/2, 60, width=1, outline="#6E6E6E", fill="#6E6E6E")

        # 绘制闸机(right) 以400为x原点，左上角坐标:[400+self.Master2SlverDistance/2,10]  右下角坐标:[(400+self.Master2SlverDistance/2+30),60]
        # 参数: 左上角x, 左上角y, 右下角x, 右下角y, 线宽, 线条颜色, 填充颜色
        self.canvas.create_rectangle(400+self.Master2SlverDistance/2, 10, 400+self.Master2SlverDistance/2+30, 60, width=1, outline="#6E6E6E", fill="#6E6E6E")

        selected_mode = self.modeCombo.get()
        if selected_mode == "GATE":
        # 绘制蓝区(矩形)   高度固定150
        # 左上角坐标[400-self.Master2SlverDistance/2,60] 右下角坐标[400+self.Master2SlverDistance/2,60+150]
            self.canvas.create_rectangle(400-self.Master2SlverDistance/2, 60, 400+self.Master2SlverDistance/2, 60+self.blue_height, width=1, outline="#4A90E2", fill="#4A90E2")

        # 绘制红区(半圆)  r=self.Master2SlverDistance/2  圆心(400,60)  
        # 左上角坐标(400-self.Master2SlverDistance/2,60-self.Master2SlverDistance/2)
        # 右下角坐标(400+self.Master2SlverDistance/2,60+self.Master2SlverDistance/2)
            if self.red_height == 0:
                self.canvas.create_arc(400-self.Master2SlverDistance/2, 60-self.Master2SlverDistance/2, 400+self.Master2SlverDistance/2, 60+self.Master2SlverDistance/2, \
                                   start=180, extent=180, fill='#FF6347',outline="#FF6347")
            else:
                self.canvas.create_arc(400-self.Master2SlverDistance/2, 60-self.red_height/2, 400+self.Master2SlverDistance/2, 60+self.red_height/2, \
                                   start=180, extent=180, fill='#FF6347',outline="#FF6347")
        #self.canvas.create_text(360,300,text="坐标:")
        elif selected_mode == 'LIFT':
            self.canvas.create_rectangle(400-self.Master2SlverDistance/2, 60, 400+self.Master2SlverDistance/2, 60+self.distance_list[0]['lift_deep'], \
                                         width=1, outline="#4A90E2", fill="#4A90E2")
        self.init_draw = 1

    def startULTDOA(self):
        # thread_com1 = threading.Thread(target=self.UL_read_data, args=('COM3', 3000000, self.queue_com1))
        # thread_com2 = threading.Thread(target=self.UL_read_data, args=('COM4', 3000000, self.queue_com2))
        # thread_com3 = threading.Thread(target=self.UL_read_data, args=('COM5', 3000000, self.queue_com3))

        # thread_com1.daemon = True  # 设置为守护线程
        # thread_com2.daemon = True  # 设置为守护线程
        # thread_com3.daemon = True  # 设置为守护线程

        # thread_com1.start()
        # thread_com2.start()
        # thread_com3.start()

        #创建锚点坐标图
        self.TagInstance = CoordinatePlotter(self.master_position,self.slave1_position, self.slave2_position)
        self.TagInstance.plot_coordinates()
        self.TagInstance.add_new_point([0,0],'blue','D','Tag')
        
        self.update_location()
        pass

    def on_mode_change(self,event=None):
        selected_mode = self.modeCombo.get()
        if selected_mode == "UL-TDOA":

            self.open_coordinate_settings()          #init settings
            
        elif selected_mode == "DL-TDOA":
            messagebox.showinfo("Tips", "功能待开发")
            pass
        
        else:
            self.draw_basic();      

    def update_location(self):
        # try:
        #     data_master = self.queue_com1.get_nowait()
        #     data_slave1 = self.queue_com2.get_nowait()
        #     data_slave2 = self.queue_com3.get_nowait()

        #     if data_master is not None and data_slave1 is not None and data_slave2 is not None:
        #         self.text_box.insert(tk.END,f"<Master:> {data_master} , <Slave1:> {data_slave1} , <Slave2:> {data_slave2} \n")
        #         self.text_box.see(tk.END)

        #         self.DSi_M = self.cacl_timediff(data_master,data_slave1,data_slave2)       #计算时间差
        #         ChanINS = ChanALG_LSE(self.DSi_M,self.Anchor_position,self.Q)
        #         self.x,self.y = ChanINS.chan_location()

        #         self.draw_ULTDOA_Location(self.x,self.y)       #TODO 这儿应该是触发式更新图中坐标，而不是每次创建
        # except queue.Empty:
        #     pass
        self.x = random.randint(1,12)
        self.y = random.randint(1,12)
        self.TagInstance.update_point(4,[self.x,self.y])
        
        self.master.after(200, self.update_location)
    
    def cacl_timediff(self,data_master,data_slave1,data_slave2):
        c = 299792458
        SYNC2_tx        = data_slave1[3]
        SYNC1_tx        = data_slave1[1]
        SYNC1_S1_rx     = data_slave1[2]
        SYNC2_S1_rx     = data_slave1[4]
        SYNC1_S2_rx     = data_slave2[2]
        SYNC2_S2_rx     = data_slave2[4]
        Master_blink_rx = data_master[0]
        Slave1_blink_rx = data_slave1[0]
        Slave2_blink_rx = data_slave2[0]

        Ref_MA                 = (SYNC2_tx + SYNC1_tx) / 2
        Propagation_delay_S1_M = (self.DSi_M[0] / c) * (15.65 ** -12)
        Propagation_delay_S2_M = (self.DSi_M[1] / c) * (15.65 ** -12)
        Ref_SA1                = ((SYNC2_S1_rx + SYNC1_S1_rx) / 2) - Propagation_delay_S1_M
        Ref_SA2                = ((SYNC2_S2_rx + SYNC1_S2_rx) / 2) - Propagation_delay_S2_M

        SFO_MA_S1 = ((SYNC2_tx - SYNC1_tx) - (SYNC2_S1_rx - SYNC1_S1_rx)) / (SYNC2_tx - SYNC1_tx)
        SFO_MA_S2 = ((SYNC2_tx - SYNC1_tx) - (SYNC2_S2_rx - SYNC1_S2_rx)) / (SYNC2_tx - SYNC1_tx)

        MA_S1_common_base_timestamp = (Master_blink_rx - Ref_MA) * (1 - SFO_MA_S1)
        MA_S2_common_base_timestamp = (Master_blink_rx - Ref_MA) * (1 - SFO_MA_S2)
        S1_common_base_timestamp    = Slave1_blink_rx - Ref_SA1
        S2_common_base_timestamp    = Slave2_blink_rx - Ref_SA2

        TDOA_MA_S1 = MA_S1_common_base_timestamp - S1_common_base_timestamp      #时间差
        TDOA_MA_S2 = MA_S2_common_base_timestamp - S2_common_base_timestamp

        TDOA_MA_S1 *= c       #距离差
        TDOA_MA_S2 *= c

        return [TDOA_MA_S1,TDOA_MA_S2]

          
    
    def open_coordinate_settings(self):
        settings_window = tk.Toplevel()  # 创建新的Toplevel窗口
        settings_window.title("Settings")
        settings_window.geometry("500x200")  # 设置窗口大小

        # 在设置窗口中添加一些设置选项
        ttk.Label(settings_window, text="Master_X:"+ Emoji._ITEMS[-106:][7].char,bootstyle = "danger").grid(row=0, column=0)
        Master_X = tk.StringVar()
        Master_X.set(5)  # 默认值
        ttk.Entry(settings_window, textvariable=Master_X,bootstyle = "info").grid(row=0, column=1)

        ttk.Label(settings_window, text="Master_Y:"+ Emoji._ITEMS[-106:][7].char,bootstyle = "danger").grid(row=0, column=2)
        Master_Y = tk.StringVar()
        Master_Y.set(1)  # 默认值
        ttk.Entry(settings_window, textvariable=Master_Y,bootstyle = "info").grid(row=0, column=3)

        ttk.Label(settings_window, text="Slave1_X:"+ Emoji._ITEMS[-106:][7].char,bootstyle = "danger").grid(row=1, column=0)
        Slave1_X = tk.IntVar()
        Slave1_X.set(-2)  # 默认值
        ttk.Entry(settings_window, textvariable=Slave1_X,bootstyle = "info").grid(row=1, column=1)

        ttk.Label(settings_window, text="Slave1_Y:"+ Emoji._ITEMS[-106:][7].char,bootstyle = "danger").grid(row=1, column=2)
        Slave1_Y = tk.IntVar()
        Slave1_Y.set(7)  # 默认值
        ttk.Entry(settings_window, textvariable=Slave1_Y,bootstyle = "info").grid(row=1, column=3)

        ttk.Label(settings_window, text="Slave2_X:"+ Emoji._ITEMS[-106:][7].char,bootstyle = "danger").grid(row=2, column=0)
        Slave2_X = tk.IntVar()
        Slave2_X.set(10)  # 默认值
        ttk.Entry(settings_window, textvariable=Slave2_X,bootstyle = "info").grid(row=2, column=1)

        ttk.Label(settings_window, text="Slave2_Y:"+ Emoji._ITEMS[-106:][7].char,bootstyle = "danger").grid(row=2, column=2)
        Slave2_Y = tk.IntVar()
        Slave2_Y.set(7)  # 默认值
        ttk.Entry(settings_window, textvariable=Slave2_Y,bootstyle = "info").grid(row=2, column=3)

        # 保存锚点坐标
        def save_settings():
            self.master_position = (int(Master_X.get()), int(Master_Y.get()))
            self.slave1_position = (int(Slave1_X.get()), int(Slave1_Y.get()))
            self.slave2_position = (int(Slave2_X.get()), int(Slave2_Y.get()))
            self.Anchor_position = [self.master_position,self.slave1_position,self.slave2_position]
            messagebox.showinfo("Settings Saved", f"Master_X: {Master_X.get()}, Master_Y: {Master_Y.get()},Slave1_X: {Slave1_X.get()}, Slave1_Y: {Slave1_Y.get()},Slave2_X: {Slave2_X.get()}, Slave2_Y: {Slave2_Y.get()}")
            settings_window.destroy()
            
            self.startULTDOA()                       #update location
        ttk.Button(settings_window, text="Save", command=save_settings, bootstyle="success").grid(row=4, column=2)

    
    #处理坐标数组，输出预测坐标
    def predict_coor(self,CoorX_Arr,CoorY_Arr):
        
        degree = 2  # 多项式的度数
        poly_features = PolynomialFeatures(degree=degree)
        x_poly = poly_features.fit_transform(CoorX_Arr.reshape(-1,1))
        
        #多项式回归
        #model = LinearRegression()
        #弹性网回归
        model = ElasticNet(alpha=1.0, l1_ratio=0.5)
        model.fit(x_poly,CoorY_Arr)
        
        #线性回归
        #model.fit(CoorX_Arr[:,np.newaxis],CoorY_Arr)
        #x_fit = np.array([CoorX_Arr[-1]]).reshape(-1,1)
        
        x_pre = poly_features.transform(np.array([[CoorX_Arr[-1]]])) 
        y_pre = model.predict(x_pre)

        return int(CoorX_Arr[-1]),int(y_pre)

    #移动平均处理数据
    def moving_average(self,data, window_size):
        cumsum_vec = np.cumsum(np.insert(data, 0, 0))
        return (cumsum_vec[window_size:] - cumsum_vec[:-window_size]) / window_size
    
    def Z_Score(self,ArrX,ArrY):
        #print(f'arr_x len={len(ArrX)}, arr_y len={len(ArrY)}')
        threshold_x = 3
        data        = np.concatenate((ArrX[:, np.newaxis], ArrY[:, np.newaxis]), axis=1)
        mean_x      = np.mean(ArrX)
        std_dev_x   = np.std(ArrX)
        z_scores_x  = (ArrX - mean_x) / std_dev_x
        #print(ArrX)
        #print(z_scores_x)
        
        outliers_x      = np.abs(z_scores_x) > threshold_x
        filtered_data_x = data[~outliers_x]
        new_arr_x       = filtered_data_x[:,0]
        new_arr_y       = filtered_data_x[:,1]
        #print(f'new_x len={len(new_arr_x)},new_y len={len(new_arr_y)}')
        if len(new_arr_x) < len(ArrX):
            print(f'delete corrdinate is :{data[outliers_x]}')
        
        return new_arr_x , new_arr_y

    def show_about(self):
        messagebox.showinfo("关于", "UwbCOM v1.0\n\n"
                             "版权所有 © 2024 可为有限公司\n"
                             "Author: @QLL\n"
                             "Email: ximing766@gmail.com\n"
                            )
            
    def run_UWB_Lift_Animation_plan_1(self):
        uwb_animation = UWBLiftAnimationPlan1(radius=self.radius,lift_deep=self.lift_deep,lift_height=self.lift_height)
        uwb_animation.start_animation()
    def run_UWB_Lift_Animation_plan_2(self):
        uwb_animation = UWBLiftAnimationPlan2(radius=self.radius,lift_deep=self.lift_deep,lift_height=self.lift_height)
        uwb_animation.start_animation()

def main():
    root   = tk.Tk()
    themes = ['cosmo', 'flatly', 'litera', 'minty', 'lumen', 'sandstone', 'yeti', 'pulse', 'united', 'morph', 'journal', 'darkly', 'superhero', \
              'solar', 'cyborg', 'vapor', 'simplex', 'cerculean']
    style = ttk.Style("minty")
    app   = SerialAssistant(root)
    print(style.theme_names())
    def change_theme(theme_name):
        style.theme_use(theme_name)

    # 创建菜单栏
    menubar = tk.Menu(root)  
    root.config(menu=menubar)
    
    # 创建主题菜单
    theme_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="主题", menu=theme_menu) 
    for theme in themes:
        theme_menu.add_command(label=theme, command=lambda t=theme: change_theme(t))

    # 创建关于菜单
    about_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="关于", menu=about_menu)
    about_menu.add_command(label="关于", command=app.show_about)

    #滤波算法选择菜单
    filter_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="滤波", menu=filter_menu)
    kalman_filter_menu = filter_menu.add_command(label="Kalman-Filter", command=lambda:app.change_filter(True))
    elasticnet_filter_menu = filter_menu.add_command(label="ElasticNet", command=lambda:app.change_filter(False))
    

    root.mainloop()

if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    main()