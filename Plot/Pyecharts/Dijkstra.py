import networkx as nx
from pyecharts.charts import Graph
from pyecharts import options as opts
from pyecharts.globals import ThemeType

# 创建一个有向图
G = nx.DiGraph()
edges = [
        ("A", "B", 1), ("A", "C", 4),
        ("B", "C", 2), ("B", "D", 5),
        ("C", "D", 1), ("A", "D", 8),
        ("B", "E", 3), ("C", "E", 6),
        ("D", "E", 2), ("E", "F", 7),
        ("F", "A", 9), ("A", "F", 8),
]
pos = {
        "A": (0, 0), "B": (1, 0), "C": (4, 0),
        "D": (5, 0), "E": (4, 3), "F": (-9, 0),
}
G.add_weighted_edges_from(edges)

shortest_path = nx.shortest_path(G, source="F", target="D", weight="weight")
shortest_path_length = nx.shortest_path_length(G, source="F", target="D", weight="weight")
print("最短路径:", shortest_path)
print("最短路径长度:", shortest_path_length)

# 标识最短路径的边
highlight_links = [{"source": edge[0], "target": edge[1]} for edge in zip(shortest_path, shortest_path[1:])]
print("highlight_links:", highlight_links)

#opts.GraphNode(name = node, symbol_size = 20, category = 0, x=pos[node][0], y=pos[node][1])
nodes = [opts.GraphNode(name = node, symbol_size = 20, category = 0) if node in shortest_path else \
         opts.GraphNode(name = node, symbol_size = 15, category = 1) for node in G.nodes()]
# links = [{"source": edge[0], "target": edge[1], "value": G.get_edge_data(*edge,default=None)['weight']} if {"source": edge[0], "target": edge[1]}  not in highlight_links else \
#          {"source": edge[0], "target": edge[1], "value": G.get_edge_data(*edge,default=None)['weight'],"linestyle_opts": opts.LineStyleOpts(width=3, color='red')} for edge in G.edges()]
print("nodes:", nodes)
Categor = [{'name': 'Shortest Path'}, {'name': 'others'}]

# 为普通边和最短路径的边设置不同的样式
links = []
for edge in G.edges():
    # 获取边的权重
    weight = G.get_edge_data(*edge, default=None)['weight']
    # 检查边是否属于最短路径
    if any(h['source'] == edge[0] and h['target'] == edge[1] for h in highlight_links):
        link = {
            "source": edge[0],
            "target": edge[1],
            "value": weight,
            "lineStyle": {"color": "pink", "width": 3}  # 设置最短路径的边的颜色和宽度
        }
    else:
        link = {
            "source": edge[0],
            "target": edge[1],
            "value": weight,
        }
    links.append(link)
print("links:", links)

graph = (
    Graph(init_opts=opts.InitOpts(width="800px", height="800px", theme=ThemeType.ROMA))
    .add(
        "",
        nodes,
        links,
        categories=Categor, 
        repulsion=5000,
        layout="force",
        edge_symbol=[None, 'arrow'],
        #linestyle_opts=opts.LineStyleOpts(curve=0.2),
        label_opts=opts.LabelOpts(is_show=True, position="right",  formatter="{b}"),
        edge_label=opts.LabelOpts(is_show=True, position="middle", formatter="{c}"), #"{b} : {c}"   #c为value这里的links没有value属性
        
    )
    .set_global_opts(title_opts=opts.TitleOpts(title="Shortest Path"))
)

graph.render("./Mesh/HTML/shortest_path_chart.html")


















