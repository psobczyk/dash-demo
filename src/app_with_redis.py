"""
Run this app with `python3 src/app_with_redis.py` and
visit http://127.0.0.1:8050/ in your web browser.

"""

import os
import time
import pandas as pd
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
from flask_caching import Cache
import plotly.express as px


app = Dash(__name__, assets_folder="../assets")

server = app.server

CACHE_CONFIG = {
    # try 'FileSystemCache' if you don't want to setup redis
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': os.environ.get('REDIS_URL', 'redis://localhost:6379')
}
cache = Cache()
cache.init_app(app.server, config=CACHE_CONFIG)


# Loading data
with open(
    "data/raw_data/ewp_dsh_zgony_po_szczep_20220127.csv",
    encoding="utf8",
    errors="ignore",
) as f:
    df = pd.read_csv(f, sep=";")


# App layout
app.layout = html.Div(
    children=[
        html.H1(children="Zgony na Covid a przyjęte dawki szczepień"),
        html.Div(
            children="""
        Aplikacja napisana w Dashu
    """
        ),
        html.Div(
            [
                html.H3(children="Płeć", className="card"),
                dcc.Dropdown(
                    df["plec"].unique(),
                    df["plec"].unique(),
                    id="gender-selection",
                    multi=True,
                ),
            ]
        ),
        html.Br(),
        html.Div(
            [
                html.H3(children="Wiek", className="card"),
                dcc.RangeSlider(
                    min=1,
                    max=max(df.wiek),
                    value=[30, 80],
                    id="age-selection",
                ),
            ]
        ),
        html.Div(dcc.Graph(id="chart")),
        # signal value to trigger callbacks
        dcc.Store(id='signal')
    ]
)


# perform expensive computations in this "global store"
# these computations are cached in a globally available
# redis memory store which is available across processes
# and for all time.
@cache.memoize()
def global_store(value):
    gender = value['gender']
    age = value['age']
    # "dlugie obliczenia"
    time.sleep(3)
    tmp = df[df["plec"].isin(gender)]
    tmp = tmp[tmp["wiek"] <= age[1]]
    tmp = tmp[tmp["wiek"] >= age[0]]
    tmp = (
        tmp.groupby("dawka_ost")
            .agg({"liczba_zaraportowanych_zgonow": sum})
            .reset_index()
    )
    return tmp


@app.callback(Output('signal', 'data'),
              [Input("gender-selection", "value"), Input("age-selection", "value")])
def compute_value(selected_gender_value, age_selection_value):
    global_store({'gender': selected_gender_value,
                  'age': age_selection_value})

    return {'gender': selected_gender_value,
            'age': age_selection_value}


@app.callback(
    Output("chart", "figure"),
    Input('signal', 'data'),
)
def update_graph(value):
    """
    Updates the plot according to the selected values

    :param selected_gender_value:
    :param age_selection_value:
    :return: updated plotly figure
    """
    filtered_dataframe = global_store(value)

    fig = px.bar(
        filtered_dataframe,
        x="dawka_ost",
        y="liczba_zaraportowanych_zgonow",
        color="dawka_ost",
        title="Zgony według zaszczepienia",
        labels={
            "dawka_ost": "Zaszczepienie",
            "liczba_zaraportowanych_zgonow": "Liczba zgonów",
        },
    )

    fig.update_layout(barmode="overlay")

    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
