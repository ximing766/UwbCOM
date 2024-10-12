import json

from pyecharts import options as opts
from pyecharts.charts import Graph


with open("./Mesh/Sample/les-miserables.json", "r", encoding="utf-8") as f:
    j = json.load(f)
    nodes = j["nodes"]
    links = j["links"]
    categories = j["categories"]
print("nodes:\n")
print(nodes)
print("categories:\n")
print(categories)
c = (
    Graph(init_opts=opts.InitOpts(width="800px", height="800px"))
    .add(
        "",
        nodes=nodes,
        links=links,
        categories=categories,
        repulsion=50,
        layout="force",
        is_rotate_label=True,
        linestyle_opts=opts.LineStyleOpts(color="source", curve=0.3),
        label_opts=opts.LabelOpts(position="right"),
    )
    .set_global_opts(
        title_opts=opts.TitleOpts(title="Graph-Les Miserables"),
        legend_opts=opts.LegendOpts(orient="vertical", pos_left="2%", pos_top="20%"),
    )
    .render("./Mesh/HTML/graph_les_miserables.html")
)
