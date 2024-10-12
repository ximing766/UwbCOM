# 
# Copyright 2023 NXP
# 
# NXP Confidential. This software is owned or controlled by NXP and may only be
# used strictly in accordance with the applicable license terms. By expressly
# accepting such terms or by downloading,installing, activating and/or otherwise
# using the software, you are agreeing that you have read,and that you agree to
# comply with and are bound by, such license terms. If you do not agree to be
# bound by the applicable license terms, then you may not retain, install, activate
# or otherwise use the software.
# 
# 

#from Coordinate import Coordinate
#from AlgorithmsMethods import apply_smoothing_algorithm, configure_algorithm
#from screeninfo import get_monitors
import threading
from tkinter import *
from tkinter import messagebox, simpledialog
import tkinter as tk
import sys
import signal
import serial
import math
import time
import random
import matplotlib.pyplot as plt
import numpy as np


x_tag = 0
y_tag = 0
# Selected demo
# 1 for air mouse circle
# 2 for air mouse pointing circle
selected_demo = 2
timeStart = 0 # Needed for pointing circle demo
data_available = threading.Event()
# Selected smoothing algorithm
# 1 for RAW
# 2 for SMA
# 3 for EMA
# 4 for AEMA
# 5 for AAEMA
selected_algorithm = 5

# Selected window size
selected_window_size = 7

# The screen offset can be provided as part of input parameter for the script, to adjust the middle of the point.
# If the antenna are 15cm above the screen the input parameter should be 15, if the antenna is below, the input should be -15
Screen_offset = 0

# COM Port where the UWB Receiver is connected & Baud rate
# It can be defined at execution time using COMX param
com_port = "COM4"
BAUD_RATE = 3000000
serial_port = serial.Serial()
#smoothed_point=Coordinate()
# Interpolation set to true to activate it
interpolation = False
num_interpolations = 10

# Alpha distance factor to adapt azimuth and elevation based on the distance
# The larger the distance, the higher the degree value to get to the edge of the screen
# Equation of alpha factor: a = md + c where
#   m is the slope
#   d is the distance to the screen 
#   c is the height at which the line crosses the y-axis
distance_factor = False     # Enable / Disable the distance factor
m_df = (1-1.4)/(300-50)     # Slope
c_df = 1 - (m_df*100)       # Height base

# Beta screen factor to adapt azimuth and elevation based on the screen size
# The larger the screen, the smaller the degree value to get to the edge of the screen
# Equation of screen factor: b = ms + c where
#   m is the slope
#   s is the screen size 
#   c is the height at which the line crosses the y-axis
screen_factor = False       # Enable / Disable the screen factor
m_sf = (1-0.8)/(22-15.4)    # Slope
c_sf = 1- (m_sf*22)         # Height base

# UWB Ranging session time interval
TIME_RANGING_INTERVAL = 0.050

#point = Coordinate()
point = 0

algorithm_seleccted = 0
prev_display_x = 0
prev_display_y = 0

# Get the monitor size in mm to calculate the size in inches for the screen_factor
screenwidth_mm = 0
screenheigth_mm = 0

# Variable to store previous state of button and having a debounce logic
prev_button_state = 0
monitor_selected = 0


default_screenwidth_mm =screenwidth_mm
default_screenheigth_mm =screenheigth_mm
# Screen size in inches
screen_inches = np.sqrt(np.square(screenwidth_mm) + np.square(screenheigth_mm)) // 25.4

# Create the main application window
root = tk.Tk()



screenwidth = root.winfo_screenwidth()
screenheight = root.winfo_screenheight()

# TKinter window
root.attributes('-fullscreen', False)
root.title("UWB Air Mouse PoC")
root.minsize(width=screenwidth, height=screenheight)

def on_closing_window():
    print("Close window")
    serial_port.close()
    root.destroy()
    sys.exit()

def show_about_message(event=None):
    messagebox.showinfo("UWB Air Mouse PoC", "UWB Air Mouse PoC v1.2")
    
def start_air_mouse():
    global selected_demo
    selected_demo = 1
    start_demo(1)    

def start_pointing_circle():
    global selected_demo
    selected_demo = 2
    start_demo(2)    

def update_sreen():
    global screen_inches, monitor_selected
    counter = 0
    found = 0
    # Each time we update the Monitor we select another monitor
    monitor_selected = monitor_selected+1
    for m in get_monitors():
        if monitor_selected == counter: 
            screenwidth_mm = m.width_mm
            screenheigth_mm = m.height_mm
            screen_inches = np.sqrt(np.square(screenwidth_mm) + np.square(screenheigth_mm)) // 25.4
            found = 1           
        counter = counter +1
    #No monitor found go back to first monitor config
    if found == 0:
        screen_inches = np.sqrt(np.square(default_screenwidth_mm) + np.square(default_screenheigth_mm)) // 25.4
        monitor_selected = 0
    messagebox.showinfo("monitor size selected", str(monitor_selected+1))

def enable_interpolation():
    global interpolation
    interpolation=True    

def disable_interpolation():
    global interpolation
    interpolation=False

def enable_distance_factor():
    global distance_factor
    distance_factor=True    

def disable_distance_factor():
    global distance_factor
    distance_factor=False

def enable_screen_factor():
    global screen_factor
    screen_factor=True    

def disable_screen_factor():
    global screen_factor
    screen_factor=False

# Add the menu
menubar = Menu(root)
root.config(menu=menubar)

# Settings menu
menusettings = Menu(menubar, tearoff=0)

# Demo selection submenu
submenudemo = Menu(menusettings, tearoff=0)
submenudemo.add_command(label='UWB Air Mouse', command=start_air_mouse)
submenudemo.add_command(label='UWB Pointing circle', command=start_pointing_circle)
menusettings.add_cascade(label="Demo", menu=submenudemo)

# Interpolation submenu
submenuinterpolation = Menu(menusettings, tearoff=0)
submenuinterpolation.add_command(label='Yes', command=enable_interpolation)
submenuinterpolation.add_command(label='No', command=disable_interpolation)
menusettings.add_cascade(label="Interpolation", menu=submenuinterpolation)

# Distance factor submenu
submenudistancefactor = Menu(menusettings, tearoff=0)
submenudistancefactor.add_command(label='Yes', command=enable_distance_factor)
submenudistancefactor.add_command(label='No', command=disable_distance_factor)
menusettings.add_cascade(label="Distance factor", menu=submenudistancefactor)

# Screen factor submenu
submenuscreenfactor = Menu(menusettings, tearoff=0)
submenuscreenfactor.add_command(label='Yes', command=enable_screen_factor)
submenuscreenfactor.add_command(label='No', command=disable_screen_factor)
menusettings.add_cascade(label="Screen factor", menu=submenuscreenfactor)

# About menu
menuabout = Menu(menubar, tearoff=0)
menuabout.add_command(label='About', command=show_about_message)
menuabout.add_command(label='Update screen', command=update_sreen)

# add the Settings menu to the menubar
menubar.add_cascade(label="Settings", menu=menusettings, underline=0)

# add the About menu to the menubar
menubar.add_cascade(label="Help", menu=menuabout, underline=0)

# Create a canvas for drawing the circles
canvas = tk.Canvas(root, bg="white")
canvas.pack(fill=tk.BOTH, expand=True)

# Close the demo when we close the window
root.protocol("WM_DELETE_WINDOW", lambda:on_closing_window())

# Air Mouse circle demo
circle = canvas.create_oval(40, 40, 80, 80, fill="green")  
pointing_circle = canvas.create_oval(40, 40, 80, 80, fill="red")  
label = canvas.create_text(10, 10, text='Try to keep the green circle inside the red circle for 2 seconds!', font=('Arial','18'), anchor=NW, justify=LEFT)
class SIGINThandler():
    def __init__(self):
        self.sigint = False
    
    def signal_handler(self, signal, frame):
        if keyboard.is_pressed('Esc'):
            print("You pressed ESC!")
            self.sigint = True
            sys.exit(0)

def draw_anchor():
        # 获取当前的坐标轴, gca = get current axis
        ax = plt.gca()
        # 设置标题，也可用plt.title()设置
        ax.set_title('DL-TdoA', fontsize=20, loc='left')
        # 设置右边框和上边框，隐藏
        ax.spines['right'].set_color('none')
        ax.spines['top'].set_color('none')
        # 设置x坐标轴为下边框
        ax.xaxis.set_ticks([-2,-1,0,1,2,3,4,5,6,7])
        # 设置y坐标轴为左边框
        ax.yaxis.set_ticks([-2,-1,0,1,2,3,4,5,6,7])
        
        plt.xlim((-1,7))
        plt.ylim((-1,7))
        
        x0 = 1.97
        y0 = 4.98
        plt.scatter([x0],[y0],s = 200,color='b')
        
        x1 = 0
        y1 = 0
        plt.scatter([x1],[y1],s = 200,color='b')
        
        x2 = 5.83
        y2 = 0
        plt.scatter([x2],[y2],s = 200,color='b')
        plt.scatter([float(x_tag)],[float(y_tag)], s = 100, color='r')

def read_from_serial_port(serial_port, point):
    global x_tag
    global y_tag
    print("Flush serial port")
    if serial_port.isOpen():
        serial_port.flushInput()

   
    every_time = time.strftime('%Y-%m-%d %H:%M:%S')# 时间戳
    data = ''
    print("Read from serial port started")
    while (serial_port.isOpen()):
        data = serial_port.readline()
        if (str(data).find("tag_position =") != -1):
            split_temp = str(data).split("(", 1)
            split_temp2 = str(split_temp[1]).split(")", 1)
            split_xy = str(split_temp2[0]).split(" ", 3)
            #print(split_xy[1]," ", split_xy[2])
            x_tag= split_xy[1]
            y_tag = split_xy[2]
            #print(x_tag, " ", y_tag)
        # print for debugging
        #print(ranging_data)

    
        #data_available.set() 
    else:
        print("Port is not opened")

    if serial_port.isOpen(): serial_port.close()
    print("Read from serial port exited")

def serial_port_configure(com_port, serial_port):
    serial_port.baudrate = BAUD_RATE
    serial_port.timeout = 1  # To avoid endless blocking read
    serial_port.port = com_port
    if serial_port.isOpen(): serial_port.close()
    try:
        serial_port.open()
    except:
        print("#=> Fail to open " + com_port)
        sys.exit(1)

def draw_pointing_circle():
    global timeStart, screenwidth, screenheight
    global pointing_circle

    # Target circle
    size = random.randint(50, 150)
    # Update the size of the screen each time you draw a Circle, so it updated
    screenwidth = root.winfo_screenwidth()
    screenheight = root.winfo_screenheight()
    pixelX = random.randint(round(size/2) + 50, screenwidth - round(size/2) - 100)
    pixelY = random.randint(round(size/2) + 40, screenheight - round(size/2) - 100)
    #print("winfo_screenwidth: ", root.winfo_screenwidth(),  "winfo_screenheight", root.winfo_screenheight() )
    #print("X: ",pixelX, "Y: ",pixelY )

    canvas.delete(pointing_circle)
    pointing_circle = canvas.create_oval(pixelX - size/2, pixelY - size/2, pixelX + size/2, pixelY + size/2, fill="red")
    canvas.tag_lower(pointing_circle)
    canvas.update()
    
    # Restart the timer
    timeStart = 0

def draw_pointing():
    global prev_display_x, prev_display_y, handler, Screen_offset, timeStart
    global smoothed_point
    if handler.sigint:
        sys.exit(1)

    # Check if a point can be draw
    if ((smoothed_point.dist != 0) & (smoothed_point.dist != 65535)):

        # Calculate coordinates
        x =  np.tan(math.radians(-smoothed_point.aziDest)) * smoothed_point.dist
        y =  np.tan(math.radians(smoothed_point.eleDest)) * smoothed_point.dist

        # Apply distance factor if enabled by the user
        if distance_factor == True:
            alpha = m_df * smoothed_point.dist + c_df

            x =  x * alpha
            y =  y * alpha
        
        # Apply screen factor if enabled by the user
        if screen_factor == True:
            beta = m_sf * screen_inches + c_sf
            
            x =  x * beta
            y =  y * beta

        # Adapt distance to points on the screen
        dpi = root.winfo_fpixels('1i')
        pixelsX = (dpi * x) // 2.54 + (screenwidth // 2)
        pixelsY = (dpi * y) // 2.54 + (screenheight // 2) 

        # Set the circle size
        circle_size = 20

        # Keep the circle within the canvas size
        if (pixelsX > canvas.winfo_width()):
             pixelsX = canvas.winfo_width()
        if (pixelsX < 0):
             pixelsX = 0
        if (pixelsY > canvas.winfo_height()):
             pixelsY = canvas.winfo_height()
        if (pixelsY < 0):
             pixelsY = 0

        
        # Draw intermediate positions
        if interpolation == True:
            # Calculate intermediate positions using linear interpolation
            dx = (pixelsX - prev_display_x) / num_interpolations
            dy = (pixelsY - prev_display_y) / num_interpolations
            for i in range(num_interpolations):
                display_x = prev_display_x + dx * i
                display_y = prev_display_y + dy * i

                try:
                    # Draw the circle centered at (display_x, display_y)
                    canvas.coords(circle, display_x - circle_size/2, display_y - circle_size/2, display_x + circle_size/2, display_y + circle_size/2)
                    canvas.update()
                except:
                    print("Cannot find circle element")

                # Add a small delay between drawing the intermediate points
                time.sleep(TIME_RANGING_INTERVAL/num_interpolations)  # You can adjust this value for smoother or faster motion                

            # Update the previous position to the next position for the next iteration
            prev_display_x = pixelsX
            prev_display_y = pixelsY

        else:
            try:
                canvas.coords(circle, pixelsX - circle_size/2, pixelsY - circle_size/2, pixelsX + circle_size/2, pixelsY + circle_size/2)
                canvas.update()
            except:
                print("Cannot find circle element")
            
        # Check overlap
        try:
            pos = canvas.coords(pointing_circle)
            if pos[0] < pixelsX and pos[1] < pixelsY and pos[2] > pixelsX and pos[3] > pixelsY:
                if timeStart == 0:
                    timeStart = time.time()
            else:
                timeStart = 0

            timeEnd = time.time()     
            if timeStart != 0 and timeStart + 2.0 < timeEnd:            
                draw_pointing_circle()
        except:
            print("Cannot find pointing_circle element")


def mouse_demo():
    global smoothed_point, screenwidth_mm 
    global data_available, screenheigth_mm
    global prev_button_state, screen_inches
    data_available.wait()
    if (prev_button_state != smoothed_point.button):
            prev_button_state = smoothed_point.button
            if smoothed_point.button:
                mouse.click('left')

    if ((smoothed_point.dist != 0) & (smoothed_point.dist != 65535) ):

        # Calculate coordinates
        x =  np.tan(math.radians(-smoothed_point.aziDest)) * smoothed_point.dist
        y =  np.tan(math.radians(smoothed_point.eleDest)) * smoothed_point.dist

        # Apply distance factor if enabled by the user
        if distance_factor == True:
            alpha = m_df * smoothed_point.dist + c_df

            x =  x * alpha
            y =  y * alpha
        
        # Apply screen factor if enabled by the user
        if screen_factor == True:
            beta = m_sf * screen_inches + c_sf
            
            x =  x * beta
            y =  y * beta

        # Adapt distance to points on the screen
        dpi = root.winfo_fpixels('1i')
        pixelsX = (dpi * x) // 2.54 + (screenwidth // 2)
        pixelsY = (dpi * y) // 2.54 + (screenheight // 2)        
        # Move the Windows mouse
        if selected_demo == 5 & smoothed_point.move == 1:
            mouse.move(pixelsX, pixelsY, absolute=True, duration=TIME_RANGING_INTERVAL)
        elif selected_demo != 5:
            # Carefull with this case the mouse will alwys be updated which can unconvenient to stop the program
            mouse.move(pixelsX, pixelsY, absolute=True, duration=TIME_RANGING_INTERVAL)
        data_available.clear()
        
def draw_circle():
    global prev_display_x, prev_display_y, handler, Screen_offset
    if handler.sigint:
        sys.exit(1)

    # Check if a point can be draw
    if ((smoothed_point.dist != 0) & (smoothed_point.dist != 65535)):
        
        # Calculate coordinates
        x =  np.tan(math.radians(-smoothed_point.aziDest)) * smoothed_point.dist
        y =  np.tan(math.radians(smoothed_point.eleDest)) * smoothed_point.dist

        # Apply distance factor if enabled by the user
        if distance_factor == True:
            alpha = m_df * smoothed_point.dist + c_df

            x =  x * alpha
            y =  y * alpha
        
        # Apply screen factor if enabled by the user
        if screen_factor == True:
            beta = m_sf * screen_inches + c_sf
            
            x =  x * beta
            y =  y * beta

        # Adapt distance to points on the screen
        dpi = root.winfo_fpixels('1i')
        pixelsX = (dpi * x) // 2.54 + (screenwidth // 2)
        pixelsY = (dpi * y) // 2.54 + (screenheight // 2) 

        # Change the size of the dot according to the distance
        circle_size = max(150 - int(smoothed_point.dist)/2, 20) 

        # Keep the circle within the canvas size
        if (pixelsX > canvas.winfo_width()):
             pixelsX = canvas.winfo_width()
        if (pixelsX < 0):
             pixelsX = 0
        if (pixelsY > canvas.winfo_height()):
             pixelsY = canvas.winfo_height()
        if (pixelsY < 0):
             pixelsY = 0

        # Draw intermediate positions
        if interpolation == True:
            # Calculate intermediate positions using linear interpolation
            dx = (pixelsX - prev_display_x) / num_interpolations
            dy = (pixelsY - prev_display_y) / num_interpolations
            for i in range(num_interpolations):
                display_x = prev_display_x + dx * i
                display_y = prev_display_y + dy * i

                try:
                    # Draw the circle centered at (display_x, display_y)
                    canvas.coords(circle, display_x - circle_size/2, display_y - circle_size/2, display_x + circle_size/2, display_y + circle_size/2)
                    canvas.update()
                except:
                    print("Cannot find circle element")

                # Add a small delay between drawing the intermediate points
                time.sleep(TIME_RANGING_INTERVAL/num_interpolations)  # You can adjust this value for smoother or faster motion

            # Update the previous position to the next position for the next iteration
            prev_display_x = pixelsX
            prev_display_y = pixelsY
        else:
            try:
                canvas.coords(circle, pixelsX - circle_size/2, pixelsY - circle_size/2, pixelsX + circle_size/2, pixelsY + circle_size/2)
                canvas.update()
            except:
                print("Cannot find circle element")

def start_processing(serial_port):
    read_thread = threading.Thread(target=read_from_serial_port, args=(serial_port, point))
    read_thread.start()
    while (read_thread.is_alive()):
        #print("running")
        #time.sleep(5)
        plt.clf()
        draw_anchor()
        plt.pause(0.1)
        plt.ioff()  

handler = SIGINThandler()
signal.signal(signal.SIGINT, handler.signal_handler)


def start_demo(demo):
    if demo == 1:  
        #draw_anchor()
        plt.ion() 
        print("demo start")
    else:
        print("Invalid demo selected. Select 1 for air mouse circle demo or 2 for air mouse pointing circle demo")

def main():    
    global com_port
    global Screen_offset
    global serial_port
    
    global selected_demo
    global selected_algorithm
    global selected_window_size
    global interpolation
    global distance_factor
    global screen_factor

    for arg in sys.argv[1:]:
        if (arg.startswith("COM")):
            com_port = arg

    print("Start selected demo...")
    start_demo(1)
    print("Selected demo started...")

    #print("Configure selected smoothing algorithm...")
    #configure_algorithm(selected_algorithm, selected_window_size)
    #print("Smoothing algorithm configured...")

    print("Configure serial port...")
    serial_port_configure(com_port, serial_port)
    print("Serial port configured")
    
    print("Start processing...")
    start_processing(serial_port)
    print("Processing finished")
    
if __name__ == '__main__':
    main()