"""

* Chan的方程式解法,用于3个固定锚点定位.1主2从.
* 3个锚点的纵坐标不能都相同,否则无法解出.
* 以定位误差在30cm为成功,该算法的成功率约为89%
* 若定位频率较高,建议对定位结果进行适当滤波

"""

import math
import matplotlib.pyplot as plt
import random
import numpy as np

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance_to(self, other):
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

class ChanEALG:
    def __init__(self, master, slave1, slave2, tag=[0,0], c=299792458, s1=0, s2=0):   #光速为299792458m/s
        self.master = master
        self.slave1 = slave1
        self.slave2 = slave2
        self.tag = tag
        self.c = c
        self.s1 = s1         #Slave1与Master的距离差
        self.s2 = s2         #Slave2与Master的距离差

    def calculate_distances(self):
        distance_to_master = self.tag.distance_to(self.master)
        distance_to_slave1 = self.tag.distance_to(self.slave1)
        distance_to_slave2 = self.tag.distance_to(self.slave2)
        self.s1 = distance_to_slave1 - distance_to_master           #实际需要通过获取参数计算距离差
        self.s2 = distance_to_slave2 - distance_to_master

    def solve_tdoa(self):
        x1, y1 = self.master.x, self.master.y
        x2, y2 = self.slave1.x, self.slave1.y
        x3, y3 = self.slave2.x, self.slave2.y

        k1 = x1**2 + y1**2
        k2 = x2**2 + y2**2
        k3 = x3**2 + y3**2

        p1_molecule = (y2 - y1) * self.s2**2 - (y3 - y1) * self.s1**2 + (y3 - y1) * (k2 - k1) - (y2 - y1) * (k3 - k1)
        p1_denominator = (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)
        p1 = p1_molecule / (p1_denominator * 2)
        q1 = ((y2 - y1) * self.s2 - (y3 - y1) * self.s1) / ((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1))

        p2_molecule = (x2 - x1) * self.s2**2 - (x3 - x1) * self.s1**2 + (x3 - x1) * (k2 - k1) - (x2 - x1) * (k3 - k1)
        p2_denominator = (x3 - x1) * (y2 - y1) - (x2 - x1) * (y3 - y1)
        p2 = p2_molecule / (p2_denominator * 2)
        q2 = ((x2 - x1) * self.s2 - (x3 - x1) * self.s1) / ((x3 - x1) * (y2 - y1) - (x2 - x1) * (y3 - y1))

        a = q1**2 + q2**2 - 1
        b = -2 * ((x1 - p1) * q1 + (y1 - p2) * q2)
        c = (x1 - p1)**2 + (y1 - p2)**2

        if (b**2 - 4*a*c) < 0:
            print("result is not exist")
            return 0,0

        r1 = (-b + math.sqrt(b**2 - 4*a*c)) / (2 * a)
        r2 = (-b - math.sqrt(b**2 - 4*a*c)) / (2 * a)

        if r1 > 0:
            return p1 + q1 * r1, p2 + q2 * r1
        else:
            return p1 + q1 * r2, p2 + q2 * r2

    def plot(self,x,y):
        plt.scatter(self.master.x, self.master.y, color='red', label='Master', marker='o', s=150)
        plt.scatter(self.slave1.x, self.slave1.y, color='blue', label='Slave1', marker='o', s=150)
        plt.scatter(self.slave2.x, self.slave2.y, color='green', label='Slave2', marker='o', s=150)
        plt.scatter(self.tag.x, self.tag.y, color='purple', label='Tag', marker='s', s=150)
        x, y = x,y
        plt.scatter(x, y, color='orange', label='Tag_predict', marker='*', s=150)

        plt.xlabel('X-axis')
        plt.ylabel('Y-axis')
        plt.legend()
        plt.show()


if __name__ == "__main__":

    c = 3120.77
    Master = Point(250, 500)
    Slave1 = Point(0, 0)
    Slave2 = Point(500, 0)
    DistanceDiff = []        #记录距离差

    for i in range(1000):
        Tag = Point(random.randint(-500,500),random.randint(-500,500))
        print(Tag.__repr__())

        # 创建ChanEALG对象
        tdoa = ChanEALG(Master, Slave1, Slave2, Tag, c)
        tdoa.calculate_distances()

        x, y = tdoa.solve_tdoa()
        Tag_predict = Point(x,y)
        print("Predict location is :", Tag_predict)
        print("Actual location is :", Tag)
        print("Distance diff is :",Tag.distance_to(Tag_predict))
        DistanceDiff.append(Tag.distance_to(Tag_predict))
        # tdoa.plot(x,y)
    
    DistanceDiff_array = np.array(DistanceDiff)
    
    DistanceDiff_array = [x for x in DistanceDiff_array if x <= 100]
    print("有效定位:",len(DistanceDiff_array)/len(DistanceDiff))
    x_values = np.arange(len(DistanceDiff_array))
    plt.scatter(x_values,DistanceDiff_array)
    plt.show()