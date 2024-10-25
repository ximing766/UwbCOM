import tkinter as tk

class OvalMover:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=400, height=400, bg='white')
        self.canvas.pack()
        self.oval = self.canvas.create_rectangle(50, 50, 100, 100, fill='blue', outline='blue')
        self.max_moves = 600
        self.move_times = 0
        self.start_x, self.start_y = 50, 50
        self.end_x, self.end_y = 300, 300
        self.move_oval(self.canvas, self.oval, self.start_x, self.start_y, self.end_x, self.end_y)

    def move_oval(self, canvas, oval, start_x, start_y, end_x, end_y, step=1):
        x_move = (end_x - start_x) / self.max_moves
        y_move = (end_y - start_y) / self.max_moves

        canvas.move(oval, x_move, y_move)
        self.move_times += 1

        if self.move_times < self.max_moves:
            canvas.after(10, self.move_oval, canvas, oval, start_x + x_move, start_y + y_move, end_x, end_y, step)
        else:
            self.move_times = 0
            canvas.coords(oval, end_x - 5, end_y - 5, end_x + 5, end_y + 5)

root = tk.Tk()
app = OvalMover(root)
root.mainloop()