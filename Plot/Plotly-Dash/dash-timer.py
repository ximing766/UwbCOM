import dash
from dash import html, dcc, dash_table
import pandas as pd
from dash.dependencies import Input, Output

# 假设这是你的初始DataFrame
df = pd.DataFrame({
    'Column1': [1, 2, 3],
    'Column2': [4, 5, 6]
})

app = dash.Dash(__name__)

app.layout = html.Div([
    dash_table.DataTable(
        id='table',  # 为表格设置id
        data=df.to_dict('records'),
        columns=[{'name': i, 'id': i} for i in df.columns],
        style_cell={'textAlign': 'center'},
        style_data={'whiteSpace': 'normal'},
        style_table={'overflowX': 'auto'}
    ),
    dcc.Interval(
        id='interval-component',
        interval=1*1000,  # 每1秒刷新
        n_intervals=0
    )
])

@app.callback(
    Output('table', 'data'),  # 更新表格的数据
    [Input('interval-component', 'n_intervals')]  # 监听Interval组件的n_intervals
)
def update_table(n):
    global df  # 声明df为全局变量
    # 这里模拟DataFrame的动态更新
    # 例如，我们可以添加一个新行
    new_row = {'Column1': len(df) + 1, 'Column2': len(df) + 4}
    df = df.append(new_row, ignore_index=True)
    return df.to_dict('records')

if __name__ == '__main__':
    app.run_server(debug=True)