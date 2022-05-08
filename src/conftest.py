"""
Getting data for unit tests

"""
import pytest  # type: ignore
import pandas as pd  # type: ignore


@pytest.fixture(scope="session")
def example_covid_data():
    """

    :return:
    """
    with open(
        "data/raw_data/ewp_dsh_zgony_po_szczep_20220127.csv",
        encoding="utf8",
        errors="ignore",
    ) as file:
        df_covid = pd.read_csv(file, sep=";")
    return df_covid
