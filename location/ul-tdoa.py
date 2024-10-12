import serial
import threading
import queue
import tkinter as tk

# 定义一个函数来更新UI
def update_ui():
    try:
        # 从队列中获取数据，并更新到Tkinter界面上
        data_com1 = queue_com1.get_nowait()
        data_com2 = queue_com2.get_nowait()
        
        text_com1.delete('1.0', tk.END)
        text_com1.insert(tk.END, data_com1)
        
        text_com2.delete('1.0', tk.END)
        text_com2.insert(tk.END, data_com2)
    except queue.Empty:
        pass
    # 每100毫秒调用一次update_ui来更新UI
    root.after(100, update_ui)

# 定义一个函数来处理每个COM口的数据接收
def read_data(port, baudrate, queue):
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

# 创建Tkinter窗口
root = tk.Tk()
root.title("Multi-COM Port Data Receiver")

# 创建队列来存储从各个COM口接收到的数据
queue_com1 = queue.Queue()
queue_com2 = queue.Queue()

# 创建Text控件来显示COM口的数据
text_com1 = tk.Text(root, height=10, width=40)
text_com1.pack()
text_com2 = tk.Text(root, height=10, width=40)
text_com2.pack()

# 启动数据接收的线程
thread_com1 = threading.Thread(target=read_data, args=('COM1', 9600, queue_com1))
thread_com2 = threading.Thread(target=read_data, args=('COM2', 9600, queue_com2))

thread_com1.daemon = True  # 设置为守护线程
thread_com2.daemon = True  # 设置为守护线程

thread_com1.start()
thread_com2.start()

# 启动UI更新
update_ui()

root.mainloop()