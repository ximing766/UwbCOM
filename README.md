# UwbCOM

**UWB串口助手**

# exe生成步骤

1：需要进入myenv虚拟环境(执行下方指令1)，否则没有相关包（该环境下exe太大，希望更小则再进入uwbenv,工程路径下执行下方指令2）。

```
 activate myenv；
```

```
uwbenv\Scripts\activate
```

2：执行

```
pyinstaller --noconsole --onefile -i UWB.ico --add-data "UWB.ico;." --name "UwbCOM_V1.0" UwbCOM.py
```

3：若失败，在生成的spec添加一行后执行4

```
import sys ; sys.setrecursionlimit(sys.getrecursionlimit() * 5)
```

4:使用下方命令安装

```
pyinstaller UwbCOM.spec 
```



# 简介

UWB的串口GUI工具，显示用户位置。

- 目前支持TWR的GATE和LIFT两种方案下定位
- 提供了UL-TDOA的demo
- 提供了LIFT方案的两种演示

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

# V1.4

1.修改了界面主题

2.增加了串口和burd获取方式

3.增加了各窗口组件的自适应功能

# V1.5

1.减少了生成exe文件的大小（pipenv）

2.添加了一些pyqt的测试文件

3.新增了串口程序扫描功能

4.clear2按钮能够清除更多内容

## V1.5.1

1.修改了界面整体处理逻辑，现在不需要重启助手来进行初始化了

2.添加了一点点界面优化

3.抛弃了pipenv方案（太难用了），改为使用venv生成exe

# V2.0

1.新增了模式选择，支持GATE、LIFT两种模式

2.新增了电梯演示方案

3.新增了参考坐标和半径计算，方便调试

4.细节调整

# V2.0.5
1.添加了nLos区域显示

2.用户坐标预测现在支持卡尔曼和弹性网络两种方案

3.修复新用户添加时出现的数组越界bug

4.卡尔曼方案现在支持多用户,但效果不佳

# V2.0.7
1.滤波算法现在可选了

2.现在不再对卡信息做解析，仅获取和显示，卡信息的解析由Uwb设备完成

3.修复了一些bug

# V2.0.8
1.支持动态显示红/蓝/nLos区