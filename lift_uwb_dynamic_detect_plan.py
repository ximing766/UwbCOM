import numpy as np
import matplotlib.pyplot as plt
from matplotlib import patches, animation
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from shapely.geometry import Polygon, LineString, Point
from matplotlib.widgets import Slider,Button
import math

class UWBLiftAnimationPlan1:
    def __init__(self,radius=2.0,lift_deep=2.0,lift_height=3.0):
        self.theta = np.linspace((np.pi*3/2), 2 * np.pi , 100)  #弧度数据
        self.radius = radius # uwb有效区半径，初始值为电梯深度
        self.lift_deep = lift_deep  # 电梯深度
        self.lift_height = lift_height  # 电梯高度,有效半径最大值
        self.min_sum = float('inf')
        self.min_sum_intersections = []
        self.paused = False
        self.slider_change = False

        # 创建图表
        self.fig, self.ax = plt.subplots(subplot_kw={'aspect': 'equal'}, figsize=(6, 6))
        self.fig.suptitle('UWB Lift Dynamic Detection', fontsize=16)
        self.ax.set_xlim(-3, self.lift_deep +3)
        self.ax.set_ylim(-0.5, self.lift_height + 3)
        self.ax.grid(True, linestyle='--', alpha=0.7)

        self.line, = self.ax.plot(self.radius * np.cos(self.theta), self.lift_height + self.radius * np.sin(self.theta), 'pink')
        self.line1, = self.ax.plot([0, self.radius * np.cos(self.theta[-1])], [self.lift_height, self.lift_height + self.radius * np.sin(self.theta[-1])], 'r--')
        self.line2, = self.ax.plot([0, self.radius * np.cos(self.theta[0])], [self.lift_height, self.lift_height + self.radius * np.sin(self.theta[0])], 'r--')

        # 添加矩形
        rect = patches.Rectangle((0, 0), self.lift_deep, self.lift_height, linewidth=1, edgecolor='b', facecolor='grey', alpha=0.2)
        self.ax.add_patch(rect)

        # 创建不重叠区域的路径
        vertices = np.vstack((np.column_stack((self.radius * np.cos(self.theta), self.lift_height + self.radius * np.sin(self.theta))),
                              np.column_stack((self.radius * np.cos(self.theta[::-1]), self.lift_height + self.radius * np.sin(self.theta[::-1])))))
        codes = [Path.MOVETO] + [Path.LINETO] * (len(self.theta) - 1) + [Path.MOVETO] + [Path.LINETO] * (len(self.theta) - 1)
        path = Path(vertices, codes)
        self.patch = PathPatch(path, facecolor='pink', edgecolor='none', alpha=0.5)
        self.ax.add_patch(self.patch)

        # 创建重叠区域的补丁
        initial_path = Path(np.array([[0, 0], [1, 1]]))  # 初始路径，避免空数组
        self.overlap_patch = PathPatch(initial_path, facecolor='b', edgecolor='none', alpha=0.5)
        self.ax.add_patch(self.overlap_patch)

        # 添加文本对象
        self.non_overlap_text = self.ax.text(0.05, 0.95, '', transform=self.ax.transAxes, fontsize=12, verticalalignment='top', color='black')
        self.overlap_text = self.ax.text(0.05, 0.90, '', transform=self.ax.transAxes, fontsize=12, verticalalignment='top', color='black')
        self.min_sum_text = self.ax.text(0.05, 0.85, '', transform=self.ax.transAxes, fontsize=12, verticalalignment='top', color='black')
        self.min_sum_intersections_text = self.ax.text(0.05, 0.80, '', transform=self.ax.transAxes, fontsize=12, verticalalignment='top')
        self.golden_point_text = self.ax.text(0.05, 0.75, '', transform=self.ax.transAxes, fontsize=12, verticalalignment='top')

        # 添加标题
        self.ax.set_title('UWB lift dynamic graphy plan1')
        self.ax.set_xlabel('lift deep(m)')
        self.ax.set_ylabel('lift height(m)')

        # 添加滑块
        self.slider_ax = self.fig.add_axes([0.25, 0.01, 0.35, 0.03], facecolor='lightgoldenrodyellow')
        self.radius_slider = Slider(self.slider_ax, 'Radius', 1.0, self.lift_height + 2, valinit=self.radius)
        self.radius_slider.on_changed(self.RadiusSliderChanged)

        # 添加按钮
        self.button_ax = self.fig.add_axes([0.8, 0.01, 0.1, 0.03])
        self.pause_button = Button(self.button_ax, 'Pause')
        self.pause_button.on_clicked(self.toggle_pause_button)

    def golden_ratio_point(self,A, B):
        phi = (1 + 5 ** 0.5) / 2  # φ ≈ 1.618
        x1, y1 = A
        x2, y2 = B
        # 计算线段 AB 的长度
        L = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        # 计算较长部分 AC 的长度
        AC = L / (1 + 1 / phi)
        # 点 C 的坐标
        Cx = round(x1 + (x2 - x1) * (AC / L),2)
        Cy = round(y1 + (y2 - y1) * (AC / L),2)
        Cr = round(math.sqrt((Cx)**2 + (self.lift_height - Cy)**2),2)
        return (Cx, Cy, Cr)
    
    def toggle_pause_button(self, event):
        self.paused = not self.paused
        if self.paused:
            self.pause_button.label.set_text('Resume')
        else:
            self.pause_button.label.set_text('Pause')

    # 滑动滑块回调函数，清除状态，更新半径
    def RadiusSliderChanged(self, val):
        self.radius = val
        self.slider_change = True
        self.min_sum = float('inf')
        self.update(0)

    def update(self, num):  #num由系统给，为帧编号，每次加1
        if self.paused and self.slider_change == False:
            return self.line, self.line1, self.line2, self.patch, self.overlap_patch, self.non_overlap_text, self.overlap_text, self.min_sum_text, self.min_sum_intersections_text
        self.slider_change = False
        r = self.radius + num / 100.0  # 更新半径
        x_data = r * np.cos(self.theta)
        y_data = self.lift_height + r * np.sin(self.theta)
        self.line.set_data(x_data, y_data)
        self.line1.set_data([0, x_data[-1]], [self.lift_height, y_data[-1]])
        self.line2.set_data([0, x_data[0]], [self.lift_height, y_data[0]])

        # 计算重叠区域
        line_coords = np.column_stack((self.line.get_xdata(), self.line.get_ydata()))
        line1_coords = np.column_stack((self.line1.get_xdata(), self.line1.get_ydata()))
        line2_coords = np.column_stack((self.line2.get_xdata(), self.line2.get_ydata()))
        all_coords = np.vstack((line_coords, line1_coords, line2_coords))
        polygon1 = Polygon(all_coords)
        polygon2 = Polygon([(0, 0), (self.lift_deep, 0), (self.lift_deep, self.lift_height), (0, self.lift_height)])
        overlap = polygon1.intersection(polygon2)
        non_overlap = polygon1.difference(polygon2)

        # 绘制不重叠区域
        if non_overlap.is_empty:
            self.patch.set_visible(False)
        else:
            self.patch.set_visible(True)
            if isinstance(non_overlap, Polygon):
                coords = np.array(non_overlap.exterior.coords)
            else:  # MultiPolygon
                coords = np.concatenate([np.array(p.exterior.coords) for p in non_overlap.geoms])
            self.patch.set_path(Path(coords))

        # 绘制重叠区域
        if overlap.is_empty:
            self.overlap_patch.set_visible(False)
        else:
            self.overlap_patch.set_visible(True)
            if isinstance(overlap, Polygon):
                coords = np.array(overlap.exterior.coords)
            else:  # MultiPolygon
                coords = np.concatenate([np.array(p.exterior.coords) for p in overlap.geoms])
            self.overlap_patch.set_path(Path(coords))

        # 更新文本内容
        ErrorArea = non_overlap.area
        self.non_overlap_text.set_text(f'Error detection Area(pink area):  {ErrorArea:.2f}')
        MissArea = self.lift_deep * self.lift_height - overlap.area
        self.overlap_text.set_text(f'Miss out Area(grey area):            {MissArea:.2f}')

        # 计算和并更新最小和
        current_sum = ErrorArea + MissArea
        if current_sum < self.min_sum:
            self.min_sum = current_sum
            line_string = LineString(line_coords)
            rect_polygon = Polygon([(0, 0), (self.lift_deep, 0), (self.lift_deep, self.lift_height), (0, self.lift_height)])
            intersections = line_string.intersection(rect_polygon)
            right_edge = LineString([(self.lift_deep, 0), (self.lift_deep, self.lift_height)])
            right_edge_intersections = line_string.intersection(right_edge)
            if right_edge_intersections.is_empty:
                self.min_sum_intersections = []
            elif isinstance(right_edge_intersections, Point):
                self.min_sum_intersections = [right_edge_intersections.coords[:]]
            elif isinstance(right_edge_intersections, LineString):
                self.min_sum_intersections = [right_edge_intersections.coords[:]]
            else:  # MultiLineString
                self.min_sum_intersections = [line.coords[:] for line in right_edge_intersections]

        # 格式化 min_sum_intersections 中的值，最多显示两位小数
        formatted_intersections = [
            [[round(x, 2), round(y, 2)] for x, y in intersection]
            for intersection in self.min_sum_intersections
        ]
        if formatted_intersections and len(formatted_intersections) > 0 and len(formatted_intersections[0]) > 0 and len(formatted_intersections[0][0]) > 0:
            if(self.lift_height > formatted_intersections[0][0][1]):
                minimum_r = float(math.sqrt(formatted_intersections[0][0][0]**2 + ((self.lift_height-formatted_intersections[0][0][1])**2)))
                formatted_intersections[0][0].append(round(minimum_r,2))

        # 将 formatted_intersections 转换为字符串并去掉中括号
        formatted_intersections_str = str(formatted_intersections).replace('[', '').replace(']', '') 
        self.min_sum_text.set_text(f'E+M minimum value:                  {self.min_sum:.2f}')
        
        self.min_sum_intersections_text.set_text(f'E+M minimum intersection:       ({formatted_intersections_str})')
        self.golden_point_text.set_text(f'φ point:                      {self.golden_ratio_point( [self.lift_deep, self.lift_height],[self.lift_deep, 0])}')
        return self.line, self.line1, self.line2, self.patch, self.overlap_patch, self.non_overlap_text, self.overlap_text, self.min_sum_text, self.min_sum_intersections_text

    def start_animation(self):
        self.ani = animation.FuncAnimation(self.fig, self.update, frames=100, interval=50, blit=True)
        self.fig.canvas.manager.set_window_title('UWB Lift plan')  # 设置窗口标题('UWB Lift plan')
        plt.show()





class UWBLiftAnimationPlan2:
    def __init__(self,radius=2.0,lift_deep=2.0,lift_height=3.0):
        # 创建数据
        self.theta = np.linspace((np.pi*5/4), 7/4 * np.pi , 100)
        self.radius = radius  # uwb有效区半径，初始值为电梯深度
        self.lift_deep = lift_deep  # 电梯深度
        self.lift_height = lift_height  # 电梯高度,有效半径最大值
        self.UWB_X = self.lift_deep / 2  # UWB坐标X
        self.UWB_Y = self.lift_height # UWB坐标Y
        self.paused = False
        self.slider_change = False
        # 初始化最小和及交点坐标
        self.min_sum = float('inf')
        self.min_sum_intersections = []

        # 创建图表
        self.fig, self.ax = plt.subplots(subplot_kw={'aspect': 'equal'}, figsize=(6, 6))
        self.fig.suptitle('UWB Lift Dynamic Detection', fontsize=16)
        self.ax.set_xlim(-3, self.lift_deep + 3)
        self.ax.set_ylim(-0.5, self.lift_height + 3)
        self.line, = self.ax.plot(self.UWB_X + self.radius * np.cos(self.theta), self.UWB_Y + self.radius * np.sin(self.theta), 'pink')
        self.line1, = self.ax.plot([self.UWB_X, self.UWB_X + self.radius * np.cos(self.theta[-1])], [self.UWB_Y, self.UWB_Y + self.radius * np.sin(self.theta[-1])], 'r--')
        self.line2, = self.ax.plot([self.UWB_X, self.UWB_X + self.radius * np.cos(self.theta[0])], [self.UWB_Y, self.UWB_Y + self.radius * np.sin(self.theta[0])], 'r--')

        # 添加矩形
        rect = patches.Rectangle((0, 0), self.lift_deep, self.lift_height, linewidth=1, edgecolor='b', facecolor='grey', alpha=0.2)
        self.ax.add_patch(rect)

        # 创建不重叠区域的路径
        vertices = np.vstack((np.column_stack((self.radius * np.cos(self.theta), self.lift_height + self.radius * np.sin(self.theta))),
                              np.column_stack((self.radius * np.cos(self.theta[::-1]), self.lift_height + self.radius * np.sin(self.theta[::-1])))))
        codes = [Path.MOVETO] + [Path.LINETO] * (len(self.theta) - 1) + [Path.MOVETO] + [Path.LINETO] * (len(self.theta) - 1)
        path = Path(vertices, codes)
        self.patch = PathPatch(path, facecolor='pink', edgecolor='none', alpha=0.5)
        self.ax.add_patch(self.patch)

        # 创建重叠区域的补丁
        initial_path = Path(np.array([[0, 0], [1, 1]]))  # 初始路径，避免空数组
        self.overlap_patch = PathPatch(initial_path, facecolor='b', edgecolor='none', alpha=0.5)
        self.ax.add_patch(self.overlap_patch)

        # 添加文本对象
        self.non_overlap_text = self.ax.text(0.05, 0.95, '', transform=self.ax.transAxes, fontsize=12, verticalalignment='top', color='black')
        self.overlap_text = self.ax.text(0.05, 0.90, '', transform=self.ax.transAxes, fontsize=12, verticalalignment='top', color='black')
        self.min_sum_text = self.ax.text(0.05, 0.85, '', transform=self.ax.transAxes, fontsize=12, verticalalignment='top', color='black')
        self.min_sum_intersections_text = self.ax.text(0.05, 0.80, '', transform=self.ax.transAxes, fontsize=12, verticalalignment='top')
        self.golden_point_text = self.ax.text(0.05, 0.75, '', transform=self.ax.transAxes, fontsize=12, verticalalignment='top')
        # 添加标题
        self.ax.set_title('UWB lift dynamic graphy plan2')
        self.ax.set_xlabel('lift deep(m)')
        self.ax.set_ylabel('lift height(m)')

        # 添加滑块
        self.slider_ax = self.fig.add_axes([0.25, 0.01, 0.30, 0.03], facecolor='lightgoldenrodyellow')
        self.radius_slider = Slider(self.slider_ax, 'Radius', 1.0, self.lift_height + 2, valinit=self.radius)
        self.radius_slider.on_changed(self.RadiusSliderChanged)

        # 添加按钮
        self.button_ax = self.fig.add_axes([0.8, 0.01, 0.1, 0.03])
        self.pause_button = Button(self.button_ax, 'Pause')
        self.pause_button.on_clicked(self.toggle_pause_button)

    def golden_ratio_point(self,A, B):
        phi = (1 + 5 ** 0.5) / 2  # φ ≈ 1.618
        x1, y1 = A
        x2, y2 = B
        # 计算线段 AB 的长度
        L = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        # 计算较长部分 AC 的长度
        AC = L / (1 + 1 / phi)
        # 点 C 的坐标
        Cx = round(x1 + (x2 - x1) * (AC / L),2)
        Cy = round(y1 + (y2 - y1) * (AC / L),2)
        return (Cx, Cy)

    def toggle_pause_button(self, event):
        self.paused = not self.paused
        if self.paused:
            self.pause_button.label.set_text('Resume')
        else:
            self.pause_button.label.set_text('Pause')

    def RadiusSliderChanged(self, val):
        self.radius = val
        self.slider_change = True
        self.min_sum = float('inf')
        self.update(0)

    def update(self, num):
        if self.paused and self.slider_change == False:
            return self.line, self.line1, self.line2, self.patch, self.overlap_patch, self.non_overlap_text, self.overlap_text, self.min_sum_text, self.min_sum_intersections_text
        self.slider_change = False
        r = self.radius + num / 100.0  # 更新半径
        x_data = self.UWB_X + r * np.cos(self.theta)
        y_data = self.UWB_Y + r * np.sin(self.theta)
        self.line.set_data(x_data, y_data)
        self.line1.set_data([self.UWB_X, x_data[-1]], [self.lift_height, y_data[-1]])
        self.line2.set_data([self.UWB_X, x_data[0]], [self.lift_height, y_data[0]])
        
        # 计算重叠区域
        line_coords = np.column_stack((self.line.get_xdata(), self.line.get_ydata()))
        line1_coords = np.column_stack((self.line1.get_xdata(), self.line1.get_ydata()))
        line2_coords = np.column_stack((self.line2.get_xdata(), self.line2.get_ydata()))
        
        # 合并三条线的坐标
        all_coords = np.vstack((line_coords, line1_coords, line2_coords))
        
        # 创建多边形
        polygon1 = Polygon(all_coords)
        polygon2 = Polygon([(0, 0), (self.lift_deep, 0), (self.lift_deep, self.lift_height), (0, self.lift_height)])
        overlap = polygon1.intersection(polygon2)
        non_overlap = polygon1.difference(polygon2)
        
        # 绘制不重叠区域
        if non_overlap.is_empty:
            self.patch.set_visible(False)
        else:
            self.patch.set_visible(True)
            if isinstance(non_overlap, Polygon):
                coords = np.array(non_overlap.exterior.coords)
            else:  # MultiPolygon
                coords = np.concatenate([np.array(p.exterior.coords) for p in non_overlap.geoms])
            self.patch.set_path(Path(coords))
        
        # 绘制重叠区域
        if overlap.is_empty:
            self.overlap_patch.set_visible(False)
        else:
            self.overlap_patch.set_visible(True)
            if isinstance(overlap, Polygon):
                coords = np.array(overlap.exterior.coords)
            else:  # MultiPolygon
                coords = np.concatenate([np.array(p.exterior.coords) for p in overlap.geoms])
            self.overlap_patch.set_path(Path(coords))
        
        # 更新文本内容
        ErrorArea = non_overlap.area / 2
        self.non_overlap_text.set_text(f'Pink area of right:                    {ErrorArea:.2f}')
        MissArea = self.lift_deep * self.lift_height - overlap.area - 1
        self.overlap_text.set_text(f'Grey area of bottom:               {MissArea:.2f}')
        
        # 计算和并更新最小和
        current_sum = ErrorArea + MissArea
        if current_sum < self.min_sum:
            self.min_sum = current_sum
            # 计算并记录交点
            line_string = LineString(line_coords)
            rect_polygon = Polygon([(0, 0), (self.lift_deep, 0), (self.lift_deep, self.lift_height), (0, self.lift_height)])
            intersections = line_string.intersection(rect_polygon)
            right_edge = LineString([(self.lift_deep, 0), (self.lift_deep, self.lift_height)])
            right_edge_intersections = line_string.intersection(right_edge)
            
            if right_edge_intersections.is_empty:
                self.min_sum_intersections = []
            elif isinstance(right_edge_intersections, Point):
                self.min_sum_intersections = [right_edge_intersections.coords[:]]
            elif isinstance(right_edge_intersections, LineString):
                self.min_sum_intersections = [right_edge_intersections.coords[:]]
            else:  # MultiLineString
                self.min_sum_intersections = [line.coords[:] for line in right_edge_intersections]
        
        # 格式化 min_sum_intersections 中的值，最多显示两位小数
        formatted_intersections = [
            [[round(x, 2), round(y, 2)] for x, y in intersection]
            for intersection in self.min_sum_intersections
        ]
        if formatted_intersections and len(formatted_intersections) > 0 and len(formatted_intersections[0]) > 0 and len(formatted_intersections[0][0]) > 0:
            if(self.lift_height > formatted_intersections[0][0][1]):
                minimum_r = float(math.sqrt((formatted_intersections[0][0][0]/2)**2 + ((self.lift_height-formatted_intersections[0][0][1])**2)))
                formatted_intersections[0][0].append(round(minimum_r,2))

        # 将 formatted_intersections 转换为字符串并去掉中括号
        formatted_intersections_str = str(formatted_intersections).replace('[', '').replace(']', '') 
        self.min_sum_text.set_text(f'E+M minimum value:              {self.min_sum:.2f}')
        
        self.min_sum_intersections_text.set_text(f'E+M minimum intersection:    ({formatted_intersections_str})')
        
        return self.line, self.line1, self.line2, self.patch, self.overlap_patch, self.non_overlap_text, self.overlap_text, self.min_sum_text, self.min_sum_intersections_text

    def start_animation(self):
        self.ani = animation.FuncAnimation(self.fig, self.update, frames=150, interval=50, blit=True)
        self.fig.canvas.manager.set_window_title('UWB Lift plan')  # 设置窗口标题('UWB Lift plan')
        plt.show()

# 启动动画
if __name__ == "__main__":

    plan = UWBLiftAnimationPlan1(radius=2.0,lift_deep=2.0,lift_height=3.0)
    plan.start_animation()
