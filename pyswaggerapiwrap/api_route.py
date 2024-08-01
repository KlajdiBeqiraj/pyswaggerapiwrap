"""
Api Route and Api params
"""

import keyword
from copy import deepcopy

import numpy as np

from pyswaggerapiwrap.http_client import HttpClient


class APIParam:
    """
    Represents a parameter in an API route.

    Attributes:
        known_types (dict): Mapping of parameter types
        to their corresponding Python types.
        name (str): The name of the parameter.
        param_type (str): The type of the parameter as a string (e.g., "string", "integer").
        is_required (bool): Whether the parameter is required.
        param_location (str): The location of the parameter ("path" or "query").
    """

    known_types = {
        "string": str,
        "integer": int,
        "float": float,
        "boolean": bool,
        "array": np.ndarray,
    }

    def __init__(
        self, name: str, param_type_str: str, is_required: bool, param_location: str
    ):
        """
        Initialize the APIParam instance.

        Args:
            name (str): The name of the parameter.
            param_type_str (str): The type of the parameter as a string.
            is_required (bool): Whether the parameter is required.
            param_location (str): The location of the parameter ("path" or "query").
        """
        self.name = name
        self.param_type = param_type_str
        self.is_required = is_required
        self.param_location = param_location

    @staticmethod
    def from_dict(dict_values: dict):
        """
        Create an APIParam instance from a dictionary.

        Args:
            dict_values (dict): Dictionary containing parameter data.

        Returns:
            APIParam: An instance of APIParam.
        """
        return APIParam(
            name=dict_values["name"],
            param_type_str=dict_values["param_type"],
            is_required=dict_values["is_required"],
            param_location=dict_values["in"],
        )

    def __str__(self):
        """
        Return a string representation of the APIParam instance.

        Returns:
            str: A string representation of the APIParam instance.
        """
        return (
            f"APIParam(name={self.name}, param_type={str(self.param_type)}, is_required={self.is_required}, "
            f"param_location={self.param_location})"
        )

    def validate(self, value):
        """
        Validate the value of the parameter against its
        type and requirement.

        Args:
            value (Any): The value to validate.

        Raises:
            ValueError: If the parameter is required but the
            value is None.
            TypeError: If the value does not match the
            expected type.
        """
        if self.is_required and value is None:
            raise ValueError(f"The parameter '{self.name}' is required.")
        if value is not None:
            expected_type = self.known_types.get(self.param_type)
            if expected_type is None:
                raise TypeError(
                    f"Unknown type '{self.param_type}' for parameter '{self.name}'."
                )
            if not isinstance(value, expected_type):
                raise TypeError(
                    f"The parameter '{self.name}' must be of type '{self.param_type}'."
                )


class APIRoute:
    """
    Represents an API route.

    Attributes:
        route (str): The route template.
        method (str): The HTTP method (e.g., "GET", "POST").
        parameters (list): List of APIParam objects defining
        the route parameters.
        route_type (str): The type of route extracted from the
        route path.
    """

    def __init__(self, route, method, parameters):
        """
        Initialize the APIRoute instance.

        Args:
            route (str): The route template.
            method (str): The HTTP method.
            parameters (list): List of parameters for the route.
        """
        self.route = route
        self.method = method
        self.parameters = self.define_params(parameters)
        self.route_type = route.split("/")[1]

        # Generate dynamic __call__ method for this route
        self.__call__ = None
        self.generate_call_method()
        self.run = self.__call__

    @staticmethod
    def define_params(params):
        """
        Create APIParam instances from a list of parameter
        dictionaries.

        Args:
            params (list): List of dictionaries containing
            parameter data.

        Returns:
            list: List of APIParam instances.
        """
        return [APIParam.from_dict(param) for param in params]

    @staticmethod
    def from_dict(dict_values):
        """
        Create an APIRoute instance from a dictionary.

        Args:
            dict_values (dict): Dictionary containing
            route data.

        Returns:
            APIRoute: An instance of APIRoute.
        """
        return APIRoute(
            route=dict_values["route"],
            method=dict_values["method"],
            parameters=dict_values["parameters"],
        )

    def __str__(self):
        """
        Return a string representation of the APIRoute instance.

        Returns:
            str: A string representation of the APIRoute instance.
        """
        str_params = "\n\t\t".join(str(param) for param in self.parameters)
        return (
            f"APIRoute(\n\troute={self.route}, \n\tmethod={self.method}, \n\tapi_type={self.route_type} "
            f"\n\tparameters=[\n\t\t{str_params}\n\t]\n)"
        )

    def __repr__(self):
        """
        Return a detailed string representation of the
        APIRoute instance for debugging.

        Returns:
            str: A detailed string representation of the
            APIRoute instance.
        """
        return self.__str__()

    def validate_params(self, route_params):
        """
        Validate route parameters against the expected parameters.

        Args:
            route_params (dict): Dictionary of route
            parameters to validate.

        Raises:
            ValueError: If unexpected or missing required
            parameters are found.
        """
        all_params = {param.name: param for param in self.parameters}

        for key, value in route_params.items():
            if key in all_params:
                all_params[key].validate(value)
            else:
                raise ValueError(f"Unexpected parameter: {key}")

        for param in self.parameters:
            if param.is_required and route_params.get(param.name) is None:
                raise ValueError(f"Missing required parameter: {param.name}")

    def run_api(
        self,
        http_client: HttpClient,
        route_params=None,
    ):
        """
        Execute the API call with the given parameters.

        Args:
            http_client (HttpClient): The HTTP client to use for making requests.
            route_params (Optional[dict]): Parameters to
            include in the route and query string.

        Returns:
            dict: The response from the API call.

        Raises:
            ValueError: If the HTTP method is not implemented.
        """
        self.validate_params(route_params or {})

        route_with_params: str = deepcopy(self.route)
        query_string = ""

        if route_params is not None:
            for param in self.parameters:
                if param.param_location == "path":
                    if param.name in route_params:
                        route_with_params = route_with_params.replace(
                            "{" + f"{param.name}" + "}", str(route_params[param.name])
                        )
                elif param.param_location == "query":
                    if param.name in route_params:
                        if query_string:
                            query_string += "&"
                        query_string += f"{param.name}={route_params[param.name]}"
        if query_string:
            route_with_params += f"?{query_string}"

        if self.method == "GET":
            return http_client.get(route=route_with_params)
        if self.method == "POST":
            return http_client.post(route=route_with_params)

        raise ValueError(f"Method {self.method} not yet implemented")

    def generate_call_method(self):
        """
        Generate a __call__ method dynamically based on
        the parameters.

        This method allows instances of APIRoute to be
        called like functions.
        """
        param_names = [param.name for param in self.parameters]

        safe_param_names = []
        for name in param_names:
            if keyword.iskeyword(name):
                safe_param_names.append(name + "_param")
            else:
                safe_param_names.append(name)

        params_str = ", ".join(safe_param_names)
        code = f"""def __call__(self, http_client: 'HttpClient', {params_str}):
        route_params = locals()
        route_params.pop('self')
        route_params.pop('http_client')
        return self.run_api(http_client=http_client, route_params=route_params)
    """
        exec(code, globals(), locals())
        setattr(self, "__call__", locals()["__call__"].__get__(self, APIRoute))

    def copy(self):
        """
        Create a copy of the APIRoute instance.

        Returns:
            APIRoute: A new APIRoute instance with
            the same attributes.
        """
        route, method, parameters = (
            deepcopy(self.route),
            deepcopy(self.method),
            deepcopy(self.parameters),
        )
        return APIRoute(route=route, method=method, parameters=parameters)
