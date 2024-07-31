import numpy as np

from PySwaggerAPIWrap.http_client import HttpClient
from copy import deepcopy
import keyword


class APIParam:
    known_types = {
        "string": str,
        "integer": int,
        "float": float,
        "boolean": bool,
        "array": np.ndarray
    }

    def __init__(self, name: str, param_type_str: str, is_required: bool, param_location: str):
        self.name = name
        self.param_type = param_type_str
        self.is_required = is_required
        self.param_location = param_location  # path | query

    @staticmethod
    def from_dict(dict_values: dict):
        return APIParam(
            name=dict_values["name"],
            param_type_str=dict_values["param_type"],
            is_required=dict_values["is_required"],
            param_location=dict_values["in"]
        )

    def __str__(self):
        return (f"APIParam(name={self.name}, param_type={str(self.param_type)}, is_required={self.is_required}, "
                f"param_location={self.param_location})")

    def validate(self, value):
        if self.is_required and value is None:
            raise ValueError(f"The parameter '{self.name}' is required.")
        if value is not None:
            expected_type = self.known_types.get(self.param_type)
            if expected_type is None:
                raise TypeError(f"Unknown type '{self.param_type}' for parameter '{self.name}'.")
            if not isinstance(value, expected_type):
                raise TypeError(f"The parameter '{self.name}' must be of type '{self.param_type}'.")


class APIRoute:
    def __init__(self, route, method, parameters):
        self.route = route
        self.method = method
        self.parameters = self.define_params(parameters)
        self.route_type = route.split("/")[1]

        # generate dynamic __call__ method
        self.generate_call_method()
        self.run = self.__call__

    @staticmethod
    def define_params(params):
        return [APIParam.from_dict(param) for param in params]

    @staticmethod
    def from_dict(dict_values):
        return APIRoute(
            route=dict_values["route"],
            method=dict_values["method"],
            parameters=dict_values["parameters"],
        )

    def __str__(self):
        str_params = "\n\t\t".join(str(param) for param in self.parameters)
        return f"APIRoute(\n\troute={self.route}, \n\tmethod={self.method}, \n\tapi_type={self.route_type} \n\tparameters=[\n\t\t{str_params}\n\t]\n)"

    def __repr__(self):
        return self.__str__()

    def validate_params(self, route_params):
        all_params = {param.name: param for param in self.parameters}

        for key, value in route_params.items():
            if key in all_params:
                all_params[key].validate(value)
            else:
                raise ValueError(f"Unexpected parameter: {key}")

        for param in self.parameters:
            if param.is_required and route_params.get(param.name) is None:
                raise ValueError(f"Missing required parameter: {param.name}")

    def run_api(self, http_client: HttpClient, route_params=None, ):
        self.validate_params(route_params or {})

        route_with_params: str = deepcopy(self.route)
        query_string = ""

        if route_params is not None:
            for param in self.parameters:
                if param.param_location == 'path':
                    if param.name in route_params:
                        route_with_params = route_with_params.replace("{" + f"{param.name}" + "}",
                                                                      str(route_params[param.name]))
                elif param.param_location == 'query':
                    if param.name in route_params:
                        if query_string:
                            query_string += "&"
                        query_string += f"{param.name}={route_params[param.name]}"
        if query_string:
            route_with_params += f"?{query_string}"

        if self.method == "GET":
            return http_client.get(route=route_with_params)
        elif self.method == "POST":
            return http_client.post(route=route_with_params)
        else:
            raise ValueError(f"Method {self.method} not yet implemented")

    def generate_call_method(self):
        param_names = [param.name for param in self.parameters]

        safe_param_names = []
        for name in param_names:
            if keyword.iskeyword(name):
                safe_param_names.append(name + '_param')
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
        setattr(self, '__call__', locals()['__call__'].__get__(self, APIRoute))

    # def __call__(self, *args, **kwargs):
    #     if "call" in dir(self):
    #         return self.call( *args, **kwargs)
    def copy(self):
        route, method, parameters = deepcopy(self.route), deepcopy(self.method), deepcopy(self.parameters)
        return APIRoute(
            route=route,
            method=method,
            parameters=parameters
        )
