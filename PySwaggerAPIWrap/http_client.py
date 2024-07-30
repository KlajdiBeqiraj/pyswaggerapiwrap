from typing import Optional

import requests
from PySwaggerAPIWrap.utils import get_swagger_df, find_swagger_json


class HttpClient:
    def __init__(self, base_url: str, auth_token: str):
        self.base_url = base_url
        self.auth_token = auth_token

    def _get_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.auth_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def get(self, route: str, request_data=None, timeout: int = 5) -> dict:
        if request_data is None:
            request_data = dict()
        url = f"{self.base_url}{route}"

        headers = self._get_headers()
        response = requests.get(url, headers=headers, params=request_data, timeout=timeout, verify=False)
        response.raise_for_status()
        return response.json()

    def post(self, route: str, request_data=None, timeout: int = 5) -> dict:
        if request_data is None:
            request_data = dict()
        url = f"{self.base_url}{route}"
        headers = self._get_headers()
        response = requests.post(url, headers=headers, json=request_data, timeout=timeout, verify=False)
        response.raise_for_status()
        return response.json()

    def get_swagger_info(self, route: Optional[str] = None):
        if route is None:
            route = find_swagger_json(self.base_url)
        try:
            response = self.get(route)
            return response
        except requests.exceptions.RequestException as e:
            print(f'Error accessing {route}: {e}')

    def get_routes_df(self, swagger_route: Optional[str] = None):
        routes_dict = self.get_swagger_info(route=swagger_route)
        return get_swagger_df(routes_dict)

