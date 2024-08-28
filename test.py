import tkinter as tk

def on_configure(event):
    canvas.config(scrollregion=canvas.bbox("all"))

root = tk.Tk()
root.geometry("800x600")

canvas = tk.Canvas(root, width=800, height=600)
canvas.pack()

# 创建一个立方体
points = [100, 100, 100, 200, 200, 200, 200, 100]
cube = canvas.create_polygon(points, fill="blue", outline="black")

canvas.create_text(400, 300, text="Hello, World!", font=("Arial", 24), fill="white")

canvas.bind("<Configure>", on_configure)

root.mainloop()
