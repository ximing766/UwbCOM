
import tkinter as tk
from tkinter import ttk
import serial
import threading
import time
from tkinter import scrolledtext
from tkinter import messagebox
import math

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import ElasticNet
import numpy as np

class SerialAssistant:
    def __init__(self, master):
        self.master = master
        master.title("UwbCOM")
        self.master.minsize(800, 1)

        self.serial = None

        # 设置串口参数
        self.port = "COM13"  
        self.baudrate = 115200

        self.bytesize = serial.EIGHTBITS        # 数据位
        self.parity = serial.PARITY_NONE        # 校验位
        self.stopbits = serial.STOPBITS_ONE     # 停止位

        self.initial_dict = {
            "GateDistance": 0,
            "MasterDistance": 0,
            "SlaverDistance": 0,
            "CoorX_Arr": np.array([]),
            "CoorY_Arr": np.array([]),
            "ZScoreFlag" : 0                    #Z-Score异常值处理标志,记录未经过Z-Score处理过的新坐标数量
        }
        
        self.distance_list = [self.initial_dict.copy() for _ in range(20)]


        self.init_draw = 0                      #限制除用户外，其它图形多次作图
        self.flag_str = ""                      #判断需要获取的卡信息种类                   
        self.Master2SlverDistance = 0;          #画图用的闸间距

        #坐标
        self.x = 0
        self.y = 0

        # 设置主题
        theme = "clam"  # 你可以选择其他主题，如 "default", "classic", "alt", "aqua"
        ttk.Style(self.master).theme_use(theme)

        # 定义颜色方案
        self.bg_color = "#F0F5F9"  # 背景色
        self.fg_color = "#222222"  # 前景色
        self.button_bg = "#4A90E2"  # 按钮背景色
        self.button_fg = "#FFFFFF"  # 按钮前景色
        self.red_list = ['#FF6347', '#FF684C', '#FF6D51', '#FF7256', '#FF775B', '#FF7C60', '#FF8165', '#FF866A', '#FF8B6F', '#FF9074', '#FF9579', '#FF9A7E', '#FF9F83', '#FFA488', '#FFA98D', '#FFAE92', '#FFB397', '#FFB89C', '#FFBDA1', '#FFC2A6', '#FFC7AB', '#FFCCB0', '#FFD1B5', '#FFD6BA', '#FFDBBF']#, '#FFE0C4', '#FFE5C9', '#FFEACE', '#FFEFD3', '#FFF4D8', '#FFF9DD', '#FFFEE2', '#FFFFE7', '#FFFFEC', '#FFFFF1']
        self.blue_list = ['#4A90E2', '#4F95E2', '#549AE2', '#599FE2', '#5EA4E2', '#63A9E2', '#68AEE2', '#6DB3E2', '#72B8E2', '#77BDE2', '#7CC2E2', '#81C7E2', '#86CCE2', '#8BD1E2', '#90D6E2', '#95DBE2', '#9AE0E2', '#9FE5E2', '#A4EAE2', '#A9EFE2', '#AEF4E2', '#B3F9E2', '#B8FEE2', '#BDFFE2', '#C2FFE2']#, '#C7FFE2', '#CCFFE2', '#D1FFE2', '#D6FFE2', '#DBFFE2', '#E0FFE2', '#E5FFE2', '#EAFFE2', '#EFFFE2', '#F4FFE2']
        
        self.colorflag = 0

        # 应用颜色方案
        style = ttk.Style(self.master)
        style.configure("TLabelframe", background=self.bg_color)
        style.configure("TLabelframe.Label", background=self.bg_color)
        style.configure("TLabelframe.Label", foreground='black')
        style.configure("TButton", background=self.button_bg, foreground=self.button_fg,font=("Times",10))
        
        style.layout("TLabelframe.Label", [])
        self.master.configure(background=self.bg_color)

        # 创建界面
        self.create_widgets()

    def create_widgets(self):
        '''
        description: 串口设置区域
        '''        
        frame_settings = ttk.LabelFrame(self.master, text="串口设置",style="TLabelframe")
        frame_settings.grid(row=0, column=0, padx=5, pady=5,sticky='nsew')

        ttk.Label(frame_settings, text="串口号:",background=self.bg_color).grid(row=0, column=0, padx=5, pady=5,sticky='w')
        self.port_var = tk.StringVar()
        ttk.Entry(frame_settings, textvariable=self.port_var, width=10).grid(row=0, column=1, padx=5, pady=5,sticky='we')
        self.port_var.set(self.port)

        ttk.Label(frame_settings, text="波特率:",background=self.bg_color).grid(row=1, column=0, padx=5, pady=5,sticky='w')
        self.baudrate_var = tk.IntVar()
        ttk.Entry(frame_settings, textvariable=self.baudrate_var, width=10).grid(row=1, column=1, padx=5, pady=5,sticky='we')
        self.baudrate_var.set(self.baudrate)

        ttk.Button(frame_settings, text="打开串口", command=self.open_serial,style="TButton").grid(row=0, column=2, padx=5, pady=5,sticky='ns')
        ttk.Button(frame_settings, text="关闭串口", command=self.close_serial,style="TButton").grid(row=1, column=2, padx=5, pady=5,sticky='ns')

        card_Button = ttk.Button(frame_settings, text="获取卡号", command=lambda:self.send_data(11111),style="TButton").grid(row=0, column=4, padx=5, pady=5,sticky='ns')   #这块数据下行
        self.text_area1 = tk.Text(frame_settings, width=20, height=1)
        self.text_area1.grid(row=0, column=3, padx=5, pady=5, sticky='nsew')
        #card_Button.pack(side = tk.RIGHT,padx=5,pady=5)
        
        other_Button = ttk.Button(frame_settings, text="获取有效期", command=lambda:self.send_data(22222),style="TButton").grid(row=1, column=4, padx=5, pady=5,sticky='ns')
        #other_Button.pack(side = tk.RIGHT,padx=5,pady=5)
        self.text_area2 = tk.Text(frame_settings, width=20, height=1)
        self.text_area2.grid(row=1, column=3, padx=5, pady=5, sticky='nsew')
        
        other_Button1 = ttk.Button(frame_settings, text="获取余额", command=lambda:self.send_data(33333),style="TButton").grid(row=0, column=6, padx=5, pady=5,sticky='ns')
        #other_Button.pack(side = tk.RIGHT,padx=5,pady=5)
        self.text_area3 = tk.Text(frame_settings, width=20, height=1)
        self.text_area3.grid(row=0, column=5, padx=5, pady=5, sticky='nsew')
        
        other_Button2 = ttk.Button(frame_settings, text="获取交易记录", command=lambda:self.send_data(44444),style="TButton").grid(row=1, column=6, padx=5, pady=5,sticky='ns')
        #other_Button.pack(side = tk.RIGHT,padx=5,pady=5)
        self.text_area4 = tk.Text(frame_settings, width=20, height=1)
        self.text_area4.grid(row=1, column=5, padx=5, pady=5, sticky='nsew')
        

        '''
        description: 通信区域
        '''        
        
        # 创建一个标签框架
        frame_comm = ttk.LabelFrame(self.master, text="通信区", style="TLabelframe",width=800)
        frame_comm.grid(row=1, column=0, padx=5, pady=5,sticky='nsew')
        
        # 创建第二个框架
        frame2 = ttk.LabelFrame(self.master,style="TLabelframe",width=800)
        frame2.grid(row=2, column=0, padx=5, pady=5,sticky='nsew')
        
        self.text_var = tk.StringVar()  # 存储文本数据的变量
        
        # 创建并放置第一个文本框
        self.text_box = scrolledtext.ScrolledText(frame_comm, width=80, height=15)
        self.text_box.grid(row=0, column=0, padx=5, pady=5,sticky='w')

        # 创建第二个文本框并放置在同一行
        self.text_box2 = scrolledtext.ScrolledText(frame_comm, width=28, height=15)
        self.text_box2.grid(row=0, column=1, padx=1, pady=1,sticky='w')
        
        
        # 创建并放置清除第一个文本框内容的按钮
        clear_button = ttk.Button(frame2, text="清除文本", command=lambda:self.clearAndSave_text(1),style="TButton")
        clear_button.grid(row=0, column=0, padx=5, pady=1,sticky='nsew')

        # 创建并放置清除第二个文本框内容的按钮
        clear_button2 = ttk.Button(frame2, text="清除文本2", command=lambda:self.clearAndSave_text(2),style="TButton")
        clear_button2.grid(row=0, column=2, padx=5, pady=1,sticky='nsew')
        
        # 创建并放置清除第一个文本框内容的按钮
        clear_button3 = ttk.Button(frame2, text="保存文本", command=lambda:self.clearAndSave_text(3),style="TButton")
        clear_button3.grid(row=0, column=4, padx=5, pady=1,sticky='nsew')

        # 创建并放置清除第二个文本框内容的按钮
        clear_button4 = ttk.Button(frame2, text="保存文本2", command=lambda:self.clearAndSave_text(4),style="TButton")
        clear_button4.grid(row=0, column=6, padx=5, pady=1,sticky='nsew')
        


        '''
        description: 画布区域
        '''        
        frame_draw = ttk.LabelFrame(self.master,text = "画布区",style="TLabelframe",width=800)
        frame_draw.grid(row=3, column=0, padx=5, pady=5,sticky='w')

        self.canvas = tk.Canvas(frame_draw,width=800,height=350,bg="white")
        self.canvas.grid(row=0, column=0, padx=5, pady=5,sticky='w')
        
        self.master.grid_columnconfigure(0, weight=1)

        #绘制画布边界
        self.canvas.create_rectangle(0+2,0+2, 800-1, 400-1, width=1, outline="black")
        
        


    def open_serial(self):
        try:
            self.serial = serial.Serial(self.port_var.get(), self.baudrate_var.get(), timeout=1)
            self.read_thread = threading.Thread(target=self.read_data)
            self.read_thread.start()

            # self.draw_thread = threading.Thread(target=self.draw_data)
            # self.draw_thread.start()

            #self.text_box.insert(tk.END, "串口已打开\n")
            #messagebox.showinfo("tips","serial openning!")

        except Exception as e:
            self.text_box.insert(tk.END, f"打开串口失败: {e}\n")

    def close_serial(self):
        if self.serial:
            self.serial.close()
            self.text_box.insert(tk.END, "串口已关闭\n")
                                                 
    # 清空or保存文本框内容
    def clearAndSave_text(self,flag):
        if flag == 1:
            self.text_box.delete(1.0, tk.END)
        elif flag == 2:
            self.text_box2.delete(1.0,tk.END)
        elif flag == 3:
            content = self.text_box.get("1.0",tk.END)
            print(content)
            filename = "Distance_content.txt";
            with open(filename,"w" ,encoding="utf-8") as file:
                file.write(content)
            messagebox.showinfo("tips","save success!");
            
        elif flag == 4:
            content = self.text_box2.get(1.0,tk.END)
            filename = "Corr_content.csv";
            with open(filename,"w") as file:
                file.write(content)
            messagebox.showinfo("tips","save success!");
    
    def send_data(self,flag):
        #content = self.text_area1.get("1.0", tk.END)
        self.flag_str = str(flag)
        print("flag is :",self.flag_str)
        self.serial.write(self.flag_str.encode())
        
    def show_cardData(self,data):
        if self.flag_str == "11111":
            cardNumber = data[210:320][:20]
            self.text_area1.delete('1.0', tk.END)
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
            cardNumber = data[210:320][:20]
            self.text_area1.delete('1.0', tk.END)
            self.text_area1.insert(tk.END, cardNumber)     #卡号
            validPeriod = data[210:320][20:36]
            self.text_area2.delete('1.0', tk.END)
            self.text_area2.insert(tk.END, validPeriod)     #有效期
            balance = int(data[210:320][48:52],16)
            self.text_area3.delete('1.0', tk.END)
            self.text_area3.insert(tk.END, str(balance / 100) + '￥')         #余额
            transactionRecord = data[210:320][92:106]
            self.text_area4.delete('1.0', tk.END)
            self.text_area4.insert(tk.END, transactionRecord)       #交易记录
        

    def read_data(self):
        self.UserInfo = "@Qi"
        self.CardInfoChar = "1E006F";
        while self.serial and self.serial.is_open:
            try:
                data = self.serial.readline()
                if data:
                    data = data.decode('utf-8',errors='replace')

                    #卡片信息读取
                    if self.CardInfoChar in data:
                        #self.text_box.insert(tk.END,str(data))
                        #self.text_box.see(tk.END)
                        self.show_cardData(data)                                            
                    
                    if self.UserInfo in data:               
                        #获取用户下标，更新该用户的距离数据
                        idx = int(data.split(':')[7].strip())   
                        self.distance_list[idx]['MasterDistance'] = int(data.split(':')[1].strip())
                        self.distance_list[idx]['SlaverDistance'] = int(data.split(':')[3].strip())
                        self.distance_list[idx]['GateDistance'] = int(data.split(':')[5].strip())
                        self.text_box.insert(tk.END, "用户" + str(idx) + ": " + str(self.distance_list[idx]['MasterDistance']) + "," + str(self.distance_list[idx]['SlaverDistance']) +","  \
                                             + str(self.distance_list[idx]['GateDistance']) + "(主,从,门)" + "\n")

                        self.text_box.see(tk.END)
                        
                        if self.Master2SlverDistance == 0:
                            self.Master2SlverDistance = self.distance_list[idx]['GateDistance']
                    
                        if self.distance_list[idx]['MasterDistance'] != 0 and self.distance_list[idx]['SlaverDistance'] != 0 and self.distance_list[idx]['GateDistance'] !=0:
                            #计算用户坐标
                            self.x = 400 + int(((self.distance_list[idx]['SlaverDistance']**2 - self.distance_list[idx]['MasterDistance']**2) / (2*self.distance_list[idx]['GateDistance'])))
                            #异常值去除，防止开到负根
                            if abs(self.distance_list[idx]['MasterDistance']**2 - (self.x - (400 + self.distance_list[idx]['GateDistance']/2))**2) > 0:
                                self.y = 60 + int(math.sqrt(abs(self.distance_list[idx]['MasterDistance']**2 - (self.x - (400 + self.distance_list[idx]['GateDistance']/2))**2)))
                                self.text_box2.insert(tk.END,str(idx) + "," + str(self.x) + "," + str(self.y) + "\n")
                                self.text_box2.see(tk.END)
                                
                                self.distance_list[idx]['ZScoreFlag'] += 1
                                
                                self.distance_list[idx]['CoorX_Arr'] = np.append(self.distance_list[idx]['CoorX_Arr'],self.x)
                                self.distance_list[idx]['CoorY_Arr'] = np.append(self.distance_list[idx]['CoorY_Arr'],self.y)                                                           
                                #self.draw_user(self.CoorX_Arr[-1],self.CoorY_Arr[-1])                             
                                
                                if len(self.distance_list[idx]['CoorX_Arr']) == 20:                                                                
                                    
                                    #start_time = time.perf_counter()
                                    #异常值去除:Z-Score  ：每20轮调用一次，一次处理20组coornidate。保证所有数据都能被处理的同时，最大程度消减新coornidate移动带来的偏差。
                                    if self.distance_list[idx]['ZScoreFlag'] == len(self.distance_list[idx]['CoorX_Arr']):
                                        self.distance_list[idx]['CoorX_Arr'] ,self.distance_list[idx]['CoorY_Arr']= self.Z_Score(self.distance_list[idx]['CoorX_Arr'],self.distance_list[idx]['CoorY_Arr'])
                                        self.distance_list[idx]['ZScoreFlag'] = 0
                                    
                                    if len(self.distance_list[idx]['CoorX_Arr']) < 20:
                                        print('Z-Socre reduce some data,return.',len(self.distance_list[idx]['CoorX_Arr']))
                                    else:
                                        #滤波:Moving-Average
                                        self.distance_list[idx]['CoorX_Arr'] = self.moving_average(self.distance_list[idx]['CoorX_Arr'],2).astype(int)
                                        self.distance_list[idx]['CoorY_Arr'] = self.moving_average(self.distance_list[idx]['CoorY_Arr'],2).astype(int)
                                        
                                        #创建回归曲线模型，预测用户坐标位置
                                        self.predict_x,self.predict_y = self.predict_coor(self.distance_list[idx]['CoorX_Arr'],self.distance_list[idx]['CoorY_Arr'])
                                        self.text_box.insert(tk.END, "预测用户" + str(idx) + "位置..." + "\n")
                                        self.text_box.see(tk.END)
                                        
                                        #添加预测数据到数组末尾
                                        self.distance_list[idx]['CoorX_Arr'] = np.append(self.distance_list[idx]['CoorX_Arr'],self.predict_x)    
                                        self.distance_list[idx]['CoorY_Arr'] = np.append(self.distance_list[idx]['CoorY_Arr'],self.predict_y)
                                        
                                        #绘制用户坐标位置
                                        self.text_box.insert(tk.END, "绘制用户" + str(idx) + "位置..." + "\n")
                                        self.text_box.see(tk.END)
                                        self.draw_user(self.distance_list,idx)  

                                        
                                        #删除一部分，添加新的运动趋势
                                        self.distance_list[idx]['CoorX_Arr'] = np.delete(self.distance_list[idx]['CoorX_Arr'],[0])           
                                        self.distance_list[idx]['CoorY_Arr'] = np.delete(self.distance_list[idx]['CoorY_Arr'],[0])
                                                                                                                 
                                        #end_time = time.perf_counter()
                                        #run_time = end_time - start_time
    
                                        #print(f"绘制时间(不含搜集数据): {run_time} 秒")
                                else:
                                    pass
                            else:
                                print("距离数据有误，计算出Y为负数")
            except serial.SerialException:
                self.text_box.insert(tk.END, "串口连接已断开\n")
                break

            #time.sleep(0.05)

    def draw_user(self,user,idx):
        colors = ['black',  'teal','red', 'green', 'blue', 'yellow', 'orange', 'purple', 'pink', 'brown', 'gray', 'cyan', 'magenta', 'navy', 'maroon', 'olive', 'lime', 'aqua', 'indigo' ,'plum']
        tags = "user" + str(idx)
        self.canvas.delete(tags)
        #self.canvas.delete("cor_x")
        #self.canvas.delete("cor_y")
        #绘制用户(圆，需要动态变化)
        # 参数分别为：左上角坐标、右下角坐标
        self.draw_basic()   #绘制完basic后需要将所有用户点都刷新一遍
        for i in range(20):
            if len(user[i]['CoorX_Arr']) > 0: 
                self.canvas.create_oval(user[i]['CoorX_Arr'][-1]-5, user[i]['CoorY_Arr'][-1]-5, user[i]['CoorX_Arr'][-1]+5, user[i]['CoorY_Arr'][-1]+5, outline=colors[i], fill=colors[i],tags=("user" + str(i)))

        #self.canvas.create_text(400,300,text="("+str(x)+",",tags="cor_x")
        #self.canvas.create_text(440,300,text=str(y)+")",tags="cor_y")
        
    def draw_basic(self):
        
        growth_and_decay_list = [i for i in range(25)] + [i for i in range(24, -1, -1)]
        if self.init_draw == 1:

            self.colorflag = (self.colorflag + 1) % len(growth_and_decay_list) 
            self.canvas.delete("blue_area")
            self.canvas.delete("red_area")
                
            #blue area
            self.canvas.create_rectangle(400-self.Master2SlverDistance/2, 60, 400+self.Master2SlverDistance/2, 60+150, width=1, \
                                         outline=self.blue_list[growth_and_decay_list[self.colorflag]],fill=self.blue_list[growth_and_decay_list[self.colorflag]],tags = "blue_area")
            #red area
            self.canvas.create_arc(400-self.Master2SlverDistance/2, 60-self.Master2SlverDistance/2, 400+self.Master2SlverDistance/2, 60+self.Master2SlverDistance/2, start=180, extent=180, \
                                         fill=self.red_list[growth_and_decay_list[self.colorflag]],outline=self.red_list[growth_and_decay_list[self.colorflag]],tags = "red_area")
            
            

        
        if self.init_draw == 0 and self.Master2SlverDistance != 0:         #基本形状只在开始绘制（可以用线程机制取消判断）
            # 绘制闸机(left)  以400为x原点，右下角坐标:[400-self.Master2SlverDistance/2,60]  左上角坐标[(400-self.Master2SlverDistance/2-30),10]
            # 参数: 左上角x, 左上角y, 右下角x, 右下角y, 线宽, 线条颜色, 填充颜色
            self.canvas.create_rectangle(400-self.Master2SlverDistance/2-30,10, 400-self.Master2SlverDistance/2, 60, width=1, outline="#6E6E6E", fill="#6E6E6E")

            # 绘制闸机(right) 以400为x原点，左上角坐标:[400+self.Master2SlverDistance/2,10]  右下角坐标:[(400+self.Master2SlverDistance/2+30),60]
            # 参数: 左上角x, 左上角y, 右下角x, 右下角y, 线宽, 线条颜色, 填充颜色
            self.canvas.create_rectangle(400+self.Master2SlverDistance/2, 10, 400+self.Master2SlverDistance/2+30, 60, width=1, outline="#6E6E6E", fill="#6E6E6E")

            # 绘制蓝区(矩形)   高度固定150
            # 左上角坐标[400-self.Master2SlverDistance/2,60] 右下角坐标[400+self.Master2SlverDistance/2,60+150]
            self.canvas.create_rectangle(400-self.Master2SlverDistance/2, 60, 400+self.Master2SlverDistance/2, 60+150, width=1, outline="#4A90E2", fill="#4A90E2")

            # 绘制红区(半圆)  r=self.Master2SlverDistance/2  圆心(400,60)  
            # 左上角坐标(400-self.Master2SlverDistance/2,60-self.Master2SlverDistance/2)
            # 右下角坐标(400+self.Master2SlverDistance/2,60+self.Master2SlverDistance/2)
            self.canvas.create_arc(400-self.Master2SlverDistance/2, 60-self.Master2SlverDistance/2, 400+self.Master2SlverDistance/2, 60+self.Master2SlverDistance/2, start=180, extent=180, fill='#FF6347',outline="#FF6347")
            self.canvas.create_text(360,300,text="坐标:")
            self.init_draw = 1
                    

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
        data = np.concatenate((ArrX[:, np.newaxis], ArrY[:, np.newaxis]), axis=1)
        mean_x = np.mean(ArrX)
        std_dev_x = np.std(ArrX)
        z_scores_x = (ArrX - mean_x) / std_dev_x
        #print(ArrX)
        #print(z_scores_x)
        
        outliers_x = np.abs(z_scores_x) > threshold_x
        filtered_data_x = data[~outliers_x]
        new_arr_x = filtered_data_x[:,0]
        new_arr_y = filtered_data_x[:,1]
        #print(f'new_x len={len(new_arr_x)},new_y len={len(new_arr_y)}')
        if len(new_arr_x) < len(ArrX):
            print(f'delete corrdinate is :{data[outliers_x]}')
        
        return new_arr_x , new_arr_y


    # 显示关于对话框
    def show_about(self):
        messagebox.showinfo("关于", "串口助手 v1.0\n\n"
                             "版权所有 © 2024 可为有限公司\n"
                             "Author: @QLL\n"
                             )
            
            

def main():
    root = tk.Tk()
    app = SerialAssistant(root)
    style = ttk.Style()
    style.configure("AboutButton.TButton", font=("Helvetica", 7))
    # 添加一个关于按钮到主界面
    about_button = ttk.Button(root, text="关于", command=app.show_about,width=10,style="AboutButton.TButton")
    about_button.grid(row=4, column=0, padx=1, pady=1,sticky='n' )

    root.mainloop()

if __name__ == "__main__":
    main()