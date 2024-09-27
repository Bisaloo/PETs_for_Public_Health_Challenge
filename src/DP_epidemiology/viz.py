import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from datetime import datetime
import plotly.express as px
import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime
import opendp.prelude as dp

dp.enable_features("contrib", "floating-point", "honest-but-curious")

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from DP_epidemiology.utilities import *

from DP_epidemiology.hotspot_analyzer import hotspot_analyzer 
from DP_epidemiology.mobility_analyzer import mobility_analyzer
from DP_epidemiology.pandemic_stage_analyzer import pandemic_stage_analyzer
from DP_epidemiology.contact_matrix import get_age_group_count_map

def create_hotspot_dash_app(df:pd.DataFrame):
    cities = {
    "Medellin": (6.2476, -75.5658),
    "Bogota": (4.7110, -74.0721),
    "Brasilia": (-15.7975, -47.8919),
    "Santiago": (-33.4489, -70.6693)
    }
    app = dash.Dash(__name__)

    app.layout = html.Div([
        dcc.DatePickerSingle(
            id='start-date-picker',
            date='2019-01-01'
        ),
        dcc.DatePickerSingle(
            id='end-date-picker',
            date='2019-12-31'
        ),
        dcc.Slider(
            id='epsilon-slider',
            min=0,
            max=10,
            step=0.1,
            value=1,
            marks={i: str(i) for i in range(11)}
        ),
        dcc.Dropdown(
            id='city-dropdown',
            options=[{'label': city, 'value': city} for city in cities.keys()],
            value='Medellin'
        ),
        dcc.Graph(id='geo-plot')
    ])

    @app.callback(
        Output('geo-plot', 'figure'),
        [Input('start-date-picker', 'date'),
         Input('end-date-picker', 'date'),
         Input('epsilon-slider', 'value'),
         Input('city-dropdown', 'value')]
    )
    def update_graph(start_date, end_date, epsilon, city):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Filter data using hotspot_analyser
        output = hotspot_analyzer(df, start_date, end_date, city, epsilon)
        filtered_df = get_coordinates(output)

        # Plot using Plotly Express
        fig = px.scatter_geo(
            filtered_df,
            lat='Latitude',
            lon='Longitude',
            color='nb_transactions',
            size='nb_transactions',
            hover_name='merch_postal_code',
            hover_data={'merch_postal_code': True, 'nb_transactions': True, 'Latitude': False, 'Longitude': False},
            projection='mercator',
            title=f"Transaction Locations in {city} from {start_date.date()} to {end_date.date()} with epsilon={epsilon}",
            color_continuous_scale=px.colors.sequential.Plasma
        )

        # Center the map around the selected city
        fig.update_geos(
            center=dict(lat=cities[city][0], lon=cities[city][1]),
            projection_scale=2.5  # Zoom level
        )

        return fig

    return app