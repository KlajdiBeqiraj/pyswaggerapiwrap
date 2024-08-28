"""
Http client
"""

import os
from io import BytesIO
from typing import Optional

import requests  # pylint: disable=import-error
from pydantic import BaseModel, Field
from requests_toolbelt import MultipartEncoder

from pyswaggerapiwrap.utils import find_swagger_json, get_swagger_df


class HttpClient(BaseModel):
    """
    A class to handle HTTP requests with authentication.
    """

    base_url: str = Field(..., description="Base route for APIs")
    auth_token: str = Field(..., description="Auth token")

    def _get_headers(self) -> dict:
        """
        Generate the headers required for the HTTP requests.

        Returns:
            dict: A dictionary containing the headers.
        """
        return {
            "Authorization": f"Bearer {self.auth_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    @property
    def headers(self):
        return self._get_headers()

    def get(self,
            route: str,
            request_data=None,
            timeout: int = 5,
            body: Optional[dict] = None,
            **kwargs
            ) -> dict:
        """
        Perform a GET request to the specified route.

        Args:
            kwargs: post kwargs
            body (dict): body of the request
            route (str): The route to append to the base URL for the request.
            request_data (Optional[dict]): Optional query parameters for the request.
            timeout (int): The timeout duration for the request in seconds.

        Returns:
            dict: The response JSON data.

        Raises:
            requests.exceptions.RequestException: If the request fails.
        """
        if request_data is None:
            request_data = {}
        url = f"{self.base_url}{route}"

        headers = self._get_headers()
        response = requests.get(
            url, headers=headers, params=request_data, timeout=timeout, verify=False,
            json=body, **kwargs
        )
        response.raise_for_status()
        return response.json()

    def post(self,
             route: str,
             request_data: Optional[dict] = None,
             timeout: int = 5,
             **kwargs,
             ) -> dict:
        """
        Perform a POST request to the specified route.

        Args:
            kwargs: post kwargs
            route (str): The route to append to the base URL for the request.
            request_data (Optional[dict]): Optional JSON body for the request.
            timeout (int): The timeout duration for the request in seconds.

        Returns:
            dict: The response JSON data.

        Raises:
            requests.exceptions.RequestException: If the request fails.
        """
        if request_data is None:
            request_data = {}
        url = f"{self.base_url}{route}"
        headers = self._get_headers()

        if "files" in kwargs:
            headers.pop('Content-Type', None)

        response = requests.post(
            url, headers=headers, json=request_data, timeout=timeout, verify=False, **kwargs
        )
        response.raise_for_status()
        return response.json()

    def get_swagger_info(self, route: Optional[str] = None):
        """
        Retrieve Swagger API information from the given route.

        Args:
            route (Optional[str]): The route to request Swagger information from.
                                   If None, it will attempt to find the Swagger JSON
                                   using the base URL.

        Returns:
            dict: The Swagger API information as a dictionary.

        Prints:
            str: An error message if the request fails.
        """
        if route is None:
            route = find_swagger_json(self.base_url)
        try:
            response = self.get(route)
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error accessing {route}: {e}")
            return None

    def get_routes_df(self, swagger_route: Optional[str] = None):
        """
        Get a DataFrame of API routes from Swagger information.

        Args:
            swagger_route (Optional[str]): The route to request Swagger information from.
                                           If None, it will use the default Swagger route.

        Returns:
            DataFrame: A DataFrame containing API routes information.
        """
        routes_dict = self.get_swagger_info(route=swagger_route)
        return get_swagger_df(routes_dict)

    def post_with_large_file_support(self,
                                     route: str,
                                     request_data: Optional[dict] = None,
                                     files_data: Optional[dict] = None,
                                     timeout: int = 5,
                                     **kwargs) -> dict:
        """
        Perform a POST request with support for file uploads using MultipartEncoder.

        Args:
            route (str): The route to append to the base URL for the request.
            request_data (Optional[dict]): Additional form data to send (equivalent to JSON data).
            files_data (Optional[dict]): A dictionary where keys are form field names and values are file paths.
            timeout (int): The timeout duration for the request in seconds.
            kwargs: Additional arguments for the requests.post method.

        Returns:
            dict: The response JSON data.

        Raises:
            requests.exceptions.RequestException: If the request fails.
        """
        # Initialize headers
        headers = self._get_headers()

        # Initialize form data
        if request_data is None:
            request_data = {}

        # Prepare the fields for MultipartEncoder
        fields = {**request_data}

        if files_data:
            for field_name, file in files_data.items():
                if isinstance(file, str):  # If it's a file path
                    fields[field_name] = (os.path.basename(file), open(file, 'rb'))
                elif isinstance(file, BytesIO):  # If it's a file-like object (e.g., BytesIO)
                    fields[field_name] = (field_name, file)
                else:
                    raise ValueError(f"Unsupported file type for field {field_name}")

        # Use MultipartEncoder for all file uploads
        encoder = MultipartEncoder(fields=fields)
        headers["Content-Type"] = encoder.content_type

        response = requests.post(
            f"{self.base_url}{route}",
            data=encoder,
            headers=headers,
            timeout=timeout,
            verify=False,  # Use SSL verification as needed
            **kwargs
        )

        response.raise_for_status()  # Raise an error for bad responses
        return response.json() if response.content else {}