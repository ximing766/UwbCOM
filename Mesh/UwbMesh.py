from pyecharts import options as opts
from pyecharts.charts import Graph,Grid

# 定义节点及其坐标
nodes = [
    {"name": "节点1", "symbolSize": 10, "x": 300, "y": 300},
    {"name": "节点2", "symbolSize": 10, "x": 600, "y": 300},
    {"name": "节点3", "symbolSize": 10, "x": 450, "y": 450},
    {"name": "节点4", "symbolSize": 10, "x": 300, "y": 150},
    {"name": "节点5", "symbolSize": 10, "x": 600, "y": 150},
]

# 定义边，即节点之间的连接关系
links = [
    ("节点1", "节点2"),
    ("节点1", "节点3"),
    ("节点2", "节点4"),
    ("节点3", "节点4"),
    ("节点4", "节点5"),
    ("节点2", "节点5"),
]

graph = (
    # Graph(init_opts=opts.InitOpts(bg_color={"type": "pattern", "image": "https://echarts.apache.org/zh/images/favicon.png",\
    #                                         "repeat": "repeat"}))
    Graph(init_opts=opts.InitOpts(width="1000px", height="800px"))
    .add(
        "",
        nodes,
        links,
        repulsion=8000,
        edge_symbol=["circle", "arrow"],
        layout="force",
        label_opts=opts.LabelOpts(is_show=True, position="right", formatter="{b}"),
    )
    .set_global_opts(
        title_opts=opts.TitleOpts(title="UWB Mesh Network Topology"),
        tooltip_opts=opts.TooltipOpts(trigger="item", formatter="{b}"),
    )
)

# 渲染图表到 HTML 文件中
graph.render("./Mesh/HTML/UwbMesh.html")