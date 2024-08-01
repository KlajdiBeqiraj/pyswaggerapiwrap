"""
Additional apis classes
"""

from copy import copy
from typing import Any, Dict

from pydantic import BaseModel, Field


class AdditionalAPI(BaseModel):
    """
    Represents an additional API with a route and method, including optional parameters.

    Attributes:
        original_route (str): The original route template for the API.
        method (str): The HTTP method used for the API (e.g., GET, POST).
        fixed_route_params (dict): Parameters to replace in the original route.
        new_route (str): The computed route with parameters applied.
    """

    original_route: str = Field(..., description="The original route.")
    method: str = Field(..., description="Method used for the API.")
    fixed_route_params: dict = Field(..., description="The parameters to set.")
    new_route: str = Field(None, description="The new route.")

    def __init__(self, **data: Any):
        """
        Initialize the AdditionalAPI instance and compute the new route.

        Args:
            **data (Any): The initial data to initialize the model.
        """
        super().__init__(**data)
        self.new_route = self.get_new_route()

    def get_new_route(self) -> str:
        """
        Compute the new route by replacing placeholders in the original route with fixed parameters.

        Returns:
            str: The route with parameters applied.
        """
        route_with_params = copy(self.original_route)
        for key_param in self.fixed_route_params:
            route_with_params = route_with_params.replace(
                "{" + f"{key_param}" + "}", str(self.fixed_route_params[key_param])
            )

        return route_with_params

    def __str__(self):
        """
        Return a string representation of the AdditionalAPI instance.

        Returns:
            str: A string representation of the instance attributes.
        """
        return (
            f"\n\toriginal_route={self.original_route}\n"
            f"\tnew_route={self.new_route}\n"
            f"\tmethod={self.method}\n"
        )

    def __repr__(self):
        """
        Return a detailed string representation for debugging purposes.

        Returns:
            str: A detailed string representation of the instance.
        """
        return self.__str__()


class AdditionalAPISContainer:
    """
    A container for managing additional APIs.

    Attributes:
        ADDITIONAL_APIS (dict): A dictionary to store additional APIs by name.
    """

    ADDITIONAL_APIS: Dict = {}

    @staticmethod
    def add_additional_api(new_api: AdditionalAPI, name: str):
        """
        Add a new API to the container.

        Args:
            new_api (AdditionalAPI): The API to add.
            name (str): The name under which to store the API.
        """
        AdditionalAPISContainer.ADDITIONAL_APIS.update({name: new_api})

    @classmethod
    def get_additional_apis_name(cls):
        """
        Retrieve the names of all additional APIs in the container.

        Returns:
            list: A list of names of all additional APIs.
        """
        return list(cls.ADDITIONAL_APIS)
