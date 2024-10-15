import dash
from dash import dcc, html
from dash.dependencies import Input, Output,State
import plotly.graph_objects as go

class Scatter3DPlotter:
    def __init__(self, coords):
        self.coords = coords
        self.fig = self.create_figure()

    def create_figure(self):
        x_coords = [coord[0] for coord in self.coords]
        y_coords = [coord[1] for coord in self.coords]
        z_coords = [coord[2] for coord in self.coords]

        self.fig = go.Figure(data=[go.Scatter3d(
            x=x_coords,
            y=y_coords,
            z=z_coords,
            mode='markers',
            marker=dict(
                size=5,
                color='blue',
                opacity=0.8
            )
        )])

        self.fig.update_layout(
            title='3D Scatter Plot',
            scene=dict(
                xaxis_title='X Axis',
                yaxis_title='Y Axis',
                zaxis_title='Z Axis'
            ),
            margin=dict(
                l=0,
                r=0,
                b=0,
                t=0
            )
        )

        return self.fig

    def add_point(self, new_point):
        self.coords.append(new_point)
        new_trace = go.Scatter3d(
            x=[self.coords[-1][0]],
            y=[self.coords[-1][1]],
            z=[self.coords[-1][2]],
            mode='markers',
            marker=dict(
                size=5,
                color='blue',
                opacity=0.8
            )
        )
        self.fig.add_trace(new_trace)
        self.fig.update_layout()

    def update_point(self, index, new_point):
        if index < 0 or index >= len(self.coords):
            raise IndexError("Index out of range")
        self.coords[index] = new_point
        self.fig.data[index].x = [new_point[0]]
        self.fig.data[index].y = [new_point[1]]
        self.fig.data[index].z = [new_point[2]]
        self.fig.update_layout()

app = dash.Dash(__name__)
plotter = Scatter3DPlotter([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

app.layout = html.Div([
    dcc.Graph(id='live-update-graph', figure=plotter.fig),
    dcc.Input(id='x-input', type='number', value=0),
    dcc.Input(id='y-input', type='number', value=0),
    dcc.Input(id='z-input', type='number', value=0),
    html.Button('Add Point', id='add-point-button', n_clicks=0),
    dcc.Input(id='index-input', type='number', value=0),
    html.Button('Update Point', id='update-point-button', n_clicks=0)
])

@app.callback(
    Output('live-update-graph', 'figure'),
    [Input('add-point-button', 'n_clicks')],
    [State('x-input', 'value'),
     State('y-input', 'value'),
     State('z-input', 'value')]
)
def add_point(n_clicks, x, y, z):
    if n_clicks > 0:
        plotter.add_point([x, y, z])
    return plotter.fig

@app.callback(
    Output('live-update-graph', 'figure'),
    [Input('update-point-button', 'n_clicks')],
    [State('index-input', 'value'),
     State('x-input', 'value'),
     State('y-input', 'value'),
     State('z-input', 'value')]
)
def update_point(n_clicks, index, x, y, z):
    if n_clicks > 0:
        plotter.update_point(int(index), [x, y, z])
    return plotter.fig

if __name__ == '__main__':
    app.run_server(debug=True)