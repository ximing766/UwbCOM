import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Line, Bar, Grid, Page
from pyecharts.commons.utils import JsCode
import os

# 读取CSV文件
file_path = os.path.join(os.path.dirname(__file__), "XM.csv")
df = pd.read_csv(file_path, skipinitialspace=True)

# 获取数据
points = ['P2', 'P3', 'P4', 'P5', 'P6', 'P9']
true_height = 50
data_length = len(df)
x_data = list(range(1, data_length + 1))  # 样本序号

# 创建折线图
def create_line_chart():
    line = Line()
    line.add_xaxis(x_data)

    
    
    # 添加每个点位的数据
    colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272']
    for i, point in enumerate(points):
        line.add_yaxis(
            series_name=point,
            y_axis=df[point].tolist(),
            symbol_size=8,
            is_smooth=True,
            linestyle_opts=opts.LineStyleOpts(width=2),
            label_opts=opts.LabelOpts(is_show=False),
            itemstyle_opts=opts.ItemStyleOpts(color=colors[i]),
        )
    
    line.add_yaxis(
        series_name="真实高度",
        y_axis=[true_height] * data_length,
        symbol_size=0,
        is_smooth=True,
        linestyle_opts=opts.LineStyleOpts(
            width=2,
            type_="dashed",
        ),
        label_opts=opts.LabelOpts(is_show=False),
        itemstyle_opts=opts.ItemStyleOpts(color="#000000"),
    )
    
    # label_opts=opts.LabelOpts(is_show=False),
    
    # 设置全局选项
    line.set_global_opts(
        title_opts=opts.TitleOpts(
            title="各点位高度测量值与真实高度对比",
            subtitle="数据来源: XM.csv",
            pos_left="center",
        ),
        tooltip_opts=opts.TooltipOpts(
            trigger="axis",
            axis_pointer_type="cross",
            background_color="rgba(245, 245, 245, 0.8)",
            border_width=1,
            border_color="#ccc",
            textstyle_opts=opts.TextStyleOpts(color="#000"),
        ),
        legend_opts=opts.LegendOpts(
            pos_top="10%",
            orient="horizontal",
            item_gap=25,
        ),
        xaxis_opts=opts.AxisOpts(
            type_="category",
            name="样本序号",
            name_location="center",
            name_gap=30,
            boundary_gap=False,
        ),
        yaxis_opts=opts.AxisOpts(
            type_="value",
            name="高度 (cm)",
            name_location="center",
            name_gap=40,
            min_=0,
            max_=100,
            split_number=6,
            axisline_opts=opts.AxisLineOpts(is_show=True),
            axistick_opts=opts.AxisTickOpts(is_show=True),
            splitline_opts=opts.SplitLineOpts(is_show=True),
        ),
        toolbox_opts = opts.ToolboxOpts(is_show=True,
                                        feature=opts.ToolBoxFeatureOpts(save_as_image=opts.ToolBoxFeatureSaveAsImageOpts(background_color="white",pixel_ratio=3))),
        datazoom_opts=[
            opts.DataZoomOpts(range_start=0, range_end=100),
            opts.DataZoomOpts(type_="inside"),
        ],
    )
    return line


line = create_line_chart()
output_file = os.path.join(os.path.dirname(__file__), "height_comparison.html")
line.render(output_file)
print(f"图表已保存至: {output_file}")