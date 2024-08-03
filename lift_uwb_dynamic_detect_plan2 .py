import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
import matplotlib.patches as patches
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from shapely.geometry import Polygon, LineString, Point

# 创建数据
theta = np.linspace((np.pi*5/4), 7/4 * np.pi , 100)
radius = 2.0  # uwb有效区半径，初始值为电梯深度

lift_deep = 2.0  # 电梯深度
lift_height = 3.0  # 电梯高度,有效半径最大值
UWB_X = 1.0  # UWB坐标X
UWB_Y = 3.0  # UWB坐标Y

# 创建图表
fig, ax = plt.subplots(subplot_kw={'aspect': 'equal'})
ax.set_xlim(-1, 5)
ax.set_ylim(-1, 5)
line, = ax.plot(UWB_X +radius * np.cos(theta), UWB_Y + radius * np.sin(theta),'pink')
line1, = ax.plot([UWB_X, UWB_X + radius * np.cos(theta[-1])], [UWB_Y, UWB_Y + radius * np.sin(theta[-1])], 'r--')
line2, = ax.plot([UWB_X, UWB_X + radius * np.cos(theta[0])], [UWB_Y, UWB_Y + radius * np.sin(theta[0])], 'r--')

# 添加矩形
rect = patches.Rectangle((0, 0), lift_deep, lift_height, linewidth=1, edgecolor='b', facecolor='grey', alpha=0.2)
ax.add_patch(rect)

# 创建不重叠区域的路径
vertices = np.vstack((np.column_stack((radius * np.cos(theta), lift_height + radius * np.sin(theta))),
                      np.column_stack((radius * np.cos(theta[::-1]), lift_height + radius * np.sin(theta[::-1])))))
codes = [Path.MOVETO] + [Path.LINETO] * (len(theta) - 1) + [Path.MOVETO] + [Path.LINETO] * (len(theta) - 1)
path = Path(vertices, codes)
patch = PathPatch(path, facecolor='pink', edgecolor='none', alpha=0.5)
ax.add_patch(patch)

# 创建重叠区域的补丁
initial_path = Path(np.array([[0, 0], [1, 1]]))  # 初始路径，避免空数组
overlap_patch = PathPatch(initial_path, facecolor='b', edgecolor='none', alpha=0.5)
ax.add_patch(overlap_patch)

# 添加文本对象
non_overlap_text = ax.text(0.05, 0.95, '', transform=ax.transAxes, fontsize=12, verticalalignment='top', color='black')
overlap_text = ax.text(0.05, 0.90, '', transform=ax.transAxes, fontsize=12, verticalalignment='top', color='black')
min_sum_text = ax.text(0.05, 0.85, '', transform=ax.transAxes, fontsize=12, verticalalignment='top', color='black')
min_sum_intersections_text = ax.text(0.05, 0.80, '', transform=ax.transAxes, fontsize=12, verticalalignment='top')

# 添加标题
ax.set_title('UWB lift dynamic graphy')
ax.set_xlabel('lift deep(m)')
ax.set_ylabel('lift height(m)')

# 初始化最小和及交点坐标
min_sum = float('inf')
min_sum_intersections = []

def update(num, theta, line, line1, line2, patch, overlap_patch):
    global min_sum, min_sum_intersections
    r = radius + num / 100.0  # 更新半径
    x_data = UWB_X + r * np.cos(theta)
    y_data = UWB_Y + r * np.sin(theta)
    line.set_data(x_data, y_data)
    line1.set_data([UWB_X, x_data[-1]], [lift_height, y_data[-1]])
    line2.set_data([UWB_X, x_data[0]], [lift_height, y_data[0]])
    
    # 更新不重叠区域的路径
    vertices = np.vstack((np.column_stack((r * np.cos(theta), lift_height + r * np.sin(theta))),
                          np.column_stack((r * np.cos(theta[::-1]), lift_height + r * np.sin(theta[::-1])))))
    path = Path(vertices, codes)
    patch.set_path(path)
    
    # 计算重叠区域
    line_coords = np.column_stack((line.get_xdata(), line.get_ydata()))
    line1_coords = np.column_stack((line1.get_xdata(), line1.get_ydata()))
    line2_coords = np.column_stack((line2.get_xdata(), line2.get_ydata()))
    
    # 合并三条线的坐标
    all_coords = np.vstack((line_coords, line1_coords, line2_coords))
    
    # 创建多边形
    polygon1 = Polygon(all_coords)
    polygon2 = Polygon([(0, 0), (lift_deep, 0), (lift_deep, lift_height), (0, lift_height)])
    overlap = polygon1.intersection(polygon2)
    non_overlap = polygon1.difference(polygon2)
    
    # 绘制不重叠区域
    if non_overlap.is_empty:
        patch.set_visible(False)
    else:
        patch.set_visible(True)
        if isinstance(non_overlap, Polygon):
            coords = np.array(non_overlap.exterior.coords)
        else:  # MultiPolygon
            coords = np.concatenate([np.array(p.exterior.coords) for p in non_overlap.geoms])
        patch.set_path(Path(coords))
    
    # 绘制重叠区域
    if overlap.is_empty:
        overlap_patch.set_visible(False)
    else:
        overlap_patch.set_visible(True)
        if isinstance(overlap, Polygon):
            coords = np.array(overlap.exterior.coords)
        else:  # MultiPolygon
            coords = np.concatenate([np.array(p.exterior.coords) for p in overlap.geoms])
        overlap_patch.set_path(Path(coords))
    
    # 更新文本内容
    ErrorArea = non_overlap.area/2
    non_overlap_text.set_text(f'a half of EDA(pink area): {ErrorArea:.2f}')
    MissArea = lift_deep * lift_height - overlap.area - 1
    overlap_text.set_text(f'Remove top two area MOA(grey): {MissArea:.2f}')
    
    # 计算和并更新最小和
    current_sum = ErrorArea + MissArea
    if current_sum < min_sum:
        min_sum = current_sum
        # 计算并记录交点
        line_string = LineString(line_coords)
        rect_polygon = Polygon([(0, 0), (lift_deep, 0), (lift_deep, lift_height), (0, lift_height)])
        intersections = line_string.intersection(rect_polygon)
        right_edge = LineString([(lift_deep, 0), (lift_deep, lift_height)])
        right_edge_intersections = line_string.intersection(right_edge)
        
        if right_edge_intersections.is_empty:
            min_sum_intersections = []
        elif isinstance(right_edge_intersections, Point):
            min_sum_intersections = [right_edge_intersections.coords[:]]
        elif isinstance(right_edge_intersections, LineString):
            min_sum_intersections = [right_edge_intersections.coords[:]]
        else:  # MultiLineString
            min_sum_intersections = [line.coords[:] for line in right_edge_intersections]

    # 格式化 min_sum_intersections 中的值，最多显示两位小数
    formatted_intersections = [
        [(round(x, 2), round(y, 2)) for x, y in intersection]
        for intersection in min_sum_intersections
    ]
    # 将 formatted_intersections 转换为字符串并去掉中括号
    formatted_intersections_str = str(formatted_intersections).replace('[', '').replace(']', '')

    min_sum_text.set_text(f'Error+Miss minmax value: {min_sum:.2f}')
    min_sum_intersections_text.set_text(f'Min sum intersections: {formatted_intersections_str}')
    
    return line, line1, line2, patch, overlap_patch, non_overlap_text, overlap_text, min_sum_text,min_sum_intersections_text

# 创建动画
ani = animation.FuncAnimation(fig, update, frames=150, fargs=[theta, line, line1, line2, patch, overlap_patch], interval=50, blit=True)


plt.show()

