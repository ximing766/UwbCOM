import re
import os
import sys
import csv
import math
import time
import json
import queue
import random
import serial
import logging
import warnings
import requests
import threading
import webbrowser
import numpy as np
import configparser
import tkinter as tk
import ttkbootstrap as ttk
from packaging import version
from collections import deque
from tkinter import messagebox
from PIL import Image, ImageTk
import serial.tools.list_ports
import matplotlib.pyplot as plt
from tkinter import scrolledtext
from ttkbootstrap.icons import Emoji 
from sklearn.linear_model import ElasticNet
from Plot.UwbParameterPlot import MultiPlotter
from Algorithm.KF_classify import KalmanFilter
from sklearn.linear_model import LinearRegression
from Algorithm.location.Chan_lse import ChanALG_LSE
from sklearn.preprocessing import PolynomialFeatures
from Algorithm.location.Chan_equation import ChanEALG
from Algorithm.location.ultdoa_dynamic_location import CoordinatePlotter
from Algorithm.lift_uwb_dynamic_detect_plan import UWBLiftAnimationPlan1,UWBLiftAnimationPlan2

class SerialAssistant:
    def __init__(self, master, log):
        self.master = master
        self.log = log
        self.version = "V1.4.7"
        self.view = "default"                                 # view没创建为单独的类，这里只能共用一个再去区分了
        self.master.title("UwbCOM " + self.version)
        self.master.minsize(850, 835)
        self.master.geometry("950x835")
        icon_path = os.path.join(os.path.dirname(__file__), 'UWBCOM.ico')
        self.master.wm_iconbitmap(icon_path)
        self.app_path = os.path.dirname(sys.executable)
        print(f'App Path: {self.app_path}')
        
        self.config = configparser.ConfigParser()
        config_path = os.path.join(self.app_path, 'config/init.ini') 

        if os.path.exists(config_path):
            self.config.read(config_path)
            if 'View' in self.config['DEFAULT']:
                self.view = self.config['DEFAULT']['View']

        self.serial_open  = False
        self.serial_ports = []                          

        self.colors = [        # 20
                'black',       # 黑色
                'darkred',     # 深红色
                'pink',        # 粉红色
                'violet',      # 紫罗兰色
                'gray',        # 灰色
                'yellow',      # 黄色2
                'orange',      # 橙色
                'purple',      # 紫色
                'royalblue',   # 皇家蓝
                'brown',       # 棕色
                'saddlebrown', # 马鞍棕
                'salmon',      # 鲑鱼色
                'wheat',       # 小麦色
                'royalblue',   # 皇家蓝
                'whitesmoke',  # 白烟色
                'sienna',      # 赭色
                'violet',      # 紫罗兰色
                'wheat',       # 小麦色
                'whitesmoke',  # 白烟色
        ]
        
        self.distance_list = [{
            "GateDistance"  : 0,
            "MasterDistance": 0,
            "SlaverDistance": 0,
            "CoorX_Arr"     : np.array([]),
            "CoorY_Arr"     : np.array([]),
            "CoorZ_Arr"     : np.array([]),
            "Start_X"       : 0,                       # User Moveing Start Point
            "Start_Y"       : 0,
            "Start_X_AOA"   : 0,
            "Start_Y_AOA"   : 0,
            "ZScoreFlag"    : 0,                       # Z-Score异常值处理标志, 记录未经过Z-Score处理过的新坐标数量
            "nLos"          : 0,                      
            "lift_deep"     : 0, 
            "KF"            : KalmanFilter(0.5, 2, 2), 
            "KF_predict"    : [0, 0],
            "speed"         : deque(maxlen=4),
            "Auth"          : 0,
            "Trans"         : 0,
        } for _ in range(20)]  
        #self.distance_list = [self.initial_dict.copy() for _ in range(20)]  #初始化20个用户的数据
        self.user_oval     = {}
        self.user_oval_aoa = {}
        self.user_txt      = {}
        self.user_txt_aoa  = {}

        self.test_gate_width = 118
        self.test_gate_height = 74
        self.base_points = [
            (0, -40), (0, 0), (1, 10), (0, 10), (-1, 10),
            (1, 60), (0, 60), (-1, 60), (1, 110), (0, 110),
            (-1, 110), (1, 160), (0, 160), (-1, 160), (0, 210)
        ]

        ## ** User Define ** ##
        #Emoji._ITEMS[i].name                               "🤨"
        # print(Emoji._ITEMS)
        self.face                 = Emoji.get("winking face")
        self.table_columns        = ('ID','User','nLos','D-Master','D-Slaver','D-Gate','Speed','x','y','z','Auth','Trans','RSSI-M')
        self.log_feature          = ('Auth','Trans')
        self.PosInfo              = "@POSI"
        self.CardInfo             = "@CARD"
        self.pos_pattern          = re.compile(self.PosInfo)
        self.card_pattern         = re.compile(self.CardInfo)
        self.init_draw            = 0                       #限制除用户外，其它图形多次作图
        self.flag_str             = ""                      #判断需要获取的卡信息种类
        self.Master2SlverDistance = 0
        self.radius               = 0
        self.nLos_radis           = 0
        self.lift_deep            = 0
        self.lift_height          = 0
        self.red_height           = 0
        self.blue_height          = 250
        
        self.queue_com1           = queue.Queue()           
        self.queue_com2           = queue.Queue()
        self.queue_com3           = queue.Queue()
        self.DSi_M                = []                     
        self.Q                    = []                      
        self.Anchor_position      = []                      #所有点坐标
        self.master_position      = []                      
        self.slave1_position      = []                     
        self.slave2_position      = []

        self.x                    = 0
        self.y                    = 0
        self.z                    = 0
        self.cor                  = []
        self.Use_KF               = False    
        self.Use_AOA              = False   

        self.table_data           = []
        self.table_one_data       = 0
        self.table_1s_data       = []
        self.table_IDX            = 0
        self.current_time         = 0
        self.last_call_time       = 0
        self.max_moves            = 6
        self.move_times           = 0
        self.x_move               = 0
        self.y_move               = 0
        # self.model                = tf.keras.models.load_model('hone_scence_model.keras')

        self.create_widgets(self.view)

        #实时更新串口选择框
        self.update_combobox_periodically()
        # self.update_canvas()
    
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
        self.master.after(3000, self.update_combobox_periodically) 

    def count_1s_data(func):
        def wrapper(self, *args, **kwargs):
            len_data = len(self.table_1s_data)
            func(self, *args, **kwargs)
            print("previous 1s data len:",len_data)
        return wrapper
    
    # @count_1s_data
    def update_Table(self):
        if self.serial_open == True:
            self.insert_data(self.table_1s_data)
        self.master.after(1000, self.update_Table)
    
    def process_distance_data(self):
        if not self.table_data:
            return 0, 0, 0, 0, 0
        data = np.array(self.table_data)
        M_dis = data[:, 3].astype(float)  # 第4列是Master距离
        S_dis = data[:, 4].astype(float)  # 第5列是Slaver距离
        M_RSSI = data[:, 12].astype(float)  # 第13列是Master的RSSI
        return np.average(M_dis), np.std(M_dis), M_RSSI[-1], np.average(S_dis), np.std(S_dis)
    
    def update_Test(self):
        if self.serial_open:
            M_avg, M_std, M_RSSI, S_avg, S_std = self.process_distance_data()
            point_type = 'A' if self.Height_entry.get() == '0.8' else 'B'
            point_index = self.Point_entry.get()
            M_cacl = self.point_distances[point_type][point_index]['D_M']  #TODO 修改内容时，这儿读到空
            S_cacl = self.point_distances[point_type][point_index]['D_S']

            self.m_avg_var.set(f"{M_avg:.1f}")
            self.m_std_var.set(f"{M_std:.1f}")
            self.m_res_var.set(f"{M_cacl - M_avg:.1f}")
            self.m_res_progress['value'] = min(abs(M_cacl - M_avg), 100)
            self.m_rssi_var.set(f"{M_RSSI:.1f}")
            self.s_avg_var.set(f"{S_avg:.1f}")
            self.s_std_var.set(f"{S_std:.1f}")
            self.s_res_var.set(f"{S_cacl - S_avg:.1f}")
            print(f"S_cacl={S_cacl},S_avg={S_avg}")
            self.s_res_progress['value'] = min(abs(S_cacl - S_avg), 100)
        self.master.after(1000, self.update_Test)

    def update_canvas(self):
        if self.serial_open == True:
            self.data_queue.put(self.distance_list)   #TODO 这儿通过self.distance_list进行消抖，小幅移动不进行绘制
            self.draw_user_after()
        self.master.after(300, self.update_canvas)  # 继续安排下一次更新

    def create_widgets(self, view = None):
        '''
        description: 串口设置区域
        '''
        frame_settings = ttk.LabelFrame(self.master, text=f'{Emoji._ITEMS[145]} + {Emoji._ITEMS[146]} + {Emoji._ITEMS[1258]}',bootstyle="info")
        frame_settings.grid(row=0, column=0, padx=5, pady=5,sticky='nsew')
        frame_settings.grid_columnconfigure(4, weight=1)  # 右侧框架占比
        frame_settings.grid_rowconfigure(0, weight=1)

        # COM端口选择
        ttk.Label(frame_settings, text="COM", font=("Arial", 10), bootstyle="info").grid(row=0, column=0, padx=2, pady=2, sticky='nsew')
        self.combo = ttk.Combobox(frame_settings, values=self.get_serial_ports(), bootstyle="info", width=10)
        self.update_combobox()
        self.combo.grid(row=0, column=1, padx=2, pady=2, sticky='nsew')

        # 波特率选择
        ttk.Label(frame_settings, text="Baud", font=("Arial", 10), bootstyle="info").grid(row=1, column=0, padx=2, pady=2, sticky='nsew')
        self.baudCombo = ttk.Combobox(frame_settings, values=['3000000','115200','9600'], bootstyle="info", width=10)
        self.baudCombo.current(0)
        self.baudCombo.grid(row=1, column=1, padx=2, pady=2, sticky='nsew')

        # 串口开关按钮
        self.serial_bt = ttk.Button(frame_settings, text="打开串口", command=self.open_serial, bootstyle="info", width=8)
        self.serial_bt.grid(row=0, column=2, padx=2, pady=2, sticky='nsew')

        # 模式选择
        if view == "default":
            self.modeCombo = ttk.Combobox(frame_settings, values=['GATE','LIFT','UL-TDOA','DL-TDOA'], bootstyle="info", width=10)
        else:
            self.modeCombo = ttk.Combobox(frame_settings, values=['GATE'], bootstyle="info", width=10)
        self.modeCombo.current(0)
        self.modeCombo.grid(row=1, column=2, padx=2, pady=2, sticky='nsew')
        self.modeCombo.bind("<<ComboboxSelected>>", self.on_mode_change)

        # 卡片信息容器（新增带边框的Frame）
        card_info_frame = ttk.Frame(frame_settings)
        card_info_frame.grid(row=0, column=4, rowspan=2, padx=10, sticky='nsew')
        card_info_frame.grid_rowconfigure(0, weight=1)
        card_info_frame.grid_rowconfigure(1, weight=1)

        # 卡号信息（使用更醒目的字体和颜色）
        ttk.Label(card_info_frame, text="卡号: ", font=("Arial", 12), bootstyle="info").grid(row=0, column=0, sticky='w')
        self.cardNo_txt = ttk.Entry(card_info_frame, font=("Consolas", 10, "bold"), bootstyle="info", width=20)
        self.cardNo_txt.insert(0, "-- -- -- --")
        self.cardNo_txt.grid(row=0, column=1, pady=2, sticky='ew')

        # 余额信息（添加货币符号和颜色强调）
        ttk.Label(card_info_frame, text="余额: ", font=("Arial", 12), bootstyle="info").grid(row=1, column=0, sticky='w')
        self.balance_txt = ttk.Entry(card_info_frame, font=("Consolas", 10, "bold"), bootstyle="success", width=20)
        self.balance_txt.insert(0, "￥0.00")
        self.balance_txt.grid(row=1, column=1, pady=2, sticky='ew')

        # Logo显示（调整到最右侧并增加间距）
        image_path = self.resource_path('logo.png')
        self.image = Image.open(image_path)
        self.image.thumbnail((100, 45))
        self.photo = ImageTk.PhotoImage(self.image)
        self.label = ttk.Label(frame_settings, image=self.photo)
        self.label.grid(row=0, column=6, rowspan=2, padx=20, sticky='e')
        self.label.image = self.photo

        # 配置列权重确保布局稳定
        # frame_settings.columnconfigure(6, weight=1)
        
        '''
        description: 通信区域
        '''        
        # 通信区总框架
        frame_comm = ttk.LabelFrame(self.master, text=f'{Emoji._ITEMS[1160]}{Emoji._ITEMS[1160]}{Emoji._ITEMS[1160]}',width = 900 ,height=250, bootstyle="info")
        frame_comm.grid(row=1, column=0, padx=5, pady=5,sticky='nsew')
        frame_comm.grid_columnconfigure(0, weight=5)
        frame_comm.grid_columnconfigure(1, weight=1)
        frame_comm.grid_rowconfigure(0, weight=1)
        frame_comm.grid_propagate(False)  # 防止父容器根据子控件的大小自动调整自身大小
        
        # 总框架左侧单独一个表格
        frame_comm_L = ttk.Frame(frame_comm,height=10)        
        frame_comm_L.grid(row=0, column=0, padx=1, pady=1,sticky='nsew')
        frame_comm_L.grid_rowconfigure(0,weight=1)
        frame_comm_L.grid_columnconfigure(0, weight=1)
        
        self.Table = ttk.Treeview(frame_comm_L, columns=self.table_columns,show='headings',bootstyle="info")
        self.Table.tag_configure('oddrow', background='#d7eaf3')
        self.Table.tag_configure('evenrow', background='#FFFFFF')

        for col in self.table_columns:
            self.Table.heading(col, text=col, anchor='w')
        self.SetTableColumns()
        self.Table.grid(row=0, column=0, padx=1, pady=1,sticky='nsew')
        
        # 总框架右侧子总框
        frame_comm_R = ttk.Frame(frame_comm,height=10)        
        frame_comm_R.grid(row=0, column=1, padx=1, pady=1,sticky='nsew')
        frame_comm_R.grid_rowconfigure(0,weight=1)
        frame_comm_R.grid_rowconfigure(1,weight=1)
        frame_comm_R.grid_columnconfigure(0, weight=1)

        # 子总框上侧功能框
        frame_comm_R_Top_height = 5
        frame_comm_R_Top        = ttk.Frame(frame_comm_R, height=frame_comm_R_Top_height)
        frame_comm_R_Top.grid(row=0, column=0, padx=1, pady=1,sticky='nsew')
        frame_comm_R_Top.grid_columnconfigure(0, weight=1)
        for i in range(8):  # 为8个按钮配置行权重
            frame_comm_R_Top.grid_rowconfigure(i, weight=1)
        # 定义按钮配置列表
        button_configs = [
            {"text": "Clear", "command": lambda: self.on_ClearWindow(), "state": "normal"},
            {"text": "Distance", "command": lambda: self.on_checkbutton_click_distance(), "state": "normal"},
            {"text": "Speed", "command": lambda: self.on_checkbutton_click_speed(), "state": "normal"},
            {"text": "X-Y-Z", "command": lambda: self.on_checkbutton_click_xyz(), "state": "normal"},
            {"text": "Reserved1", "command": None, "state": "disabled"},
            {"text": "Reserved2", "command": None, "state": "disabled"},
            {"text": "Reserved3", "command": None, "state": "disabled"},
            {"text": "Reserved4", "command": None, "state": "disabled"}
        ]
        
        # 通过循环创建按钮
        for i, config in enumerate(button_configs):
            btn = ttk.Button(
                frame_comm_R_Top,
                text=config["text"],
                command=config["command"],
                state=config["state"],
                bootstyle="success-outline",
                cursor="hand2",
            )
            btn.grid(row=i, column=0, padx=1, pady=1, sticky='ew')

        # 子总框下侧功能框(更具进度条的值，更新演示图中电梯的高度和深度,半径)
        frame_comm_R_Bottom = ttk.LabelFrame(frame_comm_R, width=300, height=15,text="demonstration",bootstyle="info")
        # frame_comm_R_Bottom.grid(row=1, column=0, padx=1, pady=1,sticky='nsew')
        frame_comm_R_Bottom.grid_rowconfigure(0,weight=1)
        frame_comm_R_Bottom.grid_rowconfigure(1,weight=1)
        frame_comm_R_Bottom.grid_rowconfigure(2,weight=1)
        frame_comm_R_Bottom.grid_columnconfigure(1, weight=1)

        # 添加第一个进度条
        progressbar1 = ttk.Scale(frame_comm_R_Bottom, orient="horizontal", length=100, from_=0, to=10,bootstyle="info")
        progressbar1.grid(row=0, column=1, padx=1, pady=1, sticky='nsew')
        progressbar1.set(2.0)

        # 添加一个标签来显示第一个进度条的值
        progressbar1_value = tk.StringVar(value=f"Deep : {progressbar1.get():.1f}")
        progressbar1_label = ttk.Label(frame_comm_R_Bottom, textvariable=progressbar1_value)
        progressbar1_label.grid(row=0, column=0, padx=1, pady=1, sticky='nsew')

        # 赋值给self.lift_deep
        def update_progressbar1_value(event):
            value = f"Deep : {progressbar1.get():.1f}"
            progressbar1_value.set(value)
            self.lift_deep = float(value.split(":")[1].strip())

        progressbar1.bind("<Motion>", update_progressbar1_value)
        progressbar1.bind("<ButtonRelease-1>", update_progressbar1_value)

        # 添加第二个进度条
        progressbar2 = ttk.Scale(frame_comm_R_Bottom, orient="horizontal", length=100, from_=0, to=10,bootstyle="warning")
        progressbar2.grid(row=1, column=1, padx=1, pady=1, sticky='nsew')
        progressbar2.set(3.0)

        # 赋值给self.lift_height
        progressbar2_value = tk.StringVar(value=f"Height : {progressbar2.get():.1f}")
        progressbar2_label = ttk.Label(frame_comm_R_Bottom, textvariable=progressbar2_value)
        progressbar2_label.grid(row=1, column=0, padx=1, pady=1, sticky='nsew')

        # 更新第二个进度条标签的值
        def update_progressbar2_value(event):
            value = f"Height : {progressbar2.get():.1f}"
            progressbar2_value.set(value)
            self.lift_height = float(value.split(":")[1].strip())

        progressbar2.bind("<Motion>", update_progressbar2_value)
        progressbar2.bind("<ButtonRelease-1>", update_progressbar2_value)

        # 添加第三个进度条
        progressbar3 = ttk.Scale(frame_comm_R_Bottom, orient="horizontal", length=100, from_=0, to=10)
        progressbar3.grid(row=2, column=1, padx=1, pady=1, sticky='nsew')
        progressbar3.set(2.0)

        # 添加一个标签来显示第三个进度条的值
        self.progressbar3_value = tk.StringVar(value=f"UWB_R : {progressbar3.get():.1f}")
        progressbar3_label      = ttk.Label(frame_comm_R_Bottom, textvariable=self.progressbar3_value)
        progressbar3_label.grid(row=2, column=0, padx=1, pady=1, sticky='nsew')

        # 更新第三个进度条标签的值
        def update_progressbar3_value(event):
            value = f"UWB_R : {progressbar3.get():.1f}"
            self.progressbar3_value.set(value)
            self.radius = float(value.split(":")[1].strip())

        progressbar3.bind("<Motion>", update_progressbar3_value)
        progressbar3.bind("<ButtonRelease-1>", update_progressbar3_value)

        ani_state = "enabled" if view == "default" else "disabled"
        animation_button1 = ttk.Button(frame_comm_R_Bottom, text="demoA", command=self.run_UWB_Lift_Animation_plan_1, width=5,bootstyle="info",state=ani_state)
        animation_button1.grid(row=0, column=2, padx=1, pady=0,sticky='nsew')
        
        animation_button2 = ttk.Button(frame_comm_R_Bottom, text="demoB", command=self.run_UWB_Lift_Animation_plan_2, width=5,bootstyle="info",state=ani_state)
        animation_button2.grid(row=1, column=2, padx=1, pady=1,sticky='nsew')

        animation_button2 = ttk.Button(frame_comm_R_Bottom, text="...", command=self.run_UWB_Lift_Animation_plan_2, width=5,bootstyle="info",state=ani_state)
        animation_button2.grid(row=2, column=2, padx=1, pady=1,sticky='nsew')

        '''
        description: 画布区域
        '''        
        frame_draw = ttk.LabelFrame(self.master,text = f'{Emoji._ITEMS[1158]}{Emoji._ITEMS[1158]}{Emoji._ITEMS[1158]}',bootstyle="info")
        frame_draw.grid(row=3, column=0, padx=5, pady=5,sticky='nsew')
        frame_draw.grid_columnconfigure(0, weight=1)

        self.notebook = ttk.Notebook(frame_draw)
        self.notebook.grid(row = 0, column = 0, padx = 1, pady = 1, sticky = 'nsew')

        self.canvas_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.canvas_frame, text = 'canvas')
        self.canvas_frame.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(self.canvas_frame,bg="white",height=390)
        self.canvas.grid(row=0, column=0, padx=5, pady=5,sticky='nsew')
        self.master.grid_columnconfigure(0, weight=1)

        self.Test_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.Test_frame, text='Test')
        self.Test_frame.grid_columnconfigure(0, weight=1, uniform='group1')
        self.Test_frame.grid_columnconfigure(1, weight=1, uniform='group1')
        
        # Master信息框
        master_frame = ttk.LabelFrame(self.Test_frame, text="Master Information", padding=10, bootstyle="info")
        master_frame.grid(row=0, column=0, padx=10, pady=5, sticky='nsew')
        
        # Master数据显示
        ttk.Label(master_frame, text="Average:", bootstyle="info").grid(row=0, column=0, padx=5, pady=2, sticky='e')
        self.m_avg_var = tk.StringVar(value="0.0")
        ttk.Label(master_frame, textvariable=self.m_avg_var, width=10, bootstyle="inverse-info").grid(row=0, column=1, padx=5, pady=2, sticky='w')
        
        ttk.Label(master_frame, text="Std:", bootstyle="info").grid(row=1, column=0, padx=5, pady=2, sticky='e')
        self.m_std_var = tk.StringVar(value="0.0")
        ttk.Label(master_frame, textvariable=self.m_std_var, width=10, bootstyle="inverse-info").grid(row=1, column=1, padx=5, pady=2, sticky='w')
        
        ttk.Label(master_frame, text="Res:", bootstyle="info").grid(row=2, column=0, padx=5, pady=2, sticky='e')
        self.m_res_var = tk.StringVar(value="0.0")
        ttk.Label(master_frame, textvariable=self.m_res_var, width=10, bootstyle="inverse-info").grid(row=2, column=1, padx=5, pady=2, sticky='w')
        self.m_res_progress = ttk.Progressbar(master_frame, length=100, maximum=100, mode='determinate', bootstyle="info")
        self.m_res_progress.grid(row=2, column=2, columnspan=4, padx=5, pady=2, sticky='ew')
        
        ttk.Label(master_frame, text="RSSI:", bootstyle="info").grid(row=3, column=0, padx=5, pady=2, sticky='e')
        self.m_rssi_var = tk.StringVar(value="0.0")
        ttk.Label(master_frame, textvariable=self.m_rssi_var, width=10, bootstyle="inverse-info").grid(row=3, column=1, padx=5, pady=2, sticky='w')
        
        ttk.Label(master_frame, text="L:", bootstyle="info").grid(row=3, column=2, padx=5, pady=2, sticky='e')
        self.Anchor_len = ttk.Entry(master_frame, width=5, bootstyle="info")
        self.Anchor_len.grid(row=3, column=3, padx=5, pady=2, sticky='w')
        self.Anchor_len.insert(0, "100")
        
        ttk.Label(master_frame, text="H:", bootstyle="info").grid(row=3, column=4, padx=5, pady=2, sticky='e')
        self.Anchor_H = ttk.Entry(master_frame, width=5, bootstyle="info")
        self.Anchor_H.grid(row=3, column=5, padx=5, pady=2, sticky='w')
        self.Anchor_H.insert(0, "90")

        self.update_anchor_btn = ttk.Button(master_frame, text="Update", command=self.update_test_points, width=8, bootstyle="info")
        self.update_anchor_btn.grid(row=3, column=6, padx=5, pady=2, sticky='w')

        # Slaver信息框
        slaver_frame = ttk.LabelFrame(self.Test_frame, text="Slaver Information", padding=10, bootstyle="success")
        slaver_frame.grid(row=0, column=1, padx=10, pady=5, sticky='nsew')
        
        # Slaver数据显示
        ttk.Label(slaver_frame, text="Average:", bootstyle="success").grid(row=0, column=0, padx=5, pady=2, sticky='e')
        self.s_avg_var = tk.StringVar(value="0.0")
        ttk.Label(slaver_frame, textvariable=self.s_avg_var, width=10, bootstyle="inverse-success").grid(row=0, column=1, padx=5, pady=2, sticky='w')
        
        ttk.Label(slaver_frame, text="Std:", bootstyle="success").grid(row=1, column=0, padx=5, pady=2, sticky='e')
        self.s_std_var = tk.StringVar(value="0.0")
        ttk.Label(slaver_frame, textvariable=self.s_std_var, width=10, bootstyle="inverse-success").grid(row=1, column=1, padx=5, pady=2, sticky='w')
        
        ttk.Label(slaver_frame, text="Res:", bootstyle="success").grid(row=2, column=0, padx=5, pady=2, sticky='e')
        self.s_res_var = tk.StringVar(value="0.0")
        ttk.Label(slaver_frame, textvariable=self.s_res_var, width=10, bootstyle="inverse-success").grid(row=2, column=1, padx=5, pady=2, sticky='w')
        self.s_res_progress = ttk.Progressbar(slaver_frame, length=100, maximum=100, mode='determinate', bootstyle="success")
        self.s_res_progress.grid(row=2, column=2, columnspan=4, padx=5, pady=2, sticky='ew')

        ttk.Label(slaver_frame, text="RSSI:", bootstyle="success").grid(row=3, column=0, padx=5, pady=2, sticky='e')
        self.s_rssi_entry = ttk.Entry(slaver_frame, width=10, bootstyle="success")
        self.s_rssi_entry.grid(row=3, column=1, padx=5, pady=2, sticky='w')
        self.s_rssi_entry.insert(0, "0.0")

        ttk.Label(slaver_frame, text="P:", bootstyle="success").grid(row=3, column=2, padx=5, pady=2, sticky='e')
        self.Point_entry = ttk.Entry(slaver_frame, width=5, bootstyle="success")
        self.Point_entry.grid(row=3, column=3, padx=5, pady=2, sticky='w')
        self.Point_entry.insert(0, "0")
        
        ttk.Label(slaver_frame, text="H:", bootstyle="success").grid(row=3, column=4, padx=5, pady=2, sticky='e')
        self.Height_entry = ttk.Entry(slaver_frame, width=5, bootstyle="success")
        self.Height_entry.grid(row=3, column=5, padx=5, pady=2, sticky='w')
        self.Height_entry.insert(0, "0.8")

        log_frame = ttk.Frame(self.Test_frame)
        log_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky='w')  # 修改sticky为'w'
        log_frame.grid_columnconfigure(0, weight=0)  # 移除左侧空白权重
        log_frame.grid_columnconfigure(4, weight=1)  # 保持右侧空白权重
        
        self.log_name_entry = ttk.Entry(log_frame, width=20, bootstyle="primary")
        self.log_name_entry.grid(row=0, column=0, padx=5, pady=2)
        ttk.Button(log_frame, text="Log", command=self.start_test_logging, bootstyle="primary", width=10).grid(row=0, column=1, padx=5, pady=2)

        '''
        others
        '''
    def start_test_logging(self):
        prefix = self.log_name_entry.get().strip()
        if not prefix:
            messagebox.showerror("错误", "请输入日志名称")
            return
    
        # 如果当前没有test logger或者prefix不同，创建新的logger
        if not hasattr(self, 'current_test_prefix') or self.current_test_prefix != prefix:
            self.current_test_prefix = prefix
            self.log.add_test_handler(prefix)
            headers = ['Point', 'Height', 'M_Avg', 'M_Std', 'M_Res', 'M_RSSI', 'S_Avg', 'S_Std', 'S_Res', 'S_RSSI']
            self.log.info_test(','.join(headers) + '\n')
        
        current_data = [
            self.Point_entry.get(),
            self.Height_entry.get(),
            self.m_avg_var.get(),
            self.m_std_var.get(),
            self.m_res_var.get(),
            self.m_rssi_var.get(),
            self.s_avg_var.get(),
            self.s_std_var.get(),
            self.s_res_var.get(),
            self.s_rssi_entry.get()
        ]
        
        self.log.info_test(','.join(current_data) + '\n')
        messagebox.showinfo("成功", f"数据已记录到日志: {prefix}")

    def update_test_points(self):
        try:
            self.test_gate_width = int(self.Anchor_len.get())
            self.test_gate_height = int(self.Anchor_H.get())
            self.MAnchor = [self.test_gate_width/2, 0, self.test_gate_height]
            self.SAnchor = [-self.test_gate_width/2, 0, self.test_gate_height]
            self.test_point = {
                **{f"A{i}": [x * (self.test_gate_width/2 if x != 0 else 1), y, 80] 
                    for i, (x, y) in enumerate(self.base_points)},
                **{f"B{i}": [x * (self.test_gate_width/2 if x != 0 else 1), y, 150] 
                    for i, (x, y) in enumerate(self.base_points)}
            }
            self.point_distances = {
                'A': {},  # A类测试点的距离
                'B': {}   # B类测试点的距离
            }
            for point_name, coords in self.test_point.items():
                m_dist = math.sqrt((coords[0] - self.MAnchor[0])**2 + 
                                    (coords[1] - self.MAnchor[1])**2 + 
                                    (coords[2] - self.MAnchor[2])**2)
                s_dist = math.sqrt((coords[0] - self.SAnchor[0])**2 + 
                                    (coords[1] - self.SAnchor[1])**2 + 
                                    (coords[2] - self.SAnchor[2])**2)
                
                # 根据点名前缀(A或B)存储距离
                point_type = point_name[0]  # 获取A或B
                point_index = point_name[1:]  # 获取数字部分
                self.point_distances[point_type][point_index] = {
                    'D_M': round(m_dist),
                    'D_S': round(s_dist)
                }
            print(self.point_distances)
        except ValueError as e:
            messagebox.showerror("错误", "请输入有效的数字")
        except Exception as e:
            messagebox.showerror("错误", f"更新测试点失败: {str(e)}")
        
    def resource_path(self, relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)
    
    def table_scroll(self):
        children = self.Table.get_children()
        if children:
            self.Table.yview_moveto(1.0)

    def insert_data(self, data):
        if data == []:
            return
        for idx, row in enumerate(data):
            self.table_IDX += 1
            row_list = list(row)
            row_list.insert(0, self.table_IDX)
            self.Table.insert('','end',values=row_list)
            self.table_data.append(row_list)

        self.table_scroll()
        self.table_1s_data = []
    
    def SetTableColumns(self):
        self.Table.column('ID',       width=45, anchor='w')
        self.Table.column('User',     width=30, anchor='w')
        self.Table.column('nLos',     width=30, anchor='w')
        self.Table.column('D-Master', width=45, anchor='w')
        self.Table.column('D-Slaver', width=45, anchor='w')
        self.Table.column('D-Gate',   width=45, anchor='w')
        self.Table.column('Speed',    width=35, anchor='w')
        self.Table.column('x',        width=35, anchor='w')
        self.Table.column('y',        width=35, anchor='w')
        self.Table.column('z',        width=35, anchor='w')
        self.Table.column('Auth',     width=35, anchor='w')
        self.Table.column('Trans',    width=35, anchor='w')
        self.Table.column('RSSI-M',   width=40, anchor='w')
        # self.Table.column('RSSI-S',   width=40, anchor='w')
        

    def update_serial_button(self):
        if self.serial_open:
            self.serial_bt.config(text="关闭串口", command=self.close_serial,bootstyle="danger-outline")
        else:
            self.serial_bt.config(text="打开串口", command=self.open_serial,bootstyle="primary")

    def clear_table(self):
        items = self.Table.get_children()
        for item in items[::-1]:
            self.Table.delete(item)
        self.table_IDX = 0
        self.table_data = []

    def on_ClearWindow(self):
        self.clear_table()
        self.cardNo_txt.delete(0,tk.END)
        self.balance_txt.delete(0,tk.END)
        self.text_area4.delete(0,tk.END)  
    
    def on_checkbutton_click_distance(self):
        self.plotter1 = MultiPlotter(self.table_data)
        # master, slave = map(int, self.distance_value.split(','))
        self.plotter1.plot_distance()

            
    def on_checkbutton_click_speed(self):
        self.plotter2 = MultiPlotter(self.table_data)
        self.plotter2.plot_speed()

    def on_checkbutton_click_xyz(self):
        self.plotter3 = MultiPlotter(self.table_data)
        self.plotter3.plot_xyz(self.Use_AOA)

    def send_data(self,flag):
        self.flag_str = str(flag)
        self.serial.write(self.flag_str.encode())
        
    def show_cardData(self, data):    
        data = data.strip()
        try:
            json_data = json.loads(data)
            cardNumber = json_data['CardNumber']
            self.cardNo_txt.configure(text=cardNumber)
            balance = json_data['Balance'] / 100
            self.balance_txt.configure(text=f"{balance:.2f}￥")
        except json.JSONDecodeError as e:
            messagebox.showerror("JSON decode error:", e)   
        
    def change_filter(self,flag):
        self.Use_KF = flag
        if flag == True:
            messagebox.showinfo("tips","filter has been changed to KalmanFilter" );
        else:
            messagebox.showinfo("tips","filter has been changed to ElasticNet" );
    
    def open_serial(self):
        try:
            self.serial = serial.Serial(self.combo.get(), self.baudCombo.get(), timeout=0.05)
            
            self.data_queue  = queue.Queue()
            self.read_thread = threading.Thread(target=self.read_data)
            self.read_thread.start()
            
            self.serial_open = True
            self.update_canvas()
            self.update_Table()
            self.update_test_points()
            self.update_Test()
            self.update_serial_button()
            self.log.add_filehandler()
            self.log.info(', '.join(self.table_columns)) # 写入Log表头
            self.log.add_second_handler()
            self.log_number = 0

        except Exception as e:
            messagebox.showerror("tips","open uart failed:{}".format(e))    
    
    def close_serial(self):
        try:
            if self.serial: 
                self.serial.close()
                # self.read_thread.join()
                # messagebox.showinfo("tips","Uart has been closed" )
                self.Master2SlverDistance = 0    #保证重绘basic
                self.serial_open          = False
                self.update_serial_button()
                self.canvas.delete("all")
                self.log.remove_filehandler()
        except Exception as e:
            messagebox.showerror("tips","Close uart failed:{}".format(e))
    
    def UL_read_data(self,port,baudrate,queue):
        ser = serial.Serial(port, baudrate, timeout=1)
        while True:
            try:
                if ser.in_waiting > 0:
                    data = ser.readline().decode('utf-8').strip()
                    queue.put(data)
            except serial.SerialException as e:
                print(f"Error reading from {port}: {e}")
                break
        pass
    
    def read_data(self):
        while self.serial and self.serial.is_open:
            try:
                if (data := self.serial.readline()):
                    data = data.decode('utf-8',errors='replace')
                    self.log.info_second(data)
                    if self.pos_pattern.search(data):       
                        match = re.search(r'\{.*?\}', data, re.DOTALL)        
                        try:
                            if match:
                                json_data = json.loads(match.group(0))
                        except json.JSONDecodeError as e:
                            print("Error decoding JSON:", e)
                            continue
                        idx = json_data['idx']
                        if 0 <= idx < len(self.distance_list):
                            self.distance_list[idx]['MasterDistance'] = json_data.get('Master')
                            self.distance_list[idx]['SlaverDistance'] = json_data.get('Slave')
                            self.distance_list[idx]['GateDistance']   = json_data.get('Gate')
                            self.distance_list[idx]['nLos']           = json_data.get('nLos')
                            self.distance_list[idx]['lift_deep']      = json_data.get('LiftDeep')
                            self.distance_list[idx]['Auth']           = json_data.get('Auth')
                            self.distance_list[idx]['Trans']          = json_data.get('Trans')
                            if json_data['User-Z'] != 0:
                                self.Use_AOA = True
                            self.x_offset = 200 if self.Use_AOA else 400
                            self.distance_list[idx]['CoorX_Arr']   = np.append(self.distance_list[idx]['CoorX_Arr'], self.x_offset + json_data.get('User-X'))
                            self.distance_list[idx]['CoorY_Arr']   = np.append(self.distance_list[idx]['CoorY_Arr'], 60 + json_data.get('User-Y'))
                            self.distance_list[idx]['CoorZ_Arr']   = np.append(self.distance_list[idx]['CoorZ_Arr'], json_data.get('User-Z'))
                            
                            self.distance_list[idx]['speed'].append(json_data.get('Speed'))
                            # print(f'User-{idx} Speed: {round(np.average(json_data["Speed"]))} cm/s')

                            if json_data.get('RedAreaH') != self.red_height or json_data.get('BlueAreaH') != self.blue_height:
                                self.red_height                           = json_data.get('RedAreaH')
                                self.blue_height                          = json_data.get('BlueAreaH')
                                print("draw_basic")
                                self.draw_basic(idx)
                        else:
                            print(f"Invalid index: {idx}")
                            continue
                        
                        if self.Master2SlverDistance == 0:
                            self.Master2SlverDistance = self.distance_list[idx]['GateDistance']
                            self.on_mode_change(idx)

                        self.x = self.distance_list[idx]['CoorX_Arr'][-1]
                        self.y = self.distance_list[idx]['CoorY_Arr'][-1]
                        self.z = self.distance_list[idx]['CoorZ_Arr'][-1]
                        if self.modeCombo.get() == "LIFT":
                            self.y = math.sqrt(abs(self.y**2 - 35*35))  

                        if self.Use_AOA == True:
                            data_x = int(self.x - 200)
                        else:
                            data_x = int(self.x - 400)

                        self.table_one_data = (idx, self.distance_list[idx]['nLos'], self.distance_list[idx]['MasterDistance'], self.distance_list[idx]['SlaverDistance'], \
                                               self.distance_list[idx]['GateDistance'], json_data['Speed'], data_x, int(self.y-60), int(self.z), json_data.get('Auth'),     \
                                               json_data.get('Trans'), int(json_data.get('LiftDeep'))/2)
                        self.table_1s_data.append(self.table_one_data)  #  Table 秒级更新
                        log_data = (self.log_number,) + self.table_one_data  #+ (self.distance_list[idx]['Auth'] , self.distance_list[idx]['Trans'])
                        self.log.info(', '.join(map(str, log_data)))    #  log 实时更新
                        self.log_number += 1

                        if self.Use_KF == True:  
                            self.cor = [self.x,self.y]
                            user_kf  = self.distance_list[idx]['KF']
                            z        = np.matrix(self.cor).T
                            user_kf.predict()
                            prediction = user_kf.update(z)
                            prediction = prediction.T.tolist()[0]
                            # print(f"KF_Filter : user {idx} prediction = {round(prediction[0]-400),round(prediction[1]-60)}")
                            self.distance_list[idx]["KF_predict"] = prediction
                            # self.data_queue.put([self.distance_list[idx]["KF_predict"],idx])
                            self.draw_user_KF(self.distance_list[idx]["KF_predict"],idx)
                        else:
                            self.distance_list[idx]['ZScoreFlag'] += 1
                            if len(self.distance_list[idx]['CoorX_Arr']) == 20:                                                                
                                #异常值去除:Z-Score  ：每20轮调用一次，一次处理20组coornidate。保证所有数据都能被处理的同时，最大程度消减新coornidate移动带来的偏差。
                                if self.distance_list[idx]['ZScoreFlag'] == len(self.distance_list[idx]['CoorX_Arr']):
                                    self.distance_list[idx]['CoorX_Arr'] ,self.distance_list[idx]['CoorY_Arr'] = self.Z_Score(self.distance_list[idx]['CoorX_Arr'],self.distance_list[idx]['CoorY_Arr'])
                                    self.distance_list[idx]['ZScoreFlag'] = 0
                                
                                if len(self.distance_list[idx]['CoorX_Arr']) < 20:
                                    print('Z-Socre reduce some data,return.',len(self.distance_list[idx]['CoorX_Arr']))
                                else:
                                    #19
                                    self.distance_list[idx]['CoorX_Arr'] = self.moving_average(self.distance_list[idx]['CoorX_Arr'],2).astype(int)
                                    self.distance_list[idx]['CoorY_Arr'] = self.moving_average(self.distance_list[idx]['CoorY_Arr'],2).astype(int)

                                    self.predict_x,self.predict_y = self.predict_coor(self.distance_list[idx]['CoorX_Arr'],self.distance_list[idx]['CoorY_Arr'])
                                    
                                    #20
                                    self.distance_list[idx]['CoorX_Arr'] = np.append(self.distance_list[idx]['CoorX_Arr'],self.predict_x)    
                                    self.distance_list[idx]['CoorY_Arr'] = np.append(self.distance_list[idx]['CoorY_Arr'],self.predict_y)

                                    # if  abs(self.distance_list[idx]['Start_X'] - self.distance_list[idx]['CoorX_Arr'][-1]) > 2 or  \
                                    #     abs(self.distance_list[idx]['Start_Y'] - self.distance_list[idx]['CoorY_Arr'][-1]) > 2 or  \
                                    #     abs(self.distance_list[idx]['Start_Y_AOA'] - self.distance_list[idx]['CoorZ_Arr'][-1]) > 2:
                                        # self.data_queue.put([self.distance_list,idx])
                                        # self.draw_user_EN(self.distance_list,idx)  

                                    self.distance_list[idx]['CoorX_Arr'] = np.delete(self.distance_list[idx]['CoorX_Arr'],[0])           
                                    self.distance_list[idx]['CoorY_Arr'] = np.delete(self.distance_list[idx]['CoorY_Arr'],[0])
                            else:
                                # print("E : len(self.distance_list[idx]['CoorX_Arr']) = ",len(self.distance_list[idx]['CoorX_Arr']))
                                self.distance_list[idx]['CoorX_Arr'] = self.distance_list[idx]['CoorX_Arr'][-19:]
                                self.distance_list[idx]['CoorY_Arr'] = self.distance_list[idx]['CoorY_Arr'][-19:]
                                self.distance_list[idx]['CoorZ_Arr'] = self.distance_list[idx]['CoorZ_Arr'][-19:]
                    elif self.card_pattern.search(data):
                        self.show_cardData(data) 
            except serial.SerialException:
                messagebox.showerror("tips","uart connect error")    
                break
    def draw_data(self):
        if self.serial_open:
            try:
                data = self.data_queue.get_nowait()
                if self.Use_KF:
                    self.draw_user_KF(data[0], data[1])
                else:
                    self.draw_user_EN(data[0], data[1])
            except queue.Empty:
                print("tips","queue is empty")
                pass
            except Exception as e:
                print("tips","draw_data error:{}".format(e)) 

    def check_nLos(self):
        for idx, item in enumerate(self.distance_list):
            if item.get('nLos') == 1:
                return True
        return False
    
    def cacl_speed(self,idx):
        speed = round(np.average(self.distance_list[idx]['speed']))
        return speed
    
    #data从队列中取出，不会被串口数据修改
    def move_user(self, canvas , data):
        self.move_times += 1
        # print(f"moveing...{self.move_times}")
        for idx, user in enumerate(data):
            if canvas.find_withtag("user" + str(idx)):
                x_move = (user['CoorX_Arr'][-1] - user['Start_X']) / 6
                y_move = (user['CoorY_Arr'][-1] - user['Start_Y']) / 6
                # print(f"U{idx} : X_move = {x_move} Y_move = {y_move} moveing...{self.move_times}")
                canvas.move(self.user_oval[f'user_{idx}_oval'], x_move, y_move)
                canvas.move(self.user_txt[f'user_{idx}_txt'], x_move, y_move)
                if self.Use_AOA:
                    end_x_aoa = user['CoorY_Arr'][-1] + 440
                    end_y_aoa = 250 - user['CoorZ_Arr'][-1]
                    x_move_aoa = (end_x_aoa - user['Start_X_AOA']) / 6
                    y_move_aoa = (end_y_aoa - user['Start_Y_AOA']) / 6
                    # print(f"U{idx} : x_move_aoa = {x_move_aoa} y_move_aoa = {y_move_aoa} moveing...{self.move_times}")
                    canvas.move(self.user_oval_aoa[f'user_{idx}_oval_AOA'], x_move_aoa, y_move_aoa)
                    canvas.move(self.user_txt_aoa[f'user_{idx}_txt_AOA'], x_move_aoa, y_move_aoa)
                if self.move_times == self.max_moves:
                    canvas.coords(self.user_oval[f'user_{idx}_oval'], user['CoorX_Arr'][-1] -5, user['CoorY_Arr'][-1] - 5, user['CoorX_Arr'][-1] + 5, user['CoorY_Arr'][-1] + 5)
                    canvas.coords(self.user_txt[f'user_{idx}_txt'], user['CoorX_Arr'][-1], user['CoorY_Arr'][-1] + 15)
                    user['Start_X'] = user['CoorX_Arr'][-1]
                    user['Start_Y'] = user['CoorY_Arr'][-1]
                    if self.Use_AOA:
                        canvas.coords(self.user_oval_aoa[f'user_{idx}_oval_AOA'], end_x_aoa -5,end_y_aoa - 5, end_x_aoa + 5, end_y_aoa + 5)
                        canvas.coords(self.user_txt_aoa[f'user_{idx}_txt_AOA'], end_x_aoa, end_y_aoa + 15)
                        user['Start_X_AOA'] = end_x_aoa
                        user['Start_Y_AOA'] = end_y_aoa
                    
        if self.move_times < self.max_moves: 
            canvas.after(10, self.move_user, canvas, data)
        else:
            self.move_times = 0

    '''
    description: 
    param {*} uniform_speed  1:匀速运动  2:减速运动 待开发 3:加速运动 待开发
    '''    
    def move_oval(self,canvas, oval, txt, start_x, start_y, end_x, end_y, oval_aoa, txt_aoa, start_x_aoa,start_y_aoa,end_x_aoa,end_y_aoa ,uniform_speed=1):
        if uniform_speed == 1:
            self.x_move = (end_x - start_x) / 10
            self.y_move = (end_y - start_y) / 10
            if self.Use_AOA:
                self.x_move_aoa = (end_x_aoa - start_x_aoa) / 10
                self.y_move_aoa = - (end_y_aoa - start_y_aoa) / 10
        
        canvas.move(oval, self.x_move, self.y_move)
        canvas.move(txt, self.x_move, self.y_move)
        if self.Use_AOA:
            canvas.move(oval_aoa, self.x_move_aoa, self.y_move_aoa)
            canvas.move(txt_aoa, self.x_move_aoa, self.y_move_aoa)
        self.move_times += 1
        # print(f"X_move = {self.x_move} Y_move = {self.y_move} moveing...{self.move_times}")
        if self.Use_AOA:
            if self.move_times < self.max_moves and abs(start_x + self.x_move - end_x) > 0.1 and abs(start_y + self.y_move - end_y) > 0.1 and abs(start_y_aoa + self.y_move_aoa - end_y_aoa) > 0.1:
                canvas.after(10, self.move_oval, canvas, oval, txt, start_x + self.x_move, start_y + self.y_move, end_x, end_y, 
                                oval_aoa, txt_aoa, start_x_aoa + self.x_move_aoa, start_y_aoa + self.y_move_aoa, end_x_aoa, end_y_aoa,0)
            else:
                self.move_times = 0
                canvas.coords(oval, end_x - 5, end_y - 5, end_x + 5, end_y + 5)
                canvas.coords(txt, end_x, end_y + 15)
                canvas.coords(oval_aoa, end_x_aoa - 5, end_y_aoa - 5, end_x_aoa + 5, end_y_aoa + 5)
                canvas.coords(txt_aoa, end_x_aoa, end_y_aoa + 15)
        else:
            if self.move_times < self.max_moves and abs(start_x + self.x_move - end_x) > 0.1 and abs(start_y + self.y_move - end_y) > 0.1:
                canvas.after(10, self.move_oval, canvas, oval, txt, start_x + self.x_move, start_y + self.y_move, end_x, end_y, None, None, None, None, None, None, 0)
            else:
                self.move_times = 0
                canvas.coords(oval, end_x - 5, end_y - 5, end_x + 5, end_y + 5)
                canvas.coords(txt, end_x, end_y + 15)
    
    def draw_user_after(self):
        #检查是否更新nLos
        if self.canvas.find_withtag("blue"):
            self.nLos_radis = self.Master2SlverDistance / 2 if self.red_height == 0 else self.red_height / 2
            if self.check_nLos() and self.Use_AOA:  # if anyone in nLos, do this
                self.canvas.create_arc(200-self.Master2SlverDistance/2 - 7.5, 60-self.nLos_radis -7.5, 200+self.Master2SlverDistance/2 + 7.5, 60+self.nLos_radis +7.5, start=180, extent=180, fill='plum',outline="plum",tags="nLos") #FFA54F
                self.canvas.tag_raise("nLos", "blue")
            elif self.check_nLos() == True and self.Use_AOA == False:
                self.canvas.create_arc(400-self.Master2SlverDistance/2 - 7.5, 60-self.nLos_radis -7.5, 400+self.Master2SlverDistance/2 + 7.5, 60+self.nLos_radis +7.5, start=180, extent=180, fill='plum',outline="plum",tags="nLos") #FFA54F
                self.canvas.tag_raise("nLos", "blue")
            elif self.canvas.find_withtag("nLos"):
                self.canvas.delete("nLos")
        else:
            # messagebox.showinfo("tips", "blue not exist")
            print("No User data, Basic graphics  not exist")
            return

        #用户创建和文本更新
        data = self.data_queue.get_nowait()
        for idx, user in enumerate(data):
            #新用户
            if not self.canvas.find_withtag("user" + str(idx)) and user['MasterDistance'] != 0 :
                print(f'Create user {idx} ')
                self.user_oval[f'user_{idx}_oval'] = self.canvas.create_oval(user['CoorX_Arr'][-1]-5, user['CoorY_Arr'][-1]-5, user['CoorX_Arr'][-1]+5,  
                                                                         user['CoorY_Arr'][-1]+5, outline=self.colors[idx], fill=self.colors[idx],tags=("user" + str(idx)))
                self.user_txt[f'user_{idx}_txt'] = self.canvas.create_text(user['CoorX_Arr'][-1], user['CoorY_Arr'][-1]+15, 
                                                                            text=f'U{idx} : 0 cm/s', fill=self.colors[idx],tags=("usertxt" + str(idx)))
                if not self.canvas.find_withtag("userAoA" + str(idx))  and self.Use_AOA:
                    print(f'Create user Height {idx} ')
                    self.user_oval_aoa[f'user_{idx}_oval_AOA'] = self.canvas.create_oval(user['CoorY_Arr'][-1]+440-5, 250 - user['CoorZ_Arr'][-1]-5, user['CoorY_Arr'][-1]+440+5,  
                                                                            250 - user['CoorZ_Arr'][-1]+5, outline=self.colors[idx], fill=self.colors[idx],tags=("userAoA" + str(idx)))
                    self.user_txt_aoa[f'user_{idx}_txt_AOA'] = self.canvas.create_text(user['CoorY_Arr'][-1]+440, 250-user['CoorZ_Arr'][-1]+15, 
                                                                            text=f"U{idx} height : {user['CoorZ_Arr'][-1]}", fill=self.colors[idx], tags=("usertxtAOA" + str(idx)))
            #老用户
            elif self.canvas.find_withtag("user" + str(idx)):
                self.canvas.itemconfigure(self.user_txt[f'user_{idx}_txt'], text=f"U{idx} : {user['speed'][-1]}cm/s")
                if self.canvas.find_withtag("userAoA" + str(idx)):
                    self.canvas.itemconfigure(self.user_txt_aoa[f'user_{idx}_txt_AOA'], text=f"U{idx} height : {user['CoorZ_Arr'][-1]}")

        self.move_user(self.canvas,data)

        pass

    def draw_user_EN(self,user,idx):
        tags   = "user" + str(idx)
        speed = self.cacl_speed(idx)

        selected_mode = self.modeCombo.get()
        self.nLos_radis = self.Master2SlverDistance/2 if self.red_height == 0 else self.red_height/2
        if  selected_mode == "GATE":
            if self.check_nLos() and self.Use_AOA:  # if anyone in nLos, do this
                self.canvas.create_arc(200-self.Master2SlverDistance/2 - 7.5, 60-self.nLos_radis -7.5, 200+self.Master2SlverDistance/2 + 7.5, 60+self.nLos_radis +7.5, start=180, extent=180, fill='plum',outline="plum",tags="nLos") #FFA54F
                self.canvas.tag_raise("nLos", "blue")
            elif self.check_nLos() == True and self.Use_AOA == False:
                self.canvas.create_arc(400-self.Master2SlverDistance/2 - 7.5, 60-self.nLos_radis -7.5, 400+self.Master2SlverDistance/2 + 7.5, 60+self.nLos_radis +7.5, start=180, extent=180, fill='plum',outline="plum",tags="nLos") #FFA54F
                self.canvas.tag_raise("nLos", "blue")
            elif self.canvas.find_withtag("nLos"):
                self.canvas.delete("nLos")
        # create user in the first time
        if not self.canvas.find_withtag(tags):
            print(f'Create user_{idx}')
            self.user_oval[f'user_{idx}_oval'] = self.canvas.create_oval(user[idx]['CoorX_Arr'][-1]-5, user[idx]['CoorY_Arr'][-1]-5, user[idx]['CoorX_Arr'][-1]+5,  
                                                                         user[idx]['CoorY_Arr'][-1]+5, outline=self.colors[idx], fill=self.colors[idx],tags=("user" + str(idx)))
            self.user_txt[f'user_{idx}_txt'] = self.canvas.create_text(user[idx]['CoorX_Arr'][-1], user[idx]['CoorY_Arr'][-1]+15, 
                                                                        text=f'U{idx} : {speed}cm/s', fill=self.colors[idx],tags=("usertxt" + str(idx)))
            if self.Use_AOA:
                self.user_oval_aoa[f'user_{idx}_oval_AOA'] = self.canvas.create_oval(user[idx]['CoorY_Arr'][-1]+440-5, 250 - user[idx]['CoorZ_Arr'][-1]-5, user[idx]['CoorY_Arr'][-1]+440+5,  
                                                                         250 - user[idx]['CoorZ_Arr'][-1]+5, outline=self.colors[idx], fill=self.colors[idx],tags=("userAoA" + str(idx)))
                self.user_txt_aoa[f'user_{idx}_txt_AOA'] = self.canvas.create_text(user[idx]['CoorY_Arr'][-1]+440, 250-user[idx]['CoorZ_Arr'][-1]+15, 
                                                                        text=f"U{idx} height : {user[idx]['CoorZ_Arr'][-1]}", fill=self.colors[idx],tags=("usertxtAOA" + str(idx)))
        else:
            self.canvas.itemconfigure(self.user_txt[f'user_{idx}_txt'], text=f'U{idx} : {speed}cm/s')
            if self.Use_AOA:
                self.canvas.itemconfigure(self.user_txt_aoa[f'user_{idx}_txt_AOA'], text=f"U{idx} height : {user[idx]['CoorZ_Arr'][-1]}")
                self.move_oval(self.canvas, self.user_oval[f'user_{idx}_oval'], self.user_txt[f'user_{idx}_txt'], user[idx]['Start_X'], user[idx]['Start_Y'], user[idx]['CoorX_Arr'][-1], user[idx]['CoorY_Arr'][-1], \
                                self.user_oval_aoa[f'user_{idx}_oval_AOA'], self.user_txt_aoa[f'user_{idx}_txt_AOA'], user[idx]['Start_X_AOA'], user[idx]['Start_Y_AOA'], user[idx]['CoorY_Arr'][-1]+440, 250 - user[idx]['CoorZ_Arr'][-1])
            else:
                self.move_oval(self.canvas, self.user_oval[f'user_{idx}_oval'], self.user_txt[f'user_{idx}_txt'], user[idx]['Start_X'], user[idx]['Start_Y'], user[idx]['CoorX_Arr'][-1], user[idx]['CoorY_Arr'][-1], None, None, None, None, None, None)
        user[idx]['Start_X'] = user[idx]['CoorX_Arr'][-1]
        user[idx]['Start_Y'] = user[idx]['CoorY_Arr'][-1]
        user[idx]['Start_X_AOA'] = user[idx]['CoorY_Arr'][-1]+440
        user[idx]['Start_Y_AOA'] = 250 - user[idx]['CoorZ_Arr'][-1]
    
    def draw_user_KF(self,user,idx):
        tags   = "user" + str(idx)
        speed = self.cacl_speed(idx)
        selected_mode = self.modeCombo.get()
        self.nLos_radis = self.red_height/2 if self.red_height != 0 else self.Master2SlverDistance/2
        if  selected_mode == "GATE":
            if self.check_nLos() and self.Use_AOA:  # if anyone in nLos, do this
                self.canvas.create_arc(200-self.Master2SlverDistance/2 - 7.5, 60-self.nLos_radis -7.5, 200+self.Master2SlverDistance/2 + 7.5, 60+self.nLos_radis +7.5, start=180, extent=180, fill='plum',outline="plum",tags="nLos") #FFA54F
                self.canvas.tag_raise("nLos", "blue")
            elif self.check_nLos() and self.Use_AOA == False:  
                self.canvas.create_arc(400-self.Master2SlverDistance/2 - 7.5, 60-self.nLos_radis -7.5, 400+self.Master2SlverDistance/2 + 7.5, 60+self.nLos_radis +7.5, start=180, extent=180, fill='plum',outline="plum",tags="nLos") #FFA54F
                self.canvas.tag_raise("nLos", "blue")
            elif self.canvas.find_withtag("nLos"):
                self.canvas.delete("nLos")

        if not self.canvas.find_withtag(tags): 
            self.user_oval[f'user_{idx}_oval'] = self.canvas.create_oval(user[0]-5, user[1]-5, user[0]+5, user[1]+5,outline=self.colors[idx], fill=self.colors[idx],tags=("user" + str(idx)))
            self.user_txt[f'user_{idx}_txt'] = self.canvas.create_text(user[0], user[1]+15, text=f'U{idx} : {speed}cm/s', fill=self.colors[idx],tags=("usertxt" + str(idx)))
            if self.Use_AOA == True:
                self.user_oval_aoa[f'user_{idx}_oval_AOA'] = self.canvas.create_oval(user[1]+440-5, 250-self.z-5, user[1]+440+5, 250-self.z+5,outline=self.colors[idx], fill=self.colors[idx],tags=("userAOA" + str(idx)))
                self.user_txt_aoa[f'user_{idx}_txt_AOA'] = self.canvas.create_text(user[1]+440, 250-self.z+15, text=f"U{idx} height : {self.distance_list[idx]['CoorZ_Arr'][-1]}", fill=self.colors[idx],tags=("usertxtAOA" + str(idx)))
        else:
            self.canvas.itemconfigure(self.user_txt[f'user_{idx}_txt'], text=f'U{idx} : {speed}cm/s')
            if self.Use_AOA == True:
                self.canvas.itemconfigure(self.user_txt_aoa[f'user_{idx}_txt_AOA'], text=f"U{idx} height : {self.distance_list[idx]['CoorZ_Arr'][-1]}")
                self.move_oval(self.canvas,self.user_oval[f'user_{idx}_oval'], self.user_txt[f'user_{idx}_txt'], self.distance_list[idx]['Start_X'], self.distance_list[idx]['Start_Y'], round(user[0]), round(user[1]), \
                            self.user_oval_aoa[f'user_{idx}_oval_AOA'], self.user_txt_aoa[f'user_{idx}_txt_AOA'], self.distance_list[idx]['Start_X_AOA'], self.distance_list[idx]['Start_Y_AOA'], round(user[1]+440), 250-self.z)
            else:
                self.move_oval(self.canvas,self.user_oval[f'user_{idx}_oval'], self.user_txt[f'user_{idx}_txt'], self.distance_list[idx]['Start_X'], self.distance_list[idx]['Start_Y'], round(user[0]), round(user[1]), None, None, None, None, None, None)
        self.distance_list[idx]['Start_X'] = round(user[0])
        self.distance_list[idx]['Start_Y'] = round(user[1])
        self.distance_list[idx]['Start_X_AOA'] = round(user[1]) + 440
        self.distance_list[idx]['Start_Y_AOA'] = 250 - self.z
    
    def toggle_call_status(self):
        pass
        if not self.canvas.find_withtag('status_circle') or not self.canvas.find_withtag('status_text'):
            return
        
        current_color = self.canvas.itemcget(self.canvas.find_withtag('status_circle')[0], 'fill')
        
        if current_color == 'red':
            self.canvas.itemconfig(self.canvas.find_withtag('status_circle'), fill='blue', outline='blue')
            self.canvas.itemconfig(self.canvas.find_withtag('status_text'), text='打电话场景', fill='blue')
        else:
            self.canvas.itemconfig(self.canvas.find_withtag('status_circle'), fill='red', outline='red')
            self.canvas.itemconfig(self.canvas.find_withtag('status_text'), text='非打电话场景', fill='red')

    def draw_basic(self, idx):
        self.canvas.delete("all")
        # AOA
        if self.Use_AOA == True:
            # 绘制闸机(left)  以400为x原点，右下角坐标:[400-self.Master2SlverDistance/2,60]  左上角坐标[(400-self.Master2SlverDistance/2-30),10]
            # 参数: 左上角x, 左上角y, 右下角x, 右下角y, 线宽, 线条颜色, 填充颜色
            self.canvas.create_rectangle(200-self.Master2SlverDistance/2-30,10, 200-self.Master2SlverDistance/2, 60, width=1, outline="#6E6E6E", fill="#6E6E6E")
            self.canvas.create_rectangle(200+self.Master2SlverDistance/2, 10, 200+self.Master2SlverDistance/2+30, 60, width=1, outline="#6E6E6E", fill="#6E6E6E")

            # 绘制蓝区(矩形)   高度固定150
            # 左上角坐标[400-self.Master2SlverDistance/2,60] 右下角坐标[400+self.Master2SlverDistance/2,60+150]
            self.blue = self.canvas.create_rectangle(200-self.Master2SlverDistance/2, 60, 200+self.Master2SlverDistance/2, 60+self.blue_height, width=1, outline="#4A90E2", fill="#4A90E2",tags=("blue"))

            # 绘制红区(半圆)  r=self.Master2SlverDistance/2  圆心(400,60)  
            # 左上角坐标(400-self.Master2SlverDistance/2,60-self.Master2SlverDistance/2)
            # 右下角坐标(400+self.Master2SlverDistance/2,60+self.Master2SlverDistance/2)
            if self.red_height == 0:
                self.canvas.create_arc(200-self.Master2SlverDistance/2, 60-self.Master2SlverDistance/2, 200+self.Master2SlverDistance/2, 60+self.Master2SlverDistance/2, \
                                start=180, extent=180, fill='#FF6347',outline="#FF6347", tags=("red"))
            else:
                self.canvas.create_arc(200-self.Master2SlverDistance/2, 60-self.red_height/2, 200+self.Master2SlverDistance/2, 60+self.red_height/2, \
                                start=180, extent=180, fill='#FF6347',outline="#FF6347", tags=("red"))
            
            #侧视图 (500,250)为原点
            self.canvas.create_rectangle(500-30, 225, 500, 250, width=1, outline="#6E6E6E", fill="#6E6E6E")
            if self.red_height == 0:
                self.canvas.create_rectangle(530-30, 100, 530-30+self.Master2SlverDistance/2, 250, width=1, outline="#FF6347", fill="#FF6347")
                self.canvas.create_rectangle(530-30+self.Master2SlverDistance/2, 100, 530-30+self.Master2SlverDistance/2+150, 250, width=1, outline="#4A90E2", fill="#4A90E2")
            else:
                self.canvas.create_rectangle(530-30, 100, 530-30+self.red_height/2, 250, width=1, outline="#FF6347", fill="#FF6347")
                self.canvas.create_rectangle(530-30+self.red_height/2, 100, 530-30+self.red_height/2+150, 250, width=1, outline="#4A90E2", fill="#4A90E2")

        else:  # TWR
            self.canvas.create_rectangle(400-self.Master2SlverDistance/2-30,10, 400-self.Master2SlverDistance/2, 60, width=1, outline="#6E6E6E", fill="#6E6E6E")
            self.canvas.create_rectangle(400+self.Master2SlverDistance/2, 10, 400+self.Master2SlverDistance/2+30, 60, width=1, outline="#6E6E6E", fill="#6E6E6E")

            selected_mode = self.modeCombo.get()
            if selected_mode == "GATE":
                self.blue = self.canvas.create_rectangle(400-self.Master2SlverDistance/2, 60, 400+self.Master2SlverDistance/2, 60+self.blue_height, width=1, outline="#4A90E2", fill="#4A90E2",tags=("blue"))
                if self.red_height == 0:
                    self.canvas.create_arc(400-self.Master2SlverDistance/2, 60-self.Master2SlverDistance/2, 400+self.Master2SlverDistance/2, 60+self.Master2SlverDistance/2, \
                                    start=180, extent=180, fill='#FF6347',outline="#FF6347", tags=("red"))
                else:
                    self.canvas.create_arc(400-self.Master2SlverDistance/2, 60-self.red_height/2, 400+self.Master2SlverDistance/2, 60+self.red_height/2, \
                                    start=180, extent=180, fill='#FF6347',outline="#FF6347", tags=("red"))
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

    def on_mode_change(self,idx,event=None):
        selected_mode = self.modeCombo.get()
        if selected_mode == "UL-TDOA":

            self.open_coordinate_settings()          #init settings
            
        elif selected_mode == "DL-TDOA":
            messagebox.showinfo("Tips", "功能待开发")
            pass
        
        else:
            self.draw_basic(idx);  
            pass    

    def update_location(self):
        # try:
        #     data_master = self.queue_com1.get_nowait()
        #     data_slave1 = self.queue_com2.get_nowait()
        #     data_slave2 = self.queue_com3.get_nowait()

        #     if data_master is not None and data_slave1 is not None and data_slave2 is not None:

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

        TDOA_MA_S1 = MA_S1_common_base_timestamp - S1_common_base_timestamp      
        TDOA_MA_S2 = MA_S2_common_base_timestamp - S2_common_base_timestamp

        TDOA_MA_S1 *= c       #距离差
        TDOA_MA_S2 *= c

        return [TDOA_MA_S1,TDOA_MA_S2]
    
    def open_coordinate_settings(self):
        settings_window = tk.Toplevel()  
        settings_window.title("Settings")
        settings_window.geometry("500x150")  

        ttk.Label(settings_window, text="Master_X:"+ Emoji._ITEMS[-106:][7].char,bootstyle = "danger").grid(row=0, column=0)
        Master_X = tk.StringVar()
        Master_X.set(5)  
        ttk.Entry(settings_window, textvariable=Master_X,bootstyle = "info").grid(row=0, column=1)

        ttk.Label(settings_window, text="Master_Y:"+ Emoji._ITEMS[-106:][7].char,bootstyle = "danger").grid(row=0, column=2)
        Master_Y = tk.StringVar()
        Master_Y.set(1)  
        ttk.Entry(settings_window, textvariable=Master_Y,bootstyle = "info").grid(row=0, column=3)

        ttk.Label(settings_window, text="Slave1_X:"+ Emoji._ITEMS[-106:][7].char,bootstyle = "danger").grid(row=1, column=0)
        Slave1_X = tk.IntVar()
        Slave1_X.set(-2)  
        ttk.Entry(settings_window, textvariable=Slave1_X,bootstyle = "info").grid(row=1, column=1)

        ttk.Label(settings_window, text="Slave1_Y:"+ Emoji._ITEMS[-106:][7].char,bootstyle = "danger").grid(row=1, column=2)
        Slave1_Y = tk.IntVar()
        Slave1_Y.set(7)  
        ttk.Entry(settings_window, textvariable=Slave1_Y,bootstyle = "info").grid(row=1, column=3)

        ttk.Label(settings_window, text="Slave2_X:"+ Emoji._ITEMS[-106:][7].char,bootstyle = "danger").grid(row=2, column=0)
        Slave2_X = tk.IntVar()
        Slave2_X.set(10)  
        ttk.Entry(settings_window, textvariable=Slave2_X,bootstyle = "info").grid(row=2, column=1)

        ttk.Label(settings_window, text="Slave2_Y:"+ Emoji._ITEMS[-106:][7].char,bootstyle = "danger").grid(row=2, column=2)
        Slave2_Y = tk.IntVar()
        Slave2_Y.set(7)  
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

        model = ElasticNet(alpha=1.0, l1_ratio=0.5)
        model.fit(x_poly,CoorY_Arr)
        
        #线性回归
        #model.fit(CoorX_Arr[:,np.newaxis],CoorY_Arr)
        #x_fit = np.array([CoorX_Arr[-1]]).reshape(-1,1)
        
        x_pre = poly_features.transform(np.array([[CoorX_Arr[-1]]])) 
        y_pre = model.predict(x_pre)

        return int(CoorX_Arr[-1]),int(y_pre)

    def moving_average(self,data, window_size):
        cumsum_vec = np.cumsum(np.insert(data, 0, 0))
        return (cumsum_vec[window_size:] - cumsum_vec[:-window_size]) / window_size
    
    def Z_Score(self,ArrX,ArrY):
        threshold_x = 3
        data        = np.concatenate((ArrX[:, np.newaxis], ArrY[:, np.newaxis]), axis=1)
        mean_x      = np.mean(ArrX)
        std_dev_x   = np.std(ArrX)
        z_scores_x  = (ArrX - mean_x) / std_dev_x
        
        outliers_x      = np.abs(z_scores_x) > threshold_x
        filtered_data_x = data[~outliers_x]
        new_arr_x       = filtered_data_x[:,0]
        new_arr_y       = filtered_data_x[:,1]
        if len(new_arr_x) < len(ArrX):
            print(f'delete corrdinate is :{data[outliers_x]}')
        
        return new_arr_x , new_arr_y
    def update_app(self):
        url = "https://api.github.com/repos/{owner}/{repo}/releases/latest"
        owner = "ximing766"
        repo = "UwbCOM"
        print(url.format(owner=owner, repo=repo))
        response = requests.get(url.format(owner=owner, repo=repo))

        if response.status_code == 200:
            release_data = response.json()
            latest_version = release_data['tag_name']
            if version.parse(latest_version) > version.parse(self.version):
                self.result = messagebox.askquestion("update", "发现新版本，是否更新？")
                if self.result == "yes":
                    for asset in release_data['assets']:
                        download_url = asset['browser_download_url']
                        print(f"Download URL: {download_url}")
                        response = requests.get(download_url, stream=True)
                        if response.status_code == 200:
                            with open(asset['name'], 'wb') as file:
                                for chunk in response.iter_content(chunk_size=8192):
                                    file.write(chunk)
                            messagebox.showinfo("update", f"更新完成:{asset['name']}")
                        else:
                            messagebox.showerror("update", "下载失败")
                else:
                    messagebox.showerror("update", "取消更新")
            else:
                messagebox.showerror("update", "已是最新版本")
        else:
            messagebox.showerror("update", "please check your network")

    def show_about(self):
        messagebox.showinfo("关于", f"UwbCOM {self.version}\n\n"
                             "版权所有 © 2024 可为信息技术有限公司\n"
                             "Author: @QLL\n"
                             "Email: Tommy.yang@cardshare.cn\n"
                            )
        
    def run_UWB_Lift_Animation_plan_1(self):
        uwb_animation = UWBLiftAnimationPlan1(radius=self.radius,lift_deep=self.lift_deep,lift_height=self.lift_height)
        uwb_animation.start_animation()
    def run_UWB_Lift_Animation_plan_2(self):
        uwb_animation = UWBLiftAnimationPlan2(radius=self.radius,lift_deep=self.lift_deep,lift_height=self.lift_height)
        uwb_animation.start_animation()

def main():
    root   = tk.Tk()
    log = Log("UwbCOM")
    themes = ['cosmo', 'flatly', 'litera', 'minty', 'lumen', 'sandstone', 'yeti', 'pulse', 'united', 'morph', 'journal', 'darkly', 'superhero', \
              'solar', 'cyborg', 'vapor', 'simplex', 'cerculean']
    style = ttk.Style("minty")
    app   = SerialAssistant(root, log)
    print(style.theme_names())
    def change_theme(theme_name):
        style.theme_use(theme_name)

    menubar = tk.Menu(root)  
    root.config(menu=menubar)
    
    theme_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="主题", menu=theme_menu) 
    for theme in themes:
        theme_menu.add_command(label=theme, command=lambda t=theme: change_theme(t))

    about_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="关于", menu=about_menu)
    about_menu.add_command(label = "关于", command=app.show_about)
    if app.view == "default":
        about_menu.add_command(label = "更新", command=app.update_app)

        # source_menu = tk.Menu(menubar, tearoff=0)
        # menubar.add_cascade(label="Source", command=lambda: webbrowser.open("https://github.com/ximing766/UwbCOM"))

        filter_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="滤波", menu=filter_menu)
        filter_menu.add_command(label="Kalman-Filter", command=lambda:app.change_filter(True))
        filter_menu.add_command(label="ElasticNet", command=lambda:app.change_filter(False))
    
    root.mainloop()


class Log:
    def __init__(self,name,level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.second_logger = logging.getLogger(name + "_second")
        self.test_logger = logging.getLogger(name + "_Test")
        self.logger.setLevel(level)
        self.second_logger.setLevel(level)
        self.test_logger.setLevel(level)
        self.log_queue = queue.Queue()
        self.second_log_queue = queue.Queue()
        self.test_log_queue = queue.Queue()
        
        self.thread = threading.Thread(target=self.log_handler)
        self.thread.daemon = True
        self.thread.start()
        
        self.second_thread = threading.Thread(target=self.second_log_handler)
        self.second_thread.daemon = True
        self.second_thread.start()

        self.test_thread = threading.Thread(target=self.test_log_handler)
        self.test_thread.daemon = True
        self.test_thread.start()

        self.root_path = os.path.dirname(sys.executable)
        self.log_dir = os.path.join(self.root_path,'UwbCOMLog')
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def add_filehandler(self):
        self.log_file_path = os.path.join(self.log_dir, f'UwbCOM_Log_{time.strftime("%Y-%m-%d-%H-%M-%S")}.csv')
        self.file_handler = logging.FileHandler(self.log_file_path)
        self.log_format = logging.Formatter('%(asctime)s , %(levelname)s , %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        self.file_handler.setFormatter(self.log_format)
        self.logger.addHandler(self.file_handler)
    
    def add_second_handler(self):
        self.second_log_file_path = os.path.join(self.log_dir, f'UwbCOM_Second_Log_{time.strftime("%Y-%m-%d-%H-%M-%S")}.log')
        self.second_file_handler = logging.FileHandler(self.second_log_file_path,mode='a')
        self.second_log_format = logging.Formatter('[%(asctime)s.%(msecs)03d] | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        self.second_file_handler.terminator = ''
        self.second_file_handler.setFormatter(self.second_log_format)
        self.second_logger.addHandler(self.second_file_handler)
    
    def add_test_handler(self, prefix=''):
        file_name = f'{prefix}_UwbCOM_Test_Log_{time.strftime("%Y-%m-%d-%H-%M-%S")}.csv' if prefix else f'UwbCOM_Test_Log_{time.strftime("%Y-%m-%d-%H-%M-%S")}.csv'
        self.test_log_file_path = os.path.join(self.log_dir, file_name)
        self.test_file_handler = logging.FileHandler(self.test_log_file_path, mode='a')
        self.test_log_format = logging.Formatter('%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        self.test_file_handler.terminator = ''
        self.test_file_handler.setFormatter(self.test_log_format)
        self.test_logger.addHandler(self.test_file_handler)
    
    def remove_filehandler(self):
        # 修改现有的remove方法，添加test handler的清理
        if hasattr(self, 'file_handler'):
            self.logger.removeHandler(self.file_handler)
            self.file_handler.close()
        if hasattr(self, 'second_file_handler'):
            self.second_logger.removeHandler(self.second_file_handler)
            self.second_file_handler.close()
        
    
    def log_handler(self):
        while True:
            try:
                level, msg = self.log_queue.get()
                if msg is None:
                    break
                if level == 'info':
                    self.logger.info(msg)
                elif level == 'warning':
                    self.logger.warning(msg)
                elif level == 'error':
                    self.logger.error(msg)
                elif level == 'debug':
                    self.logger.debug(msg)
                
            except queue.Empty:
                pass
    
    def second_log_handler(self):
        while True:
            try:
                level, msg = self.second_log_queue.get()
                if msg is None:
                    break
                if level == 'info':
                    self.second_logger.info(msg)
                elif level == 'warning':
                    self.second_logger.warning(msg)
                elif level == 'error':
                    self.second_logger.error(msg)
                elif level == 'debug':
                    self.second_logger.debug(msg)
            except queue.Empty:
                pass

    def test_log_handler(self):
        """处理test logger的消息队列"""
        while True:
            try:
                level, msg = self.test_log_queue.get()
                if msg is None:
                    break
                if level == 'info':
                    self.test_logger.info(msg)
                elif level == 'warning':
                    self.test_logger.warning(msg)
                elif level == 'error':
                    self.test_logger.error(msg)
                elif level == 'debug':
                    self.test_logger.debug(msg)
            except queue.Empty:
                pass

    def info(self, msg):
        self.log_queue.put(('info', msg))

    def warning(self, msg):
        self.log_queue.put(('warning', msg))

    def error(self, msg):
        self.log_queue.put(('error', msg))
    
    def debug(self, msg):
        self.log_queue.put(('debug', msg))

    def info_second(self, msg):
        self.second_log_queue.put(('info', msg))

    def warning_second(self, msg):
        self.second_log_queue.put(('warning', msg))

    def error_second(self, msg):
        self.second_log_queue.put(('error', msg))
    
    def debug_second(self, msg):
        self.second_log_queue.put(('debug', msg))
    
    def info_test(self, msg):
        """发送info级别的消息到test logger"""
        self.test_log_queue.put(('info', msg))

    def warning_test(self, msg):
        """发送warning级别的消息到test logger"""
        self.test_log_queue.put(('warning', msg))

    def error_test(self, msg):
        """发送error级别的消息到test logger"""
        self.test_log_queue.put(('error', msg))

if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    main()