
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
from collections import deque
import time
import warnings
import json
import re
import requests
from packaging import version
import csv
import os
import sys
import logging
import webbrowser
import configparser
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import ElasticNet
import numpy as np
from Plot.UwbParameterPlot import MultiPlotter
from Algorithm.lift_uwb_dynamic_detect_plan import UWBLiftAnimationPlan1,UWBLiftAnimationPlan2
from Algorithm.KF_classify import KalmanFilter
from Algorithm.location.ultdoa_dynamic_location import CoordinatePlotter
from Algorithm.location.Chan_lse import ChanALG_LSE
from Algorithm.location.Chan_equation import ChanEALG

class SerialAssistant:
    def __init__(self, master):
        self.master = master

        # self.config = configparser.ConfigParser()
        # self.config.read('./config/init.ini')
        # self.version = self.config['DEFAULT']['Version']
        # self.Window = self.config['DEFAULT']['Window']

        self.version = "V1.4.1"
        self.master.title("UwbCOM " + self.version)
        self.master.minsize(950, 835)
        self.master.geometry("950x835")
        icon_path = os.path.join(os.path.dirname(__file__), 'UWBCOM.ico')
        self.master.wm_iconbitmap(icon_path)
        self.app_path = os.path.dirname(sys.executable)
        self.log_dir = os.path.join(self.app_path, 'Logs')
        print(self.log_dir)
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        

        # 设置串口参数
        self.port         = "COM1"
        self.baudrate     = 115200
        self.serial_open  = False
        self.serial_ports = []
        self.bytesize     = serial.EIGHTBITS            
        self.parity       = serial.PARITY_NONE          
        self.stopbits     = serial.STOPBITS_ONE         

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
        } for _ in range(20)]  
        #self.distance_list = [self.initial_dict.copy() for _ in range(20)]  #初始化20个用户的数据
        self.user_oval     = {}
        self.user_oval_aoa = {}
        self.user_txt      = {}
        self.user_txt_aoa  = {}

        ## ** User Define ** ##
        #Emoji._ITEMS[i].name                               "🤨"
        print(Emoji._ITEMS[-20])
        self.face                 = Emoji.get("winking face")
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

        self.CallCount            = 0
        self.table_data           = []
        self.table_one_data       = 0
        self.table_IDX            = 0
        self.last_idx             = None
        self.current_time         = 0
        self.last_call_time       = 0
        self.max_moves            = 10
        self.move_times           = 0
        self.x_move               = 0
        self.y_move               = 0

        self.create_widgets()

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

    def update_canvas(self):
        self.draw_data()
        self.master.after(100, self.update_canvas) 

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
        frame_settings.grid_columnconfigure(6, weight=1)
        frame_settings.grid_columnconfigure(7, weight=1)
        frame_settings.grid_rowconfigure(0, weight=1)
        frame_settings.grid_rowconfigure(1, weight=1)

        ttk.Label(frame_settings, text="COM" + Emoji._ITEMS[-106:][7].char,bootstyle="warning").grid(row=0, column=0, padx=5, pady=5,sticky='nsew')
        self.port_var = tk.StringVar()

        self.combo = ttk.Combobox(frame_settings, values=self.get_serial_ports(),bootstyle="info")
        self.update_combobox()
        self.combo.grid(row=0, column=1, padx=5, pady=5,sticky='nsew')

        ttk.Label(frame_settings, text="Baud" + Emoji._ITEMS[-106:][-4].char,bootstyle="warning").grid(row=1, column=0, padx=5, pady=5,sticky='nsew')
        self.baudrate_var = tk.IntVar()
        
        self.baudCombo = ttk.Combobox(frame_settings,values=['3000000','115200','9600'],bootstyle="info")
        self.baudCombo.current(0)
        self.baudCombo.grid(row=1, column=1, padx=5, pady=5,sticky='nsew')

        button_width = 8
        entry_width  = 20

        self.serial_bt = ttk.Button(frame_settings, text="打开串口", command=self.open_serial, width=button_width,bootstyle="info")
        self.serial_bt.grid(row=0, column=2, padx=5, pady=5,sticky='nsew')

        # self.modeCombo = ttk.Combobox(frame_settings,values=['GATE','LIFT','UL-TDOA','DL-TDOA'],width=button_width,bootstyle="info")
        self.modeCombo = ttk.Combobox(frame_settings,values=['GATE'],width=button_width,bootstyle="info")
        self.modeCombo.current(0)
        self.modeCombo.grid(row=1, column=2, padx=5, pady=5,sticky='nsew')
        self.modeCombo.bind("<<ComboboxSelected>>", self.on_mode_change)

        card_Button     = ttk.Button(frame_settings, text="卡  号", command=lambda:self.send_data(11111), width=button_width,bootstyle="primary").grid(row=0, column=4, padx=5, pady=5,sticky='nsew')   #这块数据下行
        self.text_area1 = ttk.Entry(frame_settings,width=entry_width,bootstyle="info")
        self.text_area1.grid(row=0, column=3, padx=5, pady=5, sticky='nsew')
        
        other_Button    = ttk.Button(frame_settings, text="有效期", command=lambda:self.send_data(22222), width=button_width,bootstyle="primary").grid(row=1, column=4, padx=5, pady=5,sticky='nsew')
        self.text_area2 = ttk.Entry(frame_settings,width=entry_width,bootstyle="info")
        self.text_area2.grid(row=1, column=3, padx=5, pady=5, sticky='nsew') 
        
        other_Button1   = ttk.Button(frame_settings, text="余  额", command=lambda:self.send_data(33333), width=button_width,bootstyle="primary").grid(row=0, column=6, padx=5, pady=5,sticky='nsew')
        self.text_area3 = ttk.Entry(frame_settings,width=entry_width,bootstyle="info")
        self.text_area3.grid(row=0, column=5, padx=5, pady=5, sticky='nsew') 
        
        other_Button2   = ttk.Button(frame_settings, text="交易记录", command=lambda:self.send_data(44444), width=button_width,bootstyle="primary").grid(row=1, column=6, padx=5, pady=5,sticky='nsew')
        self.text_area4 = ttk.Entry(frame_settings,width=entry_width,bootstyle="info")
        self.text_area4.grid(row=1, column=5, padx=5, pady=5, sticky='nsew')

        image_path = self.resource_path('logo.png')
        self.image = Image.open(image_path)
        self.image.thumbnail((100, 30))
        self.photo = ImageTk.PhotoImage(self.image)
        self.label = ttk.Label(frame_settings, image=self.photo)
        self.label.grid(row=0, column=7, columnspan=2,rowspan=1, padx=5, pady=5,sticky='nsew')
        self.label.image = self.photo

        self.txt_label = ttk.Label(frame_settings, text="仅授权小米内部使用",font=("Arial", 8),bootstyle="dark")
        self.txt_label.grid(row=1, column=7, columnspan=2,rowspan=1, padx=5, pady=5,sticky='nsew')
        
        '''
        description: 通信区域
        '''        
        # 通信区总框架
        frame_comm = ttk.LabelFrame(self.master, text="通信区",width = 900 ,height=250,bootstyle="info")
        frame_comm.grid(row=1, column=0, padx=5, pady=5,sticky='nsew')
        frame_comm.grid_columnconfigure(0, weight=1)
        frame_comm.grid_columnconfigure(1, weight=1)
        frame_comm.grid_rowconfigure(0, weight=1)
        frame_comm.grid_propagate(False)  # 防止父容器根据子控件的大小自动调整自身大小
        
        # 总框架左侧单独一个表格

        frame_comm_L = ttk.Frame(frame_comm,height=10,width=600)        
        frame_comm_L.grid(row=0, column=0, padx=1, pady=1,sticky='nsew')
        frame_comm_L.grid_rowconfigure(0,weight=1)
        frame_comm_L.grid_columnconfigure(0, weight=1)
        table_columns = ('ID','User','nLos','D-Master','D-Slaver','D-Gate','Speed','x','y','z')
        self.Table = ttk.Treeview(frame_comm_L, columns=table_columns,show='headings',bootstyle="info")
        self.Table.tag_configure('oddrow', background='#ECECEC')
        self.Table.tag_configure('evenrow', background='#FFFFFF')

        for col in table_columns:
            self.Table.heading(col, text=col, anchor='w')
        self.SetTableColumns()
        self.Table.grid(row=0, column=0, padx=1, pady=1,sticky='nsew')
        
        # 总框架右侧子总框
        frame_comm_R = ttk.Frame(frame_comm,height=10,width=300)        
        frame_comm_R.grid(row=0, column=1, padx=1, pady=1,sticky='nsew')
        frame_comm_R.grid_rowconfigure(0,weight=1)
        frame_comm_R.grid_rowconfigure(1,weight=1)
        frame_comm_R.grid_columnconfigure(0, weight=1)

        # 子总框上侧功能框
        frame_comm_R_Top_height = 5
        frame_comm_R_Top        = ttk.Frame(frame_comm_R,width=300,height=frame_comm_R_Top_height)
        frame_comm_R_Top.grid(row=0, column=0, padx=1, pady=1,sticky='nsew')
        frame_comm_R_Top.grid_rowconfigure(0,weight=1)
        frame_comm_R_Top.grid_columnconfigure(0, weight=1)   

        clear_bt = ttk.Button(frame_comm_R_Top, text="清除", command=lambda:self.on_clearAndSave_text(1),width=5,bootstyle="success-outline-toolbutton")
        clear_bt.grid(row=0, column=0, padx=1, pady=3,sticky='ew')
        
        save_bt = ttk.Button(frame_comm_R_Top, text="保存", command=lambda:self.on_clearAndSave_text(2),width=5,bootstyle="success-outline-toolbutton")
        save_bt.grid(row=1, column=0, padx=1, pady=3,sticky='ew')

        Check_bt1 = ttk.Button(frame_comm_R_Top, text="Distance", command=lambda:self.on_checkbutton_click_distance(), bootstyle="success-outline")
        Check_bt1.grid(row=0, column=1, padx=1, pady=3,sticky='ew')

        Check_bt2 = ttk.Button(frame_comm_R_Top, text="Speed", command=lambda:self.on_checkbutton_click_speed(), bootstyle="success-outline")
        Check_bt2.grid(row=1, column=1, padx=1, pady=3,sticky='ew')

        Check_bt3 = ttk.Button(frame_comm_R_Top, text="X-Y-Z", command=lambda:self.on_checkbutton_click_xyz(), bootstyle="success-outline")
        Check_bt3.grid(row=0, column=2, padx=1, pady=3,sticky='ew')

        Check_bt4 = ttk.Button(frame_comm_R_Top, text="...", command=lambda:self.on_checkbutton_click_xyz(), bootstyle="success-outline",state="disabled")
        Check_bt4.grid(row=1, column=2, padx=1, pady=3,sticky='ew')

        # 子总框下侧功能框(更具进度条的值，更新演示图中电梯的高度和深度,半径)
        frame_comm_R_Bottom = ttk.LabelFrame(frame_comm_R, width=300, height=15,text="demonstration",bootstyle="info")
        frame_comm_R_Bottom.grid(row=1, column=0, padx=1, pady=1,sticky='nsew')
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
            value = f"LIFT_D : {progressbar1.get():.1f}"
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
            value = f"LIFT_H : {progressbar2.get():.1f}"
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

        animation_button1 = ttk.Button(frame_comm_R_Bottom, text="demoA", command=self.run_UWB_Lift_Animation_plan_1, width=5,bootstyle="info",state="disable")
        animation_button1.grid(row=0, column=2, padx=1, pady=0,sticky='nsew')
        
        animation_button2 = ttk.Button(frame_comm_R_Bottom, text="demoB", command=self.run_UWB_Lift_Animation_plan_2, width=5,bootstyle="info",state="disable")
        animation_button2.grid(row=1, column=2, padx=1, pady=1,sticky='nsew')

        animation_button2 = ttk.Button(frame_comm_R_Bottom, text="...", command=self.run_UWB_Lift_Animation_plan_2, width=5,bootstyle="info",state="disable")
        animation_button2.grid(row=2, column=2, padx=1, pady=1,sticky='nsew')

        '''
        description: 画布区域
        '''        
        # frame_draw = ttk.LabelFrame(self.master,text = "功能区",bootstyle="info")
        frame_draw = ttk.LabelFrame(self.master,bootstyle="info")
        frame_draw.grid(row=3, column=0, padx=5, pady=5,sticky='nsew')
        frame_draw.grid_columnconfigure(0, weight=1)

        self.notebook = ttk.Notebook(frame_draw)
        self.notebook.grid(row = 0, column = 0, padx = 1, pady = 1, sticky = 'nsew')

        self.canvas_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.canvas_frame, text = 'canvas')
        self.canvas_frame.grid_columnconfigure(0, weight=1)

        # self.other_frame = ttk.Frame(self.notebook)
        # self.notebook.add(self.other_frame, text = 'others')
        # self.other_frame.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(self.canvas_frame,bg="white",height=390)
        self.canvas.grid(row=0, column=0, padx=5, pady=5,sticky='nsew')

        #绘制画布边界
        #self.canvas.create_rectangle(0+2,0+2, 800-1, 400-1, width=1, outline="black")
        self.master.grid_columnconfigure(0, weight=1)

        '''
        others
        '''

    def resource_path(self, relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)
    
    def table_scroll(self):
        children = self.Table.get_children()
        if children:
            self.Table.yview_moveto(1.0)
    def insert_data(self, data):
        self.table_flag = 0
        if self.table_flag==0:
            self.Table.insert('','end',values=data, tags=('evenrow',))
        else:
            self.Table.insert('','end',values=data, tags=('oddrow',))
        self.table_flag = 1 - self.table_flag
        self.table_scroll()
    
    def SetTableColumns(self):
        self.Table.column('ID',width=50, anchor='w')
        self.Table.column('User',width=35, anchor='w')
        self.Table.column('nLos',width=50, anchor='w')
        self.Table.column('D-Master',width=65, anchor='w')
        self.Table.column('D-Slaver',width=65, anchor='w')
        self.Table.column('D-Gate',width=65, anchor='w')
        self.Table.column('Speed',width=50, anchor='w')
        self.Table.column('x',width=50, anchor='w')
        self.Table.column('y',width=50, anchor='w')
        self.Table.column('z',width=50, anchor='w')
        

    def update_serial_button(self):
        if self.serial_open:
            self.serial_bt.config(text="关闭串口", command=self.close_serial,bootstyle="danger-outline")
        else:
            self.serial_bt.config(text="打开串口", command=self.open_serial,bootstyle="primary")

    def clear_table(self):
        items = self.Table.get_children()
        for item in items[::-1]:
            self.Table.delete(item)
        self.last_idx = None
        self.table_IDX = 0
        self.table_data = []

    def on_clearAndSave_text(self,flag):
        if flag == 1:
            self.clear_table()
            self.text_area1.delete(0,tk.END)
            self.text_area2.delete(0,tk.END)
            self.text_area3.delete(0,tk.END)
            self.text_area4.delete(0,tk.END)
        elif flag == 2:
            try:
                self.log_file_path = os.path.join(self.log_dir, f'UWBCOM_Data_{time.strftime("%Y%m%d%H%M%S")}.csv')
                logger = logging.getLogger('UWBLogger')
                logger.setLevel(logging.INFO)
                file_handler = logging.FileHandler(self.log_file_path)
                # file_handler.setLevel(logging.INFO)
                # log_format = logging.Formatter('%(asctime)s , %(levelname)s , %(message)s')
                log_format = logging.Formatter('%(message)s')
                file_handler.setFormatter(log_format)
                logger.addHandler(file_handler)

                columns = self.Table["columns"]
                column_names = [self.Table.heading(column)['text'] for column in columns]
                columns_str = ', '.join(column_names)
                logger.info(columns_str)
                for row_id in self.Table.get_children():
                    row = self.Table.item(row_id)['values']
                    row_str = ', '.join(map(str, row))
                    logger.info(row_str)

                messagebox.showinfo("tips",f"save file success : ./Logs/UWBCOM_Data.csv")
                logger.removeHandler(file_handler)
                file_handler.close()
            except Exception as e:
                messagebox.showerror("tips","save file failed:{}".format(e))    
    
    def on_checkbutton_click_distance(self):
        self.plotter1 = MultiPlotter(self.table_data)
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
        
    def show_cardData(self,data):
        data = data.strip()
        if self.flag_str == "11111":
            cardNumber = data[210:320][:20]
            #self.text_area1.delete(tk.END)
            self.text_area1.delete(0, tk.END)
            self.text_area1.insert(tk.END, cardNumber)     
            self.flag_str = ""
            
        elif self.flag_str == "22222":
            validPeriod = data[210:320][20:36]
            self.text_area2.delete('1.0', tk.END)
            self.text_area2.insert(tk.END, validPeriod)     
            self.flag_str = ""
            
        elif self.flag_str == "33333":
            balance = round(data[210:320][48:52],16)
            self.text_area3.delete('1.0', tk.END)
            self.text_area3.insert(tk.END, str(balance / 100))         
            self.flag_str = ""
            
        elif self.flag_str == "44444":
            transactionRecord = data[210:320][92:106]
            self.text_area4.delete('1.0', tk.END)
            self.text_area4.insert(tk.END, transactionRecord)       
            self.flag_str = ""
        
        else:   
            json_data = json.loads(data)
            cardNumber = json_data['CardNumber']
            self.text_area1.delete(0, tk.END)
            self.text_area1.insert(tk.END, cardNumber)    
            balance = json_data['Balance']
            self.text_area3.delete(0, tk.END)
            self.text_area3.insert(tk.END, str(balance / 100) + '￥')        

        
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
            # self.draw_thread = threading.Thread(target=self.draw_data)
            # self.draw_thread.start()
            
            self.serial_open = True
            self.update_serial_button()

        except Exception as e:
            messagebox.showerror("tips","open uart failed:{}".format(e))    
    
    def close_serial(self):
        try:
            if self.serial: 
                self.serial.close()
                # self.read_thread.join()
                # self.draw_thread.join()
                # messagebox.showinfo("tips","Uart has been closed" )

                self.canvas.delete("all")       
                self.Master2SlverDistance = 0   
                self.serial_open          = False
                self.update_serial_button()
        except Exception as e:
            messagebox.showerror("tips","close uart failed:{}".format(e))
    
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
                                                               
                    if self.pos_pattern.search(data):               
                        try:
                            json_data = json.loads(data)
                        except json.JSONDecodeError as e:
                            # messagebox.showerror("tips","JSON Decode Error:{}".format(e)) 
                            pass
                        idx = json_data['idx']
                        if 0 <= idx < len(self.distance_list):
                            self.distance_list[idx]['MasterDistance'] = json_data['Master']
                            self.distance_list[idx]['SlaverDistance'] = json_data['Slave']
                            self.distance_list[idx]['GateDistance']   = json_data['Gate']
                            self.distance_list[idx]['nLos']           = json_data['nLos']
                            self.distance_list[idx]['lift_deep']      = json_data['LiftDeep']
                            if json_data['User-Z'] !=0:
                                self.Use_AOA = True
                            self.x_offset = 200 if self.Use_AOA else 400
                            self.distance_list[idx]['CoorX_Arr']   = np.append(self.distance_list[idx]['CoorX_Arr'], self.x_offset + json_data['User-X'])
                            self.distance_list[idx]['CoorY_Arr']   = np.append(self.distance_list[idx]['CoorY_Arr'], 60 + json_data['User-Y'])
                            self.distance_list[idx]['CoorZ_Arr']   = np.append(self.distance_list[idx]['CoorZ_Arr'], json_data['User-Z'])
                            
                            self.distance_list[idx]['speed'].append(json_data['Speed'])
                            # print(f'User-{idx} Speed: {round(np.average(json_data["Speed"]))} cm/s')

                            if json_data['RedAreaH'] != self.red_height or json_data['BlueAreaH'] != self.blue_height:
                                self.red_height                           = json_data['RedAreaH']
                                self.blue_height                          = json_data['BlueAreaH']
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

                        self.table_one_data = (self.table_IDX, idx, self.distance_list[idx]['nLos'], self.distance_list[idx]['MasterDistance'], self.distance_list[idx]['SlaverDistance'], \
                                           self.distance_list[idx]['GateDistance'], json_data['Speed'], data_x, int(self.y-60), int(self.z))
                        self.table_IDX += 1
                        self.insert_data(self.table_one_data)
                        self.table_data.append(list(self.table_one_data))

                        # print("Use_KF:",self.Use_KF)
                        if self.Use_KF == True:
                            self.CallCount += 1
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
                                    self.CallCount += 1
                                    #19
                                    self.distance_list[idx]['CoorX_Arr'] = self.moving_average(self.distance_list[idx]['CoorX_Arr'],2).astype(int)
                                    self.distance_list[idx]['CoorY_Arr'] = self.moving_average(self.distance_list[idx]['CoorY_Arr'],2).astype(int)

                                    self.predict_x,self.predict_y = self.predict_coor(self.distance_list[idx]['CoorX_Arr'],self.distance_list[idx]['CoorY_Arr'])
                                    
                                    #20
                                    self.distance_list[idx]['CoorX_Arr'] = np.append(self.distance_list[idx]['CoorX_Arr'],self.predict_x)    
                                    self.distance_list[idx]['CoorY_Arr'] = np.append(self.distance_list[idx]['CoorY_Arr'],self.predict_y)

                                    if  abs(self.distance_list[idx]['Start_X'] - self.distance_list[idx]['CoorX_Arr'][-1]) > 2 or  \
                                        abs(self.distance_list[idx]['Start_Y'] - self.distance_list[idx]['CoorY_Arr'][-1]) > 2 or  \
                                        abs(self.distance_list[idx]['Start_Y_AOA'] - self.distance_list[idx]['CoorZ_Arr'][-1]) > 2:
                                        # self.data_queue.put([self.distance_list,idx])
                                        self.draw_user_EN(self.distance_list,idx)  

                                    self.distance_list[idx]['CoorX_Arr'] = np.delete(self.distance_list[idx]['CoorX_Arr'],[0])           
                                    self.distance_list[idx]['CoorY_Arr'] = np.delete(self.distance_list[idx]['CoorY_Arr'],[0])
                            else:
                                print("E : len(self.distance_list[idx]['CoorX_Arr']) = ",len(self.distance_list[idx]['CoorX_Arr']))
                                self.distance_list[idx]['CoorX_Arr'] = self.distance_list[idx]['CoorX_Arr'][-19:]
                                self.distance_list[idx]['CoorY_Arr'] = self.distance_list[idx]['CoorY_Arr'][-19:]
                                self.distance_list[idx]['CoorZ_Arr'] = self.distance_list[idx]['CoorZ_Arr'][-19:]
                    if self.card_pattern.search(data):
                        self.show_cardData(data) 
            except serial.SerialException:
                messagebox.showerror("tips","uart connect error:{}".format(e))    
                break
    def draw_data(self):
        if self.serial_open:
            try:
                data = self.data_queue.get_nowait()
                # print("tips","queue get data")
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
            self.canvas.create_rectangle(200-self.Master2SlverDistance/2, 60, 200+self.Master2SlverDistance/2, 60+self.blue_height, width=1, outline="#4A90E2", fill="#4A90E2",tags=("blue"))

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
                self.canvas.create_rectangle(400-self.Master2SlverDistance/2, 60, 400+self.Master2SlverDistance/2, 60+self.blue_height, width=1, outline="#4A90E2", fill="#4A90E2",tags=("blue"))
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
                            messagebox.showinfo("update", "下载失败")
                else:
                    messagebox.showinfo("update", "取消更新")
            else:
                messagebox.showinfo("update", "已是最新版本")
        else:
            print("Failed to retrieve release data")

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
    themes = ['cosmo', 'flatly', 'litera', 'minty', 'lumen', 'sandstone', 'yeti', 'pulse', 'united', 'morph', 'journal', 'darkly', 'superhero', \
              'solar', 'cyborg', 'vapor', 'simplex', 'cerculean']
    style = ttk.Style("minty")
    app   = SerialAssistant(root)
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
    # about_menu.add_command(label = "更新", command=app.update_app)

    # source_menu = tk.Menu(menubar, tearoff=0)
    # menubar.add_cascade(label="Source", command=lambda: webbrowser.open("https://github.com/ximing766/UwbCOM"))

    # filter_menu = tk.Menu(menubar, tearoff=0)
    # menubar.add_cascade(label="滤波", menu=filter_menu)
    # kalman_filter_menu = filter_menu.add_command(label="Kalman-Filter", command=lambda:app.change_filter(True))
    # elasticnet_filter_menu = filter_menu.add_command(label="ElasticNet", command=lambda:app.change_filter(False))
    
    root.mainloop()

if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    main()