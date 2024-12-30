import tkinter as tk
from tkinter import scrolledtext
import serial
import serial.tools.list_ports
import customtkinter
import ttkbootstrap as ttk

class SerialAssistant:
    def __init__(self, master):
        self.master = master
        self.master.title("UWB测量高度误差估计器")
        self.master.minsize(400, 350)
        self.master.geometry("400x350")
        
        self.create_widgets()
    
    def create_widgets(self):
        self.progress_frame = customtkinter.CTkFrame(self.master, height=100, fg_color= ("#E6F7FF"))
        self.progress_frame.pack(side="top", fill="x", padx=10, pady=10)
        
        self.progressbars = []
        self.progressbar_scales = [[20, 60], [50, 150], [50, 150], [0, 20], [0, 20]]
        self.progressbar_init_values = [30, 100, 100, 10, 10]
        self.labels = []
        self.label_names = ["Height  Diff ", "Max-D of M", "Max-D of S ", "Error of  M  ", "Error of  S  "]
        for i in range(5):
            container = customtkinter.CTkFrame(self.progress_frame, fg_color= ("#D3EAF9"))
            container.pack(side="top", padx=5, pady=5, fill="x")
            
            label = customtkinter.CTkLabel(container,width=50, text=f"{self.label_names[i]}: {self.progressbar_init_values[i]}", fg_color="transparent")
            label.pack(side="left", padx=5)
            self.labels.append(label)
            
            progressbar = customtkinter.CTkSlider(container, from_=self.progressbar_scales[i][0], to=self.progressbar_scales[i][1],command=lambda val, idx=i: self.update_label(val, idx))
            progressbar.set(self.progressbar_init_values[i])
            progressbar.pack(side="right", padx=5, fill="x", expand=True)
            self.progressbars.append(progressbar)
        
        self.control_frame = customtkinter.CTkFrame(self.master, height=100, fg_color= ("#E6F7FF"))
        self.control_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        self.output = customtkinter.CTkEntry(self.control_frame, width=80, height=10, fg_color= ("#D3EAF9"), font=("Roboto", 15))
        self.output.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        self.confirm_button = customtkinter.CTkButton(self.control_frame, text="Confirm", width=40, command=self.show_ZEE, fg_color= ("#A0C8CF"),  font=("Roboto", 15))
        self.confirm_button.pack(side="left", fill="y", padx=10, pady=10)

    def update_label(self, value, idx):
        percentage = f"{int(value)}"
        self.labels[idx].configure(text=f"{self.label_names[idx]}: {percentage}")

    def calculate_ez(self, h, b, c, eb, ec):
        return (b * eb - c * ec) / h
        # result = np.sqrt(((b * eb) / h)**2 + ((c * ec) / h)**2)
    
    def show_ZEE(self):
        h = self.progressbars[0].get()
        b = self.progressbars[1].get()
        c = self.progressbars[2].get()
        eb_values = range(0,int(self.progressbars[3].get())+1)
        ec_values = range(0,int(self.progressbars[4].get())+1)
        ez = [self.calculate_ez(h, b, c, eb, ec) for eb in eb_values for ec in ec_values]
        
        self.output.delete(0, "end")
        self.output.insert(tk.END, f"测量高度理论误差参考:[ {min(ez):.1f}, {max(ez):.1f}]\n")


customtkinter.set_appearance_mode("light")  # Modes: System (default), light, dark
customtkinter.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"
root = customtkinter.CTk()
app = SerialAssistant(root)
root.mainloop()