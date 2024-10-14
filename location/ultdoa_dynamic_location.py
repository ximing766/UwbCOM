import matplotlib.pyplot as plt

class CoordinatePlotter:
    def __init__(self, coord1, coord2, coord3):
        self.coord1 = coord1
        self.coord2 = coord2
        self.coord3 = coord3

    def plot_coordinates(self):
        # 解包坐标点
        x1, y1 = self.coord1
        x2, y2 = self.coord2
        x3, y3 = self.coord3

        # 创建图形和轴
        fig, ax = plt.subplots()
        ax.set_xlim(-3, 13)
        ax.set_ylim(-3, 10)
        ax.grid(True, linestyle='--', alpha=0.25)

        # 绘制坐标点
        ax.scatter(x1, y1, color='red', label='Master Coordinate',marker ='o', s = 250)
        ax.scatter(x2, y2, color='blue', label='Slave Coordinate 1',marker='s', s = 100)
        ax.scatter(x3, y3, color='green', label='Slave Coordinate 2',marker='s', s = 100)

        # 设置图例
        ax.legend()

        # 设置坐标轴标签
        ax.set_xlabel('X Coordinate')
        ax.set_ylabel('Y Coordinate')

        # 显示图形
        plt.show()

if __name__ == '__main__':
    # 示例坐标点
    coord1 = [1, 2]
    coord2 = [4, 5]
    coord3 = [7, 8]

    # 创建类实例并绘制坐标点
    plotter = CoordinatePlotter(coord1, coord2, coord3)
    plotter.plot_coordinates()