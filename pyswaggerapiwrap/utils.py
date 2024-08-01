"""
all utils of the pyswaggerapiwrap
"""

from copy import deepcopy

import pandas as pd  # pylint: disable=import-error
import requests  # pylint: disable=import-error

from pyswaggerapiwrap.additional_apis import AdditionalAPISContainer


def add_additional_apis_to_df(routes_df: pd.DataFrame):
    """
    Adds additional APIs to the routes DataFrame based on the ADDITIONAL_APIS configuration.

    Parameters:
    - routes_df: DataFrame containing the existing routes.

    Returns:
    - A new DataFrame with additional APIs included.
    """
    # Create a deep copy of the routes DataFrame to avoid modifying the original DataFrame
    routes_df_2 = deepcopy(routes_df)

    # Iterate over each additional API configuration
    for additional_api in AdditionalAPISContainer.ADDITIONAL_APIS.values():
        # Find the row that matches the original route and method
        new_api_df = deepcopy(
            routes_df_2[
                (routes_df_2["route"] == additional_api.original_route)
                & (routes_df_2["method"] == additional_api.method)
            ].iloc[0]
        )

        # Update the route and remove fixed route parameters
        new_api_df["route"] = additional_api.new_route
        new_api_df["parameters"] = [
            param
            for param in new_api_df["parameters"]
            if param["name"] not in list(additional_api.fixed_route_params.keys())
        ]

        # Append the new API to the DataFrame
        routes_df_2 = pd.concat([routes_df_2, pd.DataFrame(new_api_df).T], axis=0)

    # Reset the index of the DataFrame
    routes_df_2.reset_index(inplace=True, drop=True)

    return routes_df_2


def find_swagger_json(base_url):
    """
    Attempts to find the Swagger JSON file at various common paths.

    Parameters:
    - base_url: The base URL where the Swagger JSON might be located.

    Returns:
    - The Swagger JSON as a dictionary if found, otherwise None.
    """
    # List of common paths where the Swagger JSON might be located
    common_paths = [
        "/swagger.json",
        "/v2/swagger.json",
        "/api/swagger.json",
        "/docs/swagger.json",
    ]

    # Check each common path for the Swagger JSON
    for path in common_paths:
        url = base_url.rstrip("/") + path
        try:
            response = requests.get(url)
            if (
                response.status_code == 200
                and response.headers["Content-Type"] == "application/json"
            ):
                print(f"Found Swagger JSON at: {url}")
                return response.json()
        except requests.RequestException as error:
            print(f"Error accessing {url}: {error}")

    print("Swagger JSON not found.")
    return None


def get_swagger_df(swagger_json):
    """
    Converts the Swagger JSON into a DataFrame of API routes and their details.

    Parameters:
    - swagger_json: The Swagger JSON as a dictionary.

    Returns:
    - A DataFrame containing API route information.
    """
    paths = swagger_json.get("paths", {})
    routes_data = []

    # Extract route information from the Swagger JSON
    for path, methods in paths.items():
        for method, details in methods.items():
            parameters = details.get("parameters", [])
            route = {
                "api_type": path.split("/")[1],
                "route": path,
                "method": method.upper(),
                "parameters": [
                    {
                        "name": param.get("name"),
                        "param_type": param.get("schema", {}).get("type")
                        or param.get("type"),
                        "is_required": param.get("required", False),
                        "in": param.get("in", False),
                    }
                    for param in parameters
                ],
            }
            routes_data.append(route)

    # Create a DataFrame from the extracted route data
    routes_df = pd.DataFrame(routes_data)
    return routes_df
