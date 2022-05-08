import pytest
import pandas as pd
from app_with_redis import filter_age_gender

@pytest.fixture
def example_covid_data():
    with open(
      "data/raw_data/ewp_dsh_zgony_po_szczep_20220127.csv",
      encoding="utf8",
      errors="ignore",
    ) as f:
        df = pd.read_csv(f, sep=";")
    return df


def test_male_data(example_covid_data):
    df = filter_age_gender(example_covid_data, age=None, gender=["M"])

    assert len(df["plec"].unique()) == 1


def test_age_date(example_covid_data):
    df = filter_age_gender(example_covid_data, age=[55, 60], gender=None)

    assert len(df["wiek"].unique()) <= 6
