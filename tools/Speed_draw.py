import pyecharts.options as opts
from pyecharts.charts import Line
import pandas as pd
import numpy as np

# 读取CSV文件
data = pd.read_csv("temp\\speed_5a09.csv", sep=',', header=None, usecols=[1])
print(data.head(5))

# 将数据转换为numpy数组并重塑形状
data = np.array(data).reshape(-1)

# 创建Line对象
c = (
    Line()
    .add_xaxis(xaxis_data=list(range(len(data))))  # 添加x轴数据
    .add_yaxis(
        series_name="Speed",
        y_axis=data,
        is_smooth=True,  # 是否平滑显示线条
        areastyle_opts=opts.AreaStyleOpts(opacity=0.5),  # 数据区域缩进样式
    )
    .set_global_opts(
        title_opts=opts.TitleOpts(title="Line-smooth"),  # 设置标题
        tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),  # 设置工具提示
        legend_opts=opts.LegendOpts(pos_left="right"),  # 设置图例位置
        xaxis_opts=opts.AxisOpts(name="Index", axislabel_opts=opts.LabelOpts(rotate=45)),  # 设置X轴标签和旋转角度
        yaxis_opts=opts.AxisOpts(name="Speed (cm/s)"),  # 设置Y轴标签
        datazoom_opts=[opts.DataZoomOpts()],  # 添加数据缩放组件
    )
    .set_series_opts(
        label_opts=opts.LabelOpts(is_show=False),  # 不显示数据点的文本标签
    )
    .render("./Mesh/HTML/UWB-speed.html")  # 渲染图表并保存为HTML文件
)