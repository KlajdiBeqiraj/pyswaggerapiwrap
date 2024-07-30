from __future__ import annotations

from PySwaggerAPIWrap import ADDITIONAL_APIS
from PySwaggerAPIWrap.api_route import APIRoute
import pandas as pd
import numpy as np


class APIDataFrameFilter:
    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe
        if 'api_route' not in self.df.columns:
            self.df['api_route'] = self.df.apply(lambda row: APIRoute.from_dict(dict(row)), axis=1)

        unique_routes = self.df['api_type'].unique()

        if len(unique_routes) > 1:
            for route in unique_routes:
                setattr(self, route, APIDataFrameFilter(self.df[self.df['api_type'] == route]))
        else:
            for i, route in enumerate(self.df["route"]):
                param_name = self.df.iloc[i].method.lower() + route.replace(f"/{self.df.iloc[i].api_type}", "").replace("/", "_")
                param_name = param_name.replace("{", "with_").replace("}", "")
                setattr(self, param_name, self.df.iloc[i].api_route)

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def _filter_to_api_routes(self, filtered_df):
        return filtered_df['api_route'].tolist()

    @staticmethod
    def _create_new_instance(filtered_df):
        return APIDataFrameFilter(filtered_df)

    @property
    def api_types(self):
        """
        Show all unique API types present in the dataframe.
        """
        return tuple(self.df['api_type'].unique())

    @property
    def methods(self):
        """
        Show all unique HTTP methods present in the dataframe.
        """
        return tuple(self.df['method'].unique())

    def filter(self, api_type=None, method=None, route_pattern=None, return_api_routes: bool = False):
        """
        Apply multiple filters at once.
        """
        filtered_df = self.df

        if api_type:
            filtered_df = filtered_df[filtered_df['api_type'] == api_type]
        if method:
            filtered_df = filtered_df[filtered_df['method'] == method]
        if route_pattern:
            filtered_df = filtered_df[filtered_df['route'].str.contains(route_pattern, case=False)]

        if return_api_routes:
            return self._filter_to_api_routes(filtered_df)
        else:
            return filtered_df

    @property
    def api_routes(self):
        """
        Return all APIRoute objects in the current dataframe.
        """
        return self._filter_to_api_routes(self.df)

    def get_api(self, route: str, method: str, return_api_route: str = True) -> None | APIRoute:
        """
        Extract a specific API from the DataFrame based on its route and method.

        :param route: The exact route of the API
        :param method: The HTTP method of the API
        :params return_api_route: if true return only the api_route object
        :return: An APIRoute object if found, None otherwise

        Args:
            return: api_route:
:        """
        filtered = self.df[(self.df['route'] == route) & (self.df['method'] == method)]
        if len(filtered) == 1:
            if return_api_route:
                return filtered['api_route'].iloc[0]
            else:
                return filtered.iloc[0]
        elif len(filtered) > 1:
            raise ValueError(f"Multiple APIs found for route '{route}' and method '{method}'")
        else:
            return None

    def __str__(self):
        return self.df.__str__()

    def __repr__(self):
        return self.df.__repr__()

    def get_additional_api(self, key):
        if key in ADDITIONAL_APIS:
            route = ADDITIONAL_APIS[key].new_route
            method = ADDITIONAL_APIS[key].method
            return self.get_api(route=route, method=method)
