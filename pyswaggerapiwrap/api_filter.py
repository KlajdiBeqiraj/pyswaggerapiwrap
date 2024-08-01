"""
Api Filter
"""

from __future__ import annotations

from copy import deepcopy

import pandas as pd

from pyswaggerapiwrap.api_route import APIRoute


class APIDataFrameFilter:
    """
    A class to filter and manage API routes within a DataFrame.

    Attributes:
        df_object (pd.DataFrame): The DataFrame containing API route information.
    """

    def __init__(self, dataframe: pd.DataFrame):
        """
        Initialize the APIDataFrameFilter with a DataFrame.

        Args:
            dataframe (pd.DataFrame): The DataFrame containing API route data.
        """
        self.df_object = deepcopy(dataframe)
        # Add 'api_route' column if it does not exist, converting rows to APIRoute objects.
        if "api_route" not in self.df_object.columns:
            self.df_object["api_route"] = self.df_object.apply(
                lambda row: APIRoute.from_dict(dict(row)), axis=1
            )

        unique_routes = self.df_object["api_type"].unique()

        if len(unique_routes) > 1:
            # Create sub-filter objects for each unique API type.
            for route in unique_routes:
                try:
                    setattr(
                        self,
                        route,
                        APIDataFrameFilter(
                            self.df_object[self.df_object["api_type"] == route]
                        ),
                    )
                except ValueError:
                    continue
        else:
            # Create attributes based on routes and methods if only one API type is present.
            for i, route in enumerate(self.df_object["route"]):
                param_name = self.df_object.iloc[i].method.lower() + route.replace(
                    f"/{self.df_object.iloc[i].api_type}", ""
                ).replace("/", "_")
                param_name = param_name.replace("{", "with_").replace("}", "")
                try:
                    setattr(self, param_name, self.df_object.iloc[i].api_route)
                except ValueError:
                    continue

    def __getattr__(self, name):
        """
        Access attributes dynamically. Raise AttributeError if the attribute does not exist.

        Args:
            name (str): The name of the attribute to access.

        Returns:
            Any: The value of the attribute.

        Raises:
            AttributeError: If the attribute is not found.
        """
        if name in self.__dict__:
            return self.__dict__[name]
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'"
        )

    @staticmethod
    def _filter_to_api_routes(filtered_df):
        """
        Convert filtered DataFrame to a list of APIRoute objects.

        Args:
            filtered_df (pd.DataFrame): The filtered DataFrame.

        Returns:
            list: A list of APIRoute objects.
        """
        return filtered_df["api_route"].tolist()

    @staticmethod
    def _create_new_instance(filtered_df):
        """
        Create a new instance of APIDataFrameFilter with a filtered DataFrame.

        Args:
            filtered_df (pd.DataFrame): The filtered DataFrame.

        Returns:
            APIDataFrameFilter: A new instance of APIDataFrameFilter.
        """
        return APIDataFrameFilter(filtered_df)

    @property
    def api_types(self):
        """
        Get all unique API types present in the DataFrame.

        Returns:
            tuple: A tuple of unique API types.
        """
        return tuple(self.df_object["api_type"].unique())

    @property
    def methods(self):
        """
        Get all unique HTTP methods present in the DataFrame.

        Returns:
            tuple: A tuple of unique HTTP methods.
        """
        return tuple(self.df_object["method"].unique())

    def filter(
        self,
        api_type=None,
        method=None,
        route_pattern=None,
        return_api_routes: bool = False,
    ):
        """
        Apply multiple filters to the DataFrame and return the filtered result.

        Args:
            api_type (Optional[str]): Filter by API type.
            method (Optional[str]): Filter by HTTP method.
            route_pattern (Optional[str]): Filter by route pattern.
            return_api_routes (bool): If True, return a list of
            APIRoute objects; otherwise, return a DataFrame.

        Returns:
            pd.DataFrame or list: The filtered DataFrame or
            list of APIRoute objects based on return_api_routes.
        """
        filtered_df = self.df_object

        if api_type:
            filtered_df = filtered_df[filtered_df["api_type"] == api_type]
        if method:
            filtered_df = filtered_df[filtered_df["method"] == method]
        if route_pattern:
            filtered_df = filtered_df[
                filtered_df["route"].str.contains(route_pattern, case=False)
            ]

        if return_api_routes:
            return self._filter_to_api_routes(filtered_df)

        return filtered_df

    @property
    def api_routes(self):
        """
        Get all APIRoute objects in the current DataFrame.

        Returns:
            list: A list of APIRoute objects.
        """
        return self._filter_to_api_routes(self.df_object)

    def get_api(
        self, route: str, method: str, return_api_route: bool = True
    ) -> None | APIRoute:
        """
        Extract a specific API from the
        DataFrame based on its route and method.

        Args:
            route (str): The exact route of the API.
            method (str): The HTTP method of the API.
            return_api_route (bool): If True, return only
            the api_route object; otherwise, return the full row.

        Returns:
            None or APIRoute: An APIRoute object if
            found and return_api_route is True, otherwise None.
            If return_api_route is False, returns
            the DataFrame row instead.
        """
        filtered = self.df_object[
            (self.df_object["route"] == route) & (self.df_object["method"] == method)
        ]
        if len(filtered) == 1:
            if return_api_route:
                return filtered["api_route"].iloc[0]

            return filtered.iloc[0]
        if len(filtered) > 1:
            raise ValueError(
                f"Multiple APIs found for route '{route}' and method '{method}'"
            )

        return None

    def __str__(self):
        """
        Return a string representation of the DataFrame.

        Returns:
            str: The string representation of the DataFrame.
        """
        return self.df_object.__str__()

    def __repr__(self):
        """
        Return a detailed string representation
        of the DataFrame for debugging.

        Returns:
            str: The detailed string representation
            of the DataFrame.
        """
        return self.df_object.__repr__()

    # pylint: disable=C0415
    def get_additional_api(self, key):
        """
        Retrieve an additional API based on a key
        from AdditionalAPISContainer.

        Args:
            key (str): The key of the additional API.

        Returns:
            None or APIRoute: The APIRoute object if
            found; otherwise, None.
        """
        from pyswaggerapiwrap.additional_apis import AdditionalAPISContainer

        if key in AdditionalAPISContainer.ADDITIONAL_APIS:
            route = AdditionalAPISContainer.ADDITIONAL_APIS[key].new_route
            method = AdditionalAPISContainer.ADDITIONAL_APIS[key].method
            return self.get_api(route=route, method=method)
        return None
