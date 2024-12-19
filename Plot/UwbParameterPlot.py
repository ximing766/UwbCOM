import seaborn as sns
import matplotlib.pyplot as plt
import time
from matplotlib.animation import FuncAnimation

class MultiPlotter:
    def __init__(self, data):
        self.data = data
        self.idx    = [row[0] for row in data]
        self.user   = [row[1] for row in data]
        self.Master = [row[3] for row in data]
        self.Slaver = [row[4] for row in data]
        self.Speed  = [row[6] for row in data]
        self.x      = [row[7] for row in data]
        self.y      = [row[8] for row in data]
        self.z      = [row[9] for row in data]
        
        self.palette = sns.color_palette("mako_r", len(set(self.user)))
    
    def update_data(self, data):
        self.data = data
        self.Master = [row[3] for row in data]
        self.Slaver = [row[4] for row in data]
        self.Speed  = [row[6] for row in data]
        self.x      = [row[7] for row in data]
        self.y      = [row[8] for row in data]
        self.z      = [row[9] for row in data]
        self.user   = [row[1] for row in data]
        self.idx    = [row[0] for row in data]

    
    def plot_speed(self):
        self.speed_fig = plt.figure(figsize=(8, 6))
        sns.set_style("darkgrid")
        sns.set_context("notebook", font_scale=1.0, rc={"lines.linewidth": 1.5})
        sns.lineplot(x=range(len(self.Speed)), y=self.Speed, hue=self.user, palette=self.palette, legend="full", style=self.user)
        plt.xlabel("Index")
        plt.ylabel("Speed")
        plt.legend(title="User")

        sns.set_style("darkgrid")
        sns.set_context("notebook", font_scale=1.0, rc={"lines.linewidth": 1.5})
        sns.displot(x=self.Speed, kde=True, hue=self.user,palette=self.palette, element="step", fill = True, common_norm=False, alpha=0.2, height=4, aspect=1.2)
        plt.xlabel("speed")
        plt.show()


    def plot_distance(self):
        self.distance_fig = plt.figure(figsize=(10, 8))
        sns.set_style("darkgrid")
        sns.set_context("notebook", font_scale=1.0, rc={"lines.linewidth": 1.5})

        plt.subplot(2, 1, 1)
        sns.lineplot(x=range(len(self.Master)), y=self.Master, hue=self.user, palette=self.palette, legend="full", style=self.user)
        plt.title("Master-Slaver")
        plt.ylabel("Master")
        plt.legend(title="User")

        plt.subplot(2, 1, 2)
        sns.lineplot(x=range(len(self.Slaver)), y=self.Slaver, hue=self.user, palette=self.palette, legend="full")
        plt.xlabel("Index")
        plt.ylabel("Slaver")
        plt.legend(title="User")

        # 调整子图间距
        # plt.tight_layout()
        # plt.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=0.9, wspace=0.4, hspace=0.6)
        plt.show()
    
    def plot_xyz(self, plot_z=True):
        self.xyz_fig = plt.figure(figsize=(10, 8))
        sns.set_style("darkgrid")
        sns.set_context("notebook", font_scale=1.0, rc={"lines.linewidth": 1.5})

        plt.subplot(2, 1, 1)
        sns.lineplot(x=range(len(self.x)), y=self.x, hue=self.user, palette=self.palette, legend="full", style=self.user)
        plt.title("X-Y")
        plt.ylabel("X")
        plt.legend(title="User")

        plt.subplot(2, 1, 2)
        sns.lineplot(x=range(len(self.y)), y=self.y, hue=self.user, palette=self.palette, legend="full", style= self.user)
        plt.xlabel("Index")
        plt.ylabel("Y")
        plt.legend(title="User")

        if plot_z:
            plt.figure(figsize=(8,6))
            sns.set_style("darkgrid")
            sns.set_context("notebook", font_scale=1.0, rc={"lines.linewidth": 1.5})
            sns.lineplot(x=range(len(self.z)), y=self.z, hue=self.user, palette=self.palette, legend="full")
            plt.xlabel("Index")
            plt.ylabel("Z")
            plt.legend(title="User")

            sns.set_style("darkgrid")
            sns.set_context("notebook", font_scale=1.0, rc={"lines.linewidth": 1.5})
            g = sns.displot(x=self.z, kde=True, hue=self.user, palette=self.palette, element="step", fill = True, common_norm=False, alpha=0.2, height=6, aspect=1.25)
            fig = g.fig
    
            fig.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9)
            plt.xlabel("Z")

        plt.show()


if __name__ == '__main__':
    data = [[0, 1, 1, 48, 42, 100, 0, 0, 0, -28], [1, 1, 1, 54, 52, 100, 0, 0, 0, -30], [2, 1, 1, 48, 34, 100, 0, 0, 0, -23], [3, 1, 1, 46, 35, 100, 0, 0, 0, -25], [4, 1, 1, 56, 38, 100, 0, 0, 0, -32], [5, 1, 1, 60, 41, 100, 0, 0, 0, -37], [6, 1, 1, 59, 43, 100, 0, 0, 0, -39], [7, 1, 1, 46, 38, 100, 0, 0, 0, -33], [8, 1, 1, 43, 36, 100, 0, 0, 0, -29], [9, 1, 1, 41, 38, 100, 0, 0, 0, -26], [10, 1, 1, 36, 35, 100, 0, 0, 0, -22], [11, 1, 1, 44, 32, 100, 0, 0, 0, -23], [12, 1, 1, 39, 35, 100, 0, 0, 0, -23], [13, 1, 1, 37, 41, 100, 0, 0, 0, -21], [14, 1, 1, 37, 40, 100, 0, 0, 0, -17], [15, 1, 1, 50, 42, 100, 0, 0, 0, -21], [16, 1, 1, 49, 41, 100, 0, 0, 0, -22], [17, 1, 1, 41, 46, 100, 0, 0, 0, -20], [18, 1, 1, 39, 40, 100, 0, 0, 0, -15], [19, 1, 1, 43, 39, 100, 0, 0, 0, -16], [20, 1, 1, 39, 41, 100, 0, 0, 0, -16], [21, 1, 1, 42, 45, 100, 0, 0, 0, -16], [22, 1, 1, 42, 45, 100, 0, 0, 0, -14], [23, 1, 1, 42, 43, 100, 0, 0, 0, -12], [24, 1, 1, 39, 39, 100, 0, 0, 0, -11], [25, 1, 1, 37, 44, 100, 0, 0, 0, -11], [31, 2, 1, 51, 38, 100, 0, 0, 0, -26], [32, 2, 1, 53, 41, 100, 0, 0, 0, -31], [26, 1, 1, 35, 40, 100, 0, 0, 0, -9], [27, 1, 1, 43, 43, 100, 0, 0, 0, -12], [28, 1, 1, 35, 44, 100, 0, 0, 0, -9], [29, 1, 1, 37, 44, 100, 0, 0, 0, -8], [30, 2, 0, 0, 37, 100, 0, 0, 0, 0], [33, 2, 1, 41, 39, 100, 0, 0, 0, -20], [34, 2, 1, 43, 38, 100, 0, 0, 0, -20], [35, 2, 1, 45, 36, 100, 0, 0, 0, -21], [36, 2, 1, 44, 35, 100, 0, 0, 0, -22], [37, 2, 1, 31, 38, 100, 0, 0, 0, -18], [38, 2, 1, 38, 44, 100, 0, 0, 0, -17], [39, 2, 1, 46, 46, 100, 0, 0, 0, -17], [40, 2, 1, 43, 46, 100, 0, 0, 0, -15], [41, 2, 1, 34, 40, 100, 0, 0, 0, -10], [42, 2, 1, 39, 40, 100, 0, 0, 0, -11], [43, 2, 1, 39, 43, 100, 0, 0, 0, -11], [44, 2, 1, 27, 45, 100, 0, 0, 0, -6], [45, 2, 1, 30, 39, 100, 0, 0, 0, -3], [46, 2, 1, 41, 38, 100, 0, 0, 0, -7], [47, 2, 1, 38, 37, 100, 0, 0, 0, -10], [48, 2, 1, 33, 38, 100, 0, 0, 0, -10], [49, 2, 1, 49, 30, 100, 0, 0, 0, -16], [50, 2, 1, 43, 34, 100, 0, 0, 0, -20], [51, 2, 1, 51, 30, 100, 0, 0, 0, -26], [52, 2, 1, 52, 31, 100, 0, 0, 0, -32], [53, 2, 1, 47, 33, 100, 0, 0, 0, -33], [54, 2, 1, 47, 43, 100, 0, 0, 0, -33], [55, 2, 1, 50, 41, 100, 0, 0, 0, -30], [56, 2, 1, 42, 44, 100, 0, 0, 0, -25], [57, 2, 1, 35, 45, 100, 0, 0, 0, -18], [58, 2, 1, 44, 48, 100, 0, 0, 0, -16]] 
    plotter = MultiPlotter(data)
    fig = plotter.plot_speed()
