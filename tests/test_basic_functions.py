"""
Test base functions and classes
"""

from typing import Dict

import pandas as pd

from pyswaggerapiwrap.api_filter import APIDataFrameFilter
from pyswaggerapiwrap.api_route import APIRoute
from pyswaggerapiwrap.http_client import HttpClient

ENDPOINT = "https://petstore.swagger.io/v2"
AUTH_TOKEN = "special-key"

HTTP_CLIENT_OBJ = HttpClient(base_url=ENDPOINT, auth_token=AUTH_TOKEN)
ROUTES_DICT = HTTP_CLIENT_OBJ.get_routes_df(swagger_route="/swagger.json")
API_FILTER = APIDataFrameFilter(ROUTES_DICT)


def test_get_swagger_dataframe():
    """
    Check if the routes df is generated
    :return:
    """
    routes_dict_2 = HTTP_CLIENT_OBJ.get_routes_df(swagger_route="/swagger.json")
    print(isinstance(routes_dict_2, pd.DataFrame))
    assert isinstance(routes_dict_2, pd.DataFrame)
    assert routes_dict_2.shape[0] > 0


def test_api_filter():
    """

    :return:
    """
    api_filter_2 = APIDataFrameFilter(ROUTES_DICT)
    assert api_filter_2.df_object.shape[0] > 0


def test_attribute_indexing():
    """

    :return:
    """

    api_selected = API_FILTER.store.get_inventory

    assert isinstance(api_selected, APIRoute)


def test_filter_method():
    """

    :return:
    """

    df_result = API_FILTER.filter(method="GET", route_pattern="find", api_type="pet")
    assert isinstance(df_result, pd.DataFrame)
    assert df_result.shape[0] > 0


def test_run_api():
    """

    :return:
    """

    data = API_FILTER.pet.get_with_petId.run(http_client=HTTP_CLIENT_OBJ, petId=1)
    assert isinstance(data, Dict)
    assert len(list(data.keys())) > 0
