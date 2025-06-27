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

2：执行auto-py-to-exe(需要安装)

```
auto-py-to-exe
```
3：加载UwbCOM.json配置文件

4：run

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

