import pandas as pd
from tkinter import filedialog
import customtkinter as ctk

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Pandas CSV Reader")
        self.geometry("600x400")

        # 创建主框架
        self.home_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.home_frame.pack(fill="both", expand=True)

        # 创建文件框架
        self.file_frame = ctk.CTkFrame(self.home_frame, corner_radius=0, fg_color="transparent")
        self.file_frame.grid(row=0, column=0, padx=10, pady=10)

        # 创建文件路径显示框
        self.file_path_entry = ctk.CTkEntry(self.file_frame, placeholder_text="Select a CSV file")
        self.file_path_entry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # 创建文件选择按钮
        self.select_file_button = ctk.CTkButton(self.file_frame, text="Select CSV File", command=self.select_file)
        self.select_file_button.grid(row=0, column=1, padx=10, pady=10)

        # 创建用于显示文件内容的文本框
        self.content_textbox = ctk.CTkTextbox(self.home_frame, wrap="word")
        self.content_textbox.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.home_frame.grid_rowconfigure(1, weight=1)  # 让文本框可以垂直扩展

        # 创建用于输入列名的文本框
        self.columns_entry = ctk.CTkEntry(self.file_frame, placeholder_text="Enter column names (comma-separated)")
        self.columns_entry.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # 创建读取特定列的按钮
        self.read_columns_button = ctk.CTkButton(self.file_frame, text="Read Specific Columns", command=self.read_columns)
        self.read_columns_button.grid(row=1, column=1, padx=10, pady=10)

    def select_file(self):
        # 打开文件选择对话框
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.file_path_entry.delete(0, ctk.END)  # 清空文本框
            self.file_path_entry.insert(0, file_path)  # 显示文件路径

    def read_columns(self):
        file_path = self.file_path_entry.get()  # 获取文件路径
        columns = self.columns_entry.get()  # 获取用户输入的列名
        if not file_path:
            self.content_textbox.delete("1.0", ctk.END)
            self.content_textbox.insert("1.0", "Please select a CSV file first.")
            return
        if not columns:
            self.content_textbox.delete("1.0", ctk.END)
            self.content_textbox.insert("1.0", "Please enter column names.")
            return

        # 将列名字符串转换为列表
        columns = [col.strip() for col in columns.split(",")]

        try:
            # 使用pandas读取CSV文件，并指定列名
            df = pd.read_csv(file_path, usecols=columns)
            self.content_textbox.delete("1.0", ctk.END)
            self.content_textbox.insert("1.0", df.to_string(index=False))  # 显示数据框内容
        except Exception as e:
            self.content_textbox.delete("1.0", ctk.END)
            self.content_textbox.insert("1.0", f"Error reading file: {e}")

if __name__ == "__main__":
    app = App()
    app.mainloop()