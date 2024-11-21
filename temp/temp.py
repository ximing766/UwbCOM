import tkinter as tk
from dash import Dash, html, dash_table, dcc
import pandas as pd
import plotly.express as px

class DashApp:
    def __init__(self, external_stylesheets=None):
        self.external_stylesheets = external_stylesheets if external_stylesheets else ['https://codepen.io/chriddyp/pen/bWLwgP.css'] 
        self.app = Dash(external_stylesheets=self.external_stylesheets)
        self.setup_layout()

    def setup_layout(self):
        df = pd.read_csv('data/speed_95d.csv', sep=',', header=0, usecols=[1])
        df['Row'] = df.index + 1

        self.app.layout = html.Div([
            html.Div(children='My App in Dash', style={'width': '80%', 'margin': '0 auto', 'padding': '20px'}),
            dash_table.DataTable(
                data=df.to_dict('records'), 
                page_size=10,
                columns=[{'name': i, 'id': i} for i in df.columns],
                style_cell={'textAlign': 'center'},  
                style_data={'whiteSpace': 'normal'},  
                style_table={'overflowX': 'auto'}  
            ), 
            dcc.Graph(
                figure=px.line(df, x='Row', y=df.columns[0], title='Speed Over Time', 
                               labels={'value': 'Speed', 'index': 'Row'}, 
                               width=800, height=600)  
            )  
        ])

    def run(self, debug=False):
        self.app.run(debug=debug)

def start_dash_app():
    app = DashApp()
    app.run(debug=True)

if __name__ == '__main__':
    root = tk.Tk()
    root.title("Tkinter with Dash")
    root.geometry("300x200")

    # 创建一个按钮，点击时打开Dash应用
    open_button = tk.Button(root, text="Open Dash App", command=start_dash_app)
    open_button.pack(pady=20)

    root.mainloop()