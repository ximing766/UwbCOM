
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

# 设置圆的参数
center1 = (-10, 0, 0)  # 第一个圆的圆心
radius1 = 15          # 第一个圆的半径
center2 = (10, 0, 0)  # 第二个圆的圆心
radius2 = 15          # 第二个圆的半径
center3 = (-10,0,10)  # 第三个圆的圆心
radius3 = 15          # 第三个圆的半径

# 绘制第一个圆
theta = np.linspace(0, 2 * np.pi, 100)
x1 = center1[0] + radius1 * np.cos(theta)
y1 = center1[1] + radius1 * np.sin(theta)
z1 = np.zeros_like(x1)  # 第一个圆在XY平面上

# 绘制第二个圆
x2 = center2[0] + radius2 * np.cos(theta)
y2 = center2[1] + radius2 * np.sin(theta)
z2 = np.zeros_like(x2)  # 第二个圆也在XY平面上

x3 = center1[0] + radius1 * np.cos(theta)
y3 = np.zeros_like(x1) 
z3 = center1[1] + radius1 * np.sin(theta)

x4 = center3[0] + radius3 * np.cos(theta)
y4 = np.zeros_like(x4) 
z4 = center3[2] + radius3 * np.sin(theta)

# 计算两圆的交点
d = np.sqrt((center2[0] - center1[0])**2 + (center2[1] - center1[1])**2)
a = (radius1**2 - radius2**2 + d**2) / (2 * d)
h = np.sqrt(radius1**2 - a**2)
x0 = center1[0] + a * (center2[0] - center1[0]) / d
y0 = center1[1] + a * (center2[1] - center1[1]) / d
rx = -h * (center2[1] - center1[1]) / d
ry = h * (center2[0] - center1[0]) / d

intersection1 = (x0 + rx, y0 + ry, 0)
intersection2 = (x0 - rx, y0 - ry, 0)

# 创建3D图形
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# 绘制两个圆
ax.plot(x1, y1, z1, label="circle 1", color='blue')
ax.plot(x2, y2, z2, label="circle 2", color='blue')
ax.plot(x4, y4, z4, label="circle 3", color='pink')
ax.plot(x3, y3, z3, label="circle 4", color='pink')

# 绘制交点
ax.plot([intersection1[0]], [intersection1[1]], [intersection1[2]], 'ro')
ax.plot([intersection2[0]], [intersection2[1]], [intersection2[2]], 'ro')

# 绘制圆心
ax.plot([center1[0]], [center1[1]], [center1[2]], 'go')
ax.plot([center2[0]], [center2[1]], [center2[2]], 'go')
ax.plot([center3[0]], [center3[1]], [center3[2]], 'go')

# 设置图表标签和图例
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('demo')
ax.legend()

# 显示图表
plt.show()
