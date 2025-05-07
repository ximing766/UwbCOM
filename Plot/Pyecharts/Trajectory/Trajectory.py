import numpy as np
from pyecharts import options as opts
from pyecharts.charts import Timeline, Grid, Line, Scatter, EffectScatter
from pyecharts.globals import ThemeType, SymbolType
import math
import pandas as pd
import os
from pyecharts.commons.utils import JsCode

class TrajectoryVisualizer:
    def __init__(self, title="UWB用户移动轨迹可视化"):
        """
        初始化轨迹可视化器
        
        Args:
            title: 可视化标题
        """
        self.title = title
        self.colors = ["#5470c6", "#91cc75", "#fac858", "#ee6666", "#73c0de", "#3ba272", "#fc8452", "#9a60b4"]
        
    def load_trajectory_data(self, csv_file):
        """
        从CSV文件加载轨迹数据
        
        Args:
            csv_file: CSV文件路径
            
        Returns:
            按用户分组的轨迹数据字典，每个用户对应一个轨迹列表
        """
        # 读取CSV文件
        df = pd.read_csv(csv_file)
        df.columns = df.columns.str.strip()
        
        # 按User列分组
        user_groups = df.groupby('User')
        
        # 存储每个用户的轨迹数据
        user_trajectories = {}
        
        # 为每个用户提取x和y坐标
        for user_id, group in user_groups:
            trajectory = []
            for _, row in group.iterrows():
                trajectory.append([float(row['x']), float(row['y'])])
            user_trajectories[user_id] = trajectory
            
        return user_trajectories
    
    def create_frame(self, user_trajectories, current_frame, title):
        """
        创建单个时间帧，显示所有用户在特定时间点的位置
        
        Args:
            user_trajectories: 所有用户的轨迹数据
            current_frame: 当前帧索引
            title: 帧标题
            
        Returns:
            Grid对象
        """
        # 计算所有轨迹点的坐标范围
        all_x = []
        all_y = []
        for user_id, trajectory in user_trajectories.items():
            if current_frame < len(trajectory):
                all_x.append(trajectory[current_frame][0])
                all_y.append(trajectory[current_frame][1])
                
                # 添加历史轨迹点
                for i in range(current_frame):
                    all_x.append(trajectory[i][0])
                    all_y.append(trajectory[i][1])
        
        # 计算坐标轴范围
        x_min, x_max = min(all_x) - 2, max(all_x) + 2
        y_min, y_max = min(all_y) - 2, max(all_y) + 2
        
        # 创建散点图和线图
        scatter = Scatter()
        lines = []
        
        # 为每个用户添加轨迹
        for idx, (user_id, trajectory) in enumerate(user_trajectories.items()):
            if current_frame >= len(trajectory):
                continue
                
            # 获取当前用户的颜色
            color = self.colors[idx % len(self.colors)]
            
            # 提取当前轨迹点和历史轨迹
            current_point = trajectory[current_frame]
            history_points = trajectory[:current_frame+1]
            
            # 创建当前位置的散点
            effect_scatter = (
                EffectScatter()
                .add_xaxis([current_point[0]])
                .add_yaxis(
                    f"用户{user_id}",
                    [current_point[1]],
                    symbol_size=15,
                    symbol=SymbolType.ARROW,
                    effect_opts=opts.EffectOpts(
                        scale=3.5, 
                        period=1,
                        color=color,
                        brush_type="fill"
                    ),
                    itemstyle_opts=opts.ItemStyleOpts(
                        color=color,
                        border_color="#000",
                        border_width=1
                    ),
                    label_opts=opts.LabelOpts(
                        is_show=True,
                        position="right",
                        formatter=JsCode(
                            "function(params) {return params.seriesName;}"
                        ),
                        font_size=12,
                        font_weight="bold"
                    )
                )
            )
            
            # 创建历史轨迹线
            x_data = [p[0] for p in history_points]
            y_data = [p[1] for p in history_points]
            
            line = (
                Line()
                .add_xaxis(x_data)
                .add_yaxis(
                    f"用户{user_id}轨迹", 
                    y_data,
                    symbol="emptyCircle",
                    symbol_size=6,
                    linestyle_opts=opts.LineStyleOpts(
                        width=2, 
                        color=color,
                        type_="dashed" if idx % 2 == 0 else "solid"
                    ),
                    itemstyle_opts=opts.ItemStyleOpts(color=color),
                    label_opts=opts.LabelOpts(is_show=False),
                    areastyle_opts=opts.AreaStyleOpts(opacity=0.1, color=color),
                    is_symbol_show=True
                )
            )
            
            lines.append(line)
        
        # 组合所有图表
        grid = Grid(
            init_opts=opts.InitOpts(
                bg_color="#f4f4f4",
                animation_opts=opts.AnimationOpts(animation_delay=500, animation_easing="elasticOut")
            )
        )
        
        # 设置全局选项
        global_opts = {
            "title_opts": opts.TitleOpts(
                title=title,
                subtitle="基于UWB定位数据",
                pos_left="center",
                title_textstyle_opts=opts.TextStyleOpts(
                    font_size=18,
                    font_weight="bold"
                )
            ),
            "legend_opts": opts.LegendOpts(
                pos_top="5%",
                orient="horizontal",
                item_gap=25
            ),
            "tooltip_opts": opts.TooltipOpts(
                trigger="axis",
                axis_pointer_type="cross",
                background_color="rgba(255,255,255,0.8)",
                border_color="#ccc",
                border_width=1,
                textstyle_opts=opts.TextStyleOpts(color="#000")
            ),
            "xaxis_opts": opts.AxisOpts(
                type_="value", 
                min_=x_min,
                max_=x_max,
                name="X坐标 (m)",
                name_location="center",
                name_gap=30,
                axislabel_opts=opts.LabelOpts(formatter="{value} m"),
                axisline_opts=opts.AxisLineOpts(
                    linestyle_opts=opts.LineStyleOpts(color="#5793f3")
                ),
                splitline_opts=opts.SplitLineOpts(
                    is_show=True,
                    linestyle_opts=opts.LineStyleOpts(
                        color="#ddd", width=1, type_="dashed"
                    )
                )
            ),
            "yaxis_opts": opts.AxisOpts(
                type_="value", 
                min_=y_min,
                max_=y_max,
                name="Y坐标 (m)",
                name_location="center",
                name_gap=40,
                axislabel_opts=opts.LabelOpts(formatter="{value} m"),
                axisline_opts=opts.AxisLineOpts(
                    linestyle_opts=opts.LineStyleOpts(color="#5793f3")
                ),
                splitline_opts=opts.SplitLineOpts(
                    is_show=True,
                    linestyle_opts=opts.LineStyleOpts(
                        color="#ddd", width=1, type_="dashed"
                    )
                )
            )
        }
        
        # 为每个线图设置全局选项
        for line in lines:
            line.set_global_opts(**global_opts)
            grid.add(
                line,
                grid_opts=opts.GridOpts(
                    pos_left="5%", 
                    pos_right="5%", 
                    pos_bottom="15%",
                    pos_top="15%"
                )
            )
        
        # 为散点图设置全局选项
        effect_scatter.set_global_opts(**global_opts)
        grid.add(
            effect_scatter,
            grid_opts=opts.GridOpts(
                pos_left="5%", 
                pos_right="5%", 
                pos_bottom="15%",
                pos_top="15%"
            )
        )
        
        return grid
    
    def visualize_trajectory_from_csv(self, csv_file, save_path="uwb_trajectory_animation.html"):
        """
        从CSV文件创建轨迹动画并保存
        
        Args:
            csv_file: CSV文件路径
            save_path: 保存文件路径
        """
        # 加载轨迹数据
        user_trajectories = self.load_trajectory_data(csv_file)
        
        # 确定最大帧数
        max_frames = max([len(trajectory) for trajectory in user_trajectories.values()])
        
        # 创建时间轴
        timeline = Timeline(
            init_opts=opts.InitOpts(
                width="1200px", 
                height="800px", 
                theme=ThemeType.MACARONS,
                page_title="UWB用户轨迹可视化"
            )
        )
        
        timeline.add_schema(
            play_interval=300,
            is_auto_play=True,
            is_loop_play=True,
            is_rewind_play=False,
            is_timeline_show=True,
            pos_left="center",
            pos_bottom="5%",
            label_opts=opts.LabelOpts(
                is_show=True,
                color="#666",
                font_size=12
            )
            # 移除 control_style_opts 相关配置
        )
        
        # 为每一帧创建图表
        for frame_idx in range(max_frames):
            frame = self.create_frame(
                user_trajectories, 
                frame_idx, 
                f"{self.title} - 时间帧 {frame_idx+1}/{max_frames}"
            )
            timeline.add(frame, f"帧{frame_idx+1}")
        
        # 渲染并保存
        timeline.render(save_path)
        print(f"轨迹动画已保存至: {save_path}")
        
        return timeline

# 使用示例
if __name__ == "__main__":
    visualizer = TrajectoryVisualizer("UWB用户移动轨迹可视化")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file = os.path.join(current_dir, "P6_Trajectory.csv")
    timeline = visualizer.visualize_trajectory_from_csv(csv_file)