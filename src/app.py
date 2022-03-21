"""
Run this app with `python app.py` and
visit http://127.0.0.1:8050/ in your web browser.

"""

from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

app = Dash(__name__, assets_folder="../assets")

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
    ]
)


# decorator that enables reactivity
@app.callback(
    Output("chart", "figure"),
    [Input("gender-selection", "value"), Input("age-selection", "value")],
)
def update_graph(selected_gender_value, age_selection_value):
    """
    Updates the plot according to the selected values

    :param selected_gender_value:
    :param age_selection_value:
    :return: updated plotly figure
    """
    tmp = df[df["plec"].isin(selected_gender_value)]
    tmp = tmp[tmp["wiek"] <= age_selection_value[1]]
    tmp = tmp[tmp["wiek"] >= age_selection_value[0]]
    tmp = (
        tmp.groupby("dawka_ost")
        .agg({"liczba_zaraportowanych_zgonow": sum})
        .reset_index()
    )

    fig = px.bar(
        tmp,
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
