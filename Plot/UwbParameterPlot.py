import seaborn as sns
import matplotlib.pyplot as plt

class MultiPlotter:
    def __init__(self, data):
        self.data = data
        self.Master = [row[3] for row in data]
        self.Slaver = [row[4] for row in data]
        self.Speed  = [row[6] for row in data]
        self.x      = [row[7] for row in data]
        self.y      = [row[8] for row in data]
        self.z      = [row[9] for row in data]
        self.user   = [row[1] for row in data]
        self.palette = sns.color_palette("husl", len(set(self.user)))
        self.speed_fig = None
        self.distance_fig = None
        self.position_fig = None
    
    def plot_speed(self):
        self.speed_fig = plt.figure(figsize=(8, 6))
        sns.set_style("whitegrid")
        sns.set_context("notebook", font_scale=1.0, rc={"lines.linewidth": 1.5})

        sns.lineplot(x=range(len(self.Speed)), y=self.Speed, hue=self.user, palette=self.palette, legend="full", marker="o")
        plt.title("Speed")
        plt.xlabel("Index")
        plt.ylabel("Speed")
        plt.legend(title="User")
        plt.show()

    def plot_distance(self):
        self.distance_fig = plt.figure(figsize=(8, 8))
        sns.set_style("whitegrid")
        sns.set_context("notebook", font_scale=1.0, rc={"lines.linewidth": 1.5})

        plt.subplot(2, 1, 1)
        sns.lineplot(x=range(len(self.Master)), y=self.Master, hue=self.user, palette=self.palette, legend="full", marker="o")
        plt.title("Master")
        plt.xlabel("Index")
        plt.ylabel("Master")
        plt.legend(title="User")

        plt.subplot(2, 1, 2)
        sns.lineplot(x=range(len(self.Slaver)), y=self.Slaver, hue=self.user, palette=self.palette, legend="full", marker="o")
        plt.title("Slaver")
        plt.xlabel("Index")
        plt.ylabel("Slaver")
        plt.legend(title="User")

        # 调整子图间距
        plt.tight_layout()
        plt.show()
    
    def plot_xyz(self):
        self.xyz_fig = plt.figure(figsize=(8, 10))
        sns.set_style("whitegrid")
        sns.set_context("notebook", font_scale=1.0, rc={"lines.linewidth": 1.5})

        plt.subplot(3, 1, 1)
        sns.lineplot(x=range(len(self.x)), y=self.x, hue=self.user, palette=self.palette, legend="full", marker="o")
        plt.title("X")
        plt.xlabel("Index")
        plt.ylabel("X")
        plt.legend(title="User")

        plt.subplot(3, 1, 2)
        sns.lineplot(x=range(len(self.y)), y=self.y, hue=self.user, palette=self.palette, legend="full", marker="o")
        plt.title("Y")
        plt.xlabel("Index")
        plt.ylabel("Y")
        plt.legend(title="User")

        plt.subplot(3, 1, 3)
        sns.lineplot(x=range(len(self.z)), y=self.z, hue=self.user, palette=self.palette, legend="full", marker="o")
        plt.title("Z")
        plt.xlabel("Index")
        plt.ylabel("Z")
        plt.legend(title="User")

        plt.tight_layout()
        plt.show()
    
    def close_plt(self, fig):
            plt.close(fig)


# data = [...]  
# plotter = MultiPlotter(data)
# plotter.plot()