"""
Run this app with `python3 src/app_with_state.py` and
visit http://127.0.0.1:8050/ in your web browser.

"""

import time
from dash import Dash, html, dcc, dash_table  # type: ignore
from dash.dependencies import Input, Output  # type: ignore
import plotly.express as px  # type: ignore
import pandas as pd  # type: ignore

app = Dash(__name__, assets_folder="../assets")

# źródło danych
# szczepienia.pzh.gov.pl/analiza-ryzyka-zgonu-wsrod-zaszczepionych-i-niezaszczepionych
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
        html.Div([dcc.Checklist(id="select_columns")]),
        html.Div(dcc.Graph(id="chart")),
        html.Div(dash_table.DataTable(id="tbl")),
        # dcc.Store przechowuje pośrednie wyniki obliczeń
        dcc.Store(id="dane-preprocessing"),
    ]
)


@app.callback(
    Output("dane-preprocessing", "data"),
    [Input("gender-selection", "value"), Input("age-selection", "value")],
)
def clean_data(selected_gender_value, age_selection_value):
    """

    :param selected_gender_value:
    :param age_selection_value:
    :return:
    """
    tmp = df.loc[  # pylint: disable=E1101
        df.loc[:, "plec"].isin(selected_gender_value), :  # pylint: disable=E1101
    ]
    tmp = tmp[tmp.loc[:, "wiek"] <= age_selection_value[1]]
    tmp = tmp[tmp.loc[:, "wiek"] >= age_selection_value[0]]
    tmp = (
        tmp.groupby("dawka_ost")
        .agg({"liczba_zaraportowanych_zgonow": sum})
        .reset_index()
    )
    # "dlugie obliczenia"
    time.sleep(3)

    return tmp.to_json(date_format="iso", orient="split")


@app.callback(
    [Output("select_columns", "value"), Output("select_columns", "options")],
    Input("dane-preprocessing", "data"),
)
def update_available_columns(jsonified_cleaned_data):
    """

    :param jsonified_cleaned_data:
    :return:
    """
    df_preprocessed = pd.read_json(jsonified_cleaned_data, orient="split")

    return df_preprocessed.columns, df_preprocessed.columns


@app.callback(
    [Output("chart", "figure"), Output("tbl", "data")],
    [Input("dane-preprocessing", "data"), Input("select_columns", "value")],
)
def update_graph(jsonified_cleaned_data, selected_columns):
    """
    Updates the plot according to the selected values

    :param selected_gender_value:
    :param age_selection_value:
    :return: updated plotly figure
    """
    df_preprocessed = pd.read_json(jsonified_cleaned_data, orient="split")

    fig = px.bar(
        df_preprocessed,
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

    return fig, df_preprocessed[selected_columns].to_dict("rows")


if __name__ == "__main__":
    app.run_server(debug=True)
