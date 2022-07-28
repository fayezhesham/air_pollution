import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc, html, Input, Output, callback_context
import json


countries = json.load(open('countries.json', 'r'))
token = "pk.eyJ1IjoiZmF5ZXotaCIsImEiOiJja3kxc3N1azkwZXJnMnBsZzhkY3owY3NvIn0.bZf3aU9wAEx1mx4Vzbd0Xg"
color_sequence = ['#00FFFF', '#F0FFFF', '#89CFF0', '#0000FF', '#7393B3', '#0096FF', '#0047AB', '#6495ED', '#00FFFF', '#00008B', '#1434A4', '#7DF9FF', '#6082B6', '#3F00FF', '#5D3FD3', '#1F51FF', '#4169E1', '#0437F2']



def blank_fig():
    fig = go.Figure(go.Scatter(x=[], y = []))
    fig.update_layout(template = None,
                     plot_bgcolor="rgba( 0, 0, 0, 0)",
                     paper_bgcolor="rgba( 0, 0, 0, 0)",)
    fig.update_xaxes(showgrid = False, showticklabels = False, zeroline=False)
    fig.update_yaxes(showgrid = False, showticklabels = False, zeroline=False)

    return fig

config = {'displaylogo': False,
         'modeBarButtonsToAdd':['drawline',
                                'drawopenpath',
                                'drawclosedpath',
                                'drawcircle',
                                'drawrect',
                                'eraseshape'
                               ]}



coordinates = {1:{"lat": 0, "lon": 27.5085},
               2:{"lat": 28.0479, "lon": 85.6197},
               3:{"lat": 54.5260, "lon": 40.2551},
               4:{"lat": 44.5260, "lon": -105.2551},
               5:{"lat": -26.7832, "lon": -60.4915},
               6:{"lat": -22.7359, "lon": 140.0188}}



data=pd.read_csv('data_final.csv')
data_continent = pd.read_csv("continent_data.csv")

app = dash.Dash(__name__, update_title=None, suppress_callback_exceptions=True, meta_tags=[{'name': 'viewport','content': 'width=device-width, initial-scale=1.0'}])
server = app.server
app.title = 'Air Pollution'




app.layout = html.Div([
    html.Div([
        html.Div([
            html.P("Air Pollution Dashboard", id = "title")
        ], id = "header"),
        html.Div([
            html.Div([
                html.Button("The World", className = "button", id = "b1"),
                html.Button("Africa", className = "button", id = "b2"),
                html.Button("Asia", className = "button", id = 'b3'),
                html.Button("Europe", className = "button", id = "b4"),
                html.Button("North America", className = "button", id = "b5"),
                html.Button("South America", className = "button", id = "b6"),
                html.Button("Oceania", className = "button", id = "b7"),
            ], id = "buttons"),
            html.Div([
                dcc.Slider(
                id='year-slider',
                marks = {int(x):str(x) for x in data.sort_values('year')['year'].unique()},
                step=1,
                min=data['year'].min(),
                max=data['year'].max(),
                updatemode='mouseup',
                value=data['year'].max()
                ),
            ], id = "slider_container")
        ], id = "filters", className = "container"),
        html.Div([
            dcc.Graph(figure = blank_fig(), config = config, id = "bar_figure"),
        ], id = "bar_chart", className = "container"),
        html.Div([
            dcc.Graph(figure = blank_fig(), config = config, id = "map_figure"),
        ], id = "map", className = "container"),
        html.Div([
            dcc.Graph(figure = blank_fig(), config = config, id = "line_figure"),
        ], id = "line_chart", className = "container"),
        html.Div([
            dcc.Graph(figure = blank_fig(), config = config, id = "pie_figure"),
        ], id = "pie_chart", className = "container"),

    ], id = "main"),
    dcc.Store(id = "clicked-button")
], id = "layout")




@app.callback(
    [Output('b1', 'style'),
     Output('b2', 'style'),
     Output('b3', 'style'),
     Output('b4', 'style'),
     Output('b5', 'style'),
     Output('b6', 'style'),
     Output('b7', 'style'),
     Output('clicked-button', 'data')],
    [Input('b1', 'n_clicks'),
     Input('b2', 'n_clicks'),
     Input('b3', 'n_clicks'),
     Input('b4', 'n_clicks'),
     Input('b5', 'n_clicks'),
     Input('b6', 'n_clicks'),
     Input('b7', 'n_clicks')],
)
def change_style(b1, b2, b3, b4, b5, b6, b7):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0][0:2]
    styles = [None] * 7
    if changed_id[-1] == ".":
        styles[0] = {"background-color" : "#222222", "border": "1px solid white"}
    else:
        styles[int(changed_id[-1]) - 1] = {"background-color" : "#222222", "border": "1px solid white"}
    styles.append(changed_id)
    return styles



@app.callback(
    Output("map_figure", "figure"),
    [Input("year-slider", "value"),
     Input("clicked-button", 'data')]
)

def update_map(year, changed_id):
    dff = data[data["year"] == year]
    if changed_id[-1] == "." or changed_id[-1] == "1":
        dff = dff
        coordinate = {"lat": 20, "lon": 10}
        zoom = 1.15
    elif changed_id[-1] != "1" and changed_id[-1] != ".": 
        dff = dff[dff['continent code'] == int(changed_id[-1]) -1 ]
        coordinate = coordinates[int(changed_id[-1]) - 1]
        zoom = 2.1
    fig = px.choropleth_mapbox(dff, 
                           geojson=countries, 
                           locations="code", 
                           color= "air pollution",
                           featureidkey= "properties.iso_a3",
                           color_continuous_scale=["grey", "#527fc7", "blue"],
                           mapbox_style="dark",
                           zoom = zoom,
                           template = "plotly_dark",
                           custom_data=["country", "air pollution"]
    )

    fig.update_traces(
        hovertemplate="<br>".join([
            "Country:  <b>%{customdata[0]}</b>",
            "Air Pollution:  <b>%{customdata[1]:.3f}</b>",
        ]),
    )

    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, 
    mapbox_accesstoken = token,  
    mapbox_center = coordinate,
    dragmode= False,
    plot_bgcolor="rgba( 0, 0, 0, 0)",
    paper_bgcolor="rgba( 0, 0, 0, 0)",
    )
    return fig


@app.callback(
    Output("bar_figure", "figure"),
    [Input("year-slider", "value"),
    Input("clicked-button", 'data')]
)

def update_map(year, changed_id):
    if changed_id[-1] == "." or changed_id[-1] == "1":
        dff = data_continent[data_continent['year'] == year].sort_values('air pollution', ascending = False)

        fig = px.bar(dff, 
        x = "continent", 
        y = 'air pollution',
        color = 'air pollution',
        color_continuous_scale = ["grey", "#527fc7", "blue"],
        custom_data = ["continent", "air pollution"])

        fig.update_traces(
            hovertemplate="<br>".join([
                "Continent:  <b>%{customdata[0]}</b>",
                "Air Pollution:  <b>%{customdata[1]:.3f}</b>",
            ]),
        )

    elif changed_id[-1] != "1" and changed_id[-1] != ".": 
        dff = data[data['continent code'] == int(changed_id[-1]) -1 ]
        dff = dff[dff['year'] == year].sort_values('air pollution', ascending = False)

        fig = px.bar(dff, 
        x = 'country', 
        y = 'air pollution',
        color = 'air pollution',
        color_continuous_scale = ["grey", "#527fc7", "blue"],
        custom_data = ["country", "air pollution"])
        fig.update_traces(
        hovertemplate="<br>".join([
            "Country:  <b>%{customdata[0]}</b>",
            "Air Pollution:  <b>%{customdata[1]:.3f}</b>",
        ]),
        )


    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, 
    plot_bgcolor="rgba( 0, 0, 0, 0)",
    paper_bgcolor="rgba( 0, 0, 0, 0)",
    font = dict(color = "white")
    )
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='grey')

    return fig


@app.callback(
    Output('line_figure', 'figure'),
    Input('clicked-button', 'data')
)
def update_line(changed_id):
    if changed_id[-1] == "." or changed_id[-1] == "1":
        dff = data_continent

        fig = px.line(dff, 
        x = "year", 
        y = 'air pollution',
        color = 'continent',
        title = "Click on a continent to remove it, Double click to isolate it",
        custom_data = ["continent", "year", "air pollution"],
        color_discrete_sequence = color_sequence)

        fig.update_traces(
            hovertemplate="<br>".join([
                "Continent:  <b>%{customdata[0]}</b>",
                "Year:  <b>%{customdata[1]}</b>",
                "Air Pollution:  <b>%{customdata[2]:.3f}</b>",
            ]),
        )

    elif changed_id[-1] != "1" and changed_id[-1] != ".": 
        dff = data[data['continent code'] == int(changed_id[-1]) -1 ]

        fig = px.line(dff, 
        x = 'year', 
        y = 'air pollution',
        color = 'country',
        title = "Click on a country to remove it, Double click to isolate it",
        custom_data = ["country", "year", "air pollution"],
        color_discrete_sequence = color_sequence)

        fig.update_traces(
            hovertemplate="<br>".join([
                "Country:  <b>%{customdata[0]}</b>",
                "Year:  <b>%{customdata[1]}</b>",
                "Air Pollution:  <b>%{customdata[2]:.3f}</b>",
            ]),
        )


    fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0}, 
    plot_bgcolor="rgba( 0, 0, 0, 0)",
    paper_bgcolor="rgba( 0, 0, 0, 0)",
    font = dict(color = "white")
    )
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='grey')
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='grey')
    return fig



@app.callback(
    Output("pie_figure", "figure"),
    [Input("year-slider", "value"),
     Input("clicked-button", 'data')]
)

def update_pie(year, changed_id):
    dff = data[data['year'] == year]
    if changed_id[-1] == "." or changed_id[-1] == "1":
        dff = dff.groupby('air quality', as_index=False).count()
        dff = dff.rename(columns = {"country": "count"})

    elif changed_id[-1] != "1" and changed_id[-1] != ".":
        dff = dff[dff['continent code'] == int(changed_id[-1]) - 1]
        dff = dff.groupby('air quality', as_index=False).count()
        dff = dff.rename(columns = {"country": "count"})

    fig = px.pie(dff, 
    names = "air quality", 
    values = "count",
    hole = 0.65,
    title = "Air Quality Comparison",
    color = "air quality",
    color_discrete_map={"Excellent":"grey", "Very Good": "#6b7fa0", "Good": "#5f7fb2", "Bad": "#547fc3", "Very Bad": "#3958d8", "Poor": "blue"}
    )

    fig.update_layout(margin={"r":30,"t":30,"l":30,"b":30}, 
    plot_bgcolor="rgba( 0, 0, 0, 0)",
    paper_bgcolor="rgba( 0, 0, 0, 0)",
    font = dict(color = "white")
    )
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='grey')
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='grey')
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)