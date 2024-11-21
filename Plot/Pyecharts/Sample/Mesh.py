from pyecharts import options as opts
from pyecharts.charts import Graph
from pyecharts.globals import ThemeType
# nodes = [
#     {"name": "结点1", "symbolSize": 30,"category": 0},
#     {"name": "结点2", "symbolSize": 30,"category": 0},
#     {"name": "结点3", "symbolSize": 30,"category": 0},
#     {"name": "结点4", "symbolSize": 30,"category": 2},
#     {"name": "结点5", "symbolSize": 30,"category": 2},
#     {"name": "结点6", "symbolSize": 30,"category": 2},
#     {"name": "结点7", "symbolSize": 30,"category": 1},
#     {"name": "结点8", "symbolSize": 30,"category": 1},
#     {"name": "结点9", "symbolSize": 30,"category": 1},
# ]

# links = []
# for i in nodes:
#     for j in nodes:
#         links.append({"source": i.get("name"), "target": j.get("name")})
# print(links)

nodes = [
    opts.GraphNode(name="结点1", symbol_size=40, value=2, category=0 ,is_disabled_emphasis=True),
    opts.GraphNode(name="结点2", symbol_size=30, value=3, category=1),
    opts.GraphNode(name="结点3", symbol_size=30, value=4, category=1),
    opts.GraphNode(name="结点4", symbol_size=30, category=2),
    opts.GraphNode(name="结点5", symbol_size=30, category=2),
    opts.GraphNode(name="结点6", symbol_size=30, category=3),
    opts.GraphNode(name="结点7", symbol_size=30, category=3),
]
print("nodes:",nodes)
links = [
    opts.GraphLink(source="结点1", target="结点2", value=2),
    opts.GraphLink(source="结点1", target="结点3", value=2),
    opts.GraphLink(source="结点1", target="结点4", value=2),
    opts.GraphLink(source="结点1", target="结点5", value=2),
    opts.GraphLink(source="结点1", target="结点6", value=2),
    opts.GraphLink(source="结点1", target="结点7", value=2),
    
    
    opts.GraphLink(source="结点2", target="结点3", value=3),
    opts.GraphLink(source="结点4", target="结点5", value=5),
    opts.GraphLink(source="结点6", target="结点7", value=7),
]


Categor = [{'name': '簇1'}, {'name': '簇2'},{'name': '簇3'},{'name': '簇4'}]
c = (
    Graph(init_opts=opts.InitOpts(width="800px", height="800px", theme=ThemeType.ROMA))
    .add(
            "", 
            nodes, links, 
            categories=Categor, 
            repulsion=5000,
            edge_label=opts.LabelOpts(      
                is_show=True, position="middle", formatter=  "{c}", #"{b} : {c}"   #c为value这里的links没有value属性
            ),
            label_opts=opts.LabelOpts(is_show=True, position="right", formatter="{b}"),
            linestyle_opts=opts.LineStyleOpts(width=1.0, curve=0.0, opacity=0.9),
        )
    .set_global_opts(
        title_opts=opts.TitleOpts(title="Graph")
        )
    .render("./Mesh/HTML/graph_base.html")
)