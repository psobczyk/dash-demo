"""
Testing simple filtering function

"""
from app_with_redis import filter_age_gender


def test_male_data(example_covid_data):  # pylint: disable=W0621
    """

    :param example_covid_data:
    :return:
    """
    df_covid = filter_age_gender(example_covid_data, age=None, gender=["M"])

    assert len(df_covid["plec"].unique()) == 1


def test_age_date(example_covid_data):  # pylint: disable=W0621
    """

    :param example_covid_data:
    :return:
    """
    df_covid = filter_age_gender(example_covid_data, age=[55, 60], gender=None)

    assert len(df_covid["wiek"].unique()) <= 6
