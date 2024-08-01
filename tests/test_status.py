"""
test the saving and loading the status
"""

import os

from pyswaggerapiwrap.status import load_status, save_status
from tests.test_basic_functions import API_FILTER, HTTP_CLIENT_OBJ, ROUTES_DICT


def test_get_swagger_dataframe():
    """
    :return:
    """
    file_path = os.path.join("resources", "saved_data", "test_status.psw")

    # remove the previous status
    if os.path.exists(file_path):
        os.remove(file_path)

    # save the status
    save_status(file_path, http_client=HTTP_CLIENT_OBJ, routes_dict=ROUTES_DICT)

    # load the status
    new_api_filter, new_http_client = load_status(file_path)

    # compare the result
    data_original_api = API_FILTER.store.get_inventory.run(HTTP_CLIENT_OBJ)
    data_reloaded_api = new_api_filter.store.get_inventory.run(new_http_client)
    assert data_original_api == data_reloaded_api
