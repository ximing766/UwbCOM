import matplotlib.pyplot as plt

class CoordinatePlotter:
    def __init__(self, coord1, coord2, coord3):
        self.coord1 = coord1
        self.coord2 = coord2
        self.coord3 = coord3
        self.fig, self.ax = plt.subplots()
        self.ax.set_xlim(-5, 15)
        self.ax.set_ylim(-5, 15)
        self.ax.grid(True, linestyle='--', alpha=0.25)
        self.colors = ['red', 'purple', 'purple']  # 确保有足够的颜色
        self.markers = ['o', 'o', 'o']
        self.labels = ['Master', 'Slave 1', 'Slave 2']
        self.scatters = []

    def plot_coordinates(self):
        for i, (coord, color, marker, label) in enumerate(zip([self.coord1, self.coord2, self.coord3], self.colors, self.markers, self.labels)):
            scatter = self.ax.scatter(coord[0], coord[1], color=color, label=label, marker=marker, s=150)
            self.scatters.append(scatter)

        # self.ax.set_facecolor('lightskyblue')
        self.ax.set_title('Tag Coordinate Plot',fontsize=20, color='black')
        self.ax.set_xlabel('X Coordinate')
        self.ax.set_ylabel('Y Coordinate')
        self.ax.margins(0.2, 0.2)
        self.ax.legend()

    def update_point(self, index, new_coord):
        if not self.ax:
            print("Axes object not found.")
            return 
        
        if 1 <= index <= len(self.scatters):
            # 更新坐标点
            self.scatters[index - 1].set_offsets([new_coord[0], new_coord[1]])
            self.ax.set_xlim(min(-5, new_coord[0] - 5), max(15, new_coord[0] + 5))
            self.ax.set_ylim(min(-5, new_coord[1] - 5), max(15, new_coord[1] + 5))
            # 更新坐标数据
            if index == 1:
                self.coord1 = new_coord
            elif index == 2:
                self.coord2 = new_coord
            elif index == 3:
                self.coord3 = new_coord
        else:
            print("Index out of range.")

        # 重新绘制图形
        self.ax.figure.canvas.draw()
        plt.pause(0.01)  # 暂停0.01秒，以便更新图像

    def add_new_point(self, new_coord, color, marker, label):
        # 创建新的散点图对象
        new_scatter = self.ax.scatter(new_coord[0], new_coord[1], color=color, label=label, marker=marker, s=150)
        self.scatters.append(new_scatter)
        self.labels.append(label)  # 更新标签列表
        self.colors.append(color)  # 更新颜色列表
        self.markers.append(marker)  # 更新标记列表

        # 更新图例
        self.ax.legend()
        self.ax.figure.canvas.draw()
        plt.pause(0.01)  # 暂停0.01秒，以便更新图像

if __name__ == '__main__':
    # 示例坐标点
    coord1 = [1, 2]
    coord2 = [4, 5]
    coord3 = [7, 8]

    # 创建类实例并绘制坐标点
    plotter = CoordinatePlotter(coord1, coord2, coord3)
    plotter.plot_coordinates()

    # 添加一个新的点
    plotter.add_new_point([0, 0], 'black', 'D', 'Tag')
    for i in range(100):
        plotter.update_point(4, [i, i])

    plt.show()  # 在所有点添加完毕后显示图像

