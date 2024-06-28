# UwbCOM
UWB串口助手

# 相关指令
pyinstaller --noconsole --onefile --name "UwbCOM" UwbCOM.py

import sys ; sys.setrecursionlimit(sys.getrecursionlimit() * 5)
spec添加上面一行后用下面的安装
pyinstaller UwbCOM_V1.1.spec 

# 简介
UWB的串口GUI工具，显示用户位置
