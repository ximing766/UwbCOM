# UwbCOM
UWB串口助手

# APP生成步骤

需要进入myenv虚拟环境，否则没有相关包。

pyinstaller --noconsole --onefile --name "UwbCOM" UwbCOM.py

import sys ; sys.setrecursionlimit(sys.getrecursionlimit() * 5)

spec添加上面一行后用下面的安装

pyinstaller UwbCOM.spec 

# 简介
UWB的串口GUI工具，显示用户位置

# V1.1
初始化版本，映射用户位置

# V1.2
1.添加了多设备设别（待UWB设备优化bug）

2.添加了界面闪烁

3.添加了读取card信息

# V1.3

1.删除了界面显示闪烁效果

2.优化了接收代码逻辑

3.修复了和UWB锚点设备通信数据串行bug



