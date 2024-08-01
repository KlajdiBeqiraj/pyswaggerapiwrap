"""
Status class used to save and reload all the information needed to call the APIs
"""

import pickle

import pandas as pd

from pyswaggerapiwrap.api_filter import APIDataFrameFilter
from pyswaggerapiwrap.http_client import HttpClient


def save_status(file_path: str, http_client: HttpClient, routes_dict: pd.DataFrame):
    """
    function used to save the status
    :param http_client:
    :param routes_dict:
    :param file_path:
    :return:
    """
    status = {"routes_dict": routes_dict, "http_client": http_client}

    with open(file_path, "wb") as file:
        pickle.dump(status, file)


def load_status(file_path: str):
    """
    function  used to load from file the status
    :param file_path:
    :return:
    """
    with open(file_path, "rb") as file:
        python_object = pickle.load(file)

    api_filter = APIDataFrameFilter(python_object["routes_dict"])
    http_client = python_object["http_client"]

    return api_filter, http_client
