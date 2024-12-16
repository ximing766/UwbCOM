# UwbCOM :smile::smile::smile:

**UWB串口助手**，显示User的实时相对位置。


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
pyinstaller --noconsole --onefile -i UWBCOM.ico --add-data "UWBCOM.ico;." --name "UwbCOM_V1.4" UwbCOM.py
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

- 支持显示多用户(最多同时支持20个用户显示)

- 支持TWR定位方案

- 支持AOA定位方案

- 支持不同类型场景的定位方案切换

- 数据接收json，存储为csv

  

# 安装

Clone  repository:

```
git clone git@github.com:ximing766/UwbCOM.git
```

创建虚拟环境
```
conda activate myenv
```

在myenv内再次创建虚拟环境(减少exe大小)
```
python -m venv venv
.\venv\Scripts\activate
```

安装包

```
pip install -r requirements.txt
```

# 下载

[https://github.com/ximing766/UwbCOM/releases/tag/v1.3]: 

