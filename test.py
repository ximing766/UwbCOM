import tkinter as tk
from tkinter import messagebox

# 设置窗口的函数
def open_settings():
    settings_window = tk.Toplevel()  # 创建新的Toplevel窗口
    settings_window.title("Settings")

    # 在设置窗口中添加一些设置选项
    tk.Label(settings_window, text="COM Port:").grid(row=0, column=0)
    com_port_var = tk.StringVar()
    com_port_var.set("COM1")  # 默认值
    tk.Entry(settings_window, textvariable=com_port_var).grid(row=0, column=1)

    tk.Label(settings_window, text="Baud Rate:").grid(row=1, column=0)
    baud_rate_var = tk.IntVar()
    baud_rate_var.set(9600)  # 默认值
    tk.Entry(settings_window, textvariable=baud_rate_var).grid(row=1, column=1)

    # 添加一个保存按钮，用于保存设置
    def save_settings():
        # 这里可以添加保存设置的代码
        messagebox.showinfo("Settings Saved", f"COM Port: {com_port_var.get()}, Baud Rate: {baud_rate_var.get()}")
        settings_window.destroy()  # 关闭设置窗口

    tk.Button(settings_window, text="Save", command=save_settings).grid(row=2, column=0, columnspan=2)

# 主窗口
root = tk.Tk()
root.title("Main Window")

# 添加一个按钮，用于打开设置窗口
settings_button = tk.Button(root, text="Settings", command=open_settings)
settings_button.pack()

root.mainloop()