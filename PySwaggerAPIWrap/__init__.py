from PySwaggerAPIWrap import *  # pylint: disable=W0406
from copy import copy


class AdditionalAPI:
    def __init__(self, original_route: str, method: str, fixed_route_params: dict):
        self.fixed_route_params = fixed_route_params
        self.method = method
        self.original_route = original_route
        self.new_route = self.get_new_route()

    def get_new_route(self):
        route_with_params = copy(self.original_route)
        for key_param in self.fixed_route_params:
            route_with_params = route_with_params.replace("{" + f"{key_param}" + "}",
                                                          str(self.fixed_route_params[
                                                                  key_param]))

        return route_with_params

    def __str__(self):
        return (f"\n\toriginal_route={self.original_route}\n"
                f"\tnew_route={self.new_route}\n"
                f"\tmethod={self.method}\n")

    def __repr__(self):
        return self.__str__()


ADDITIONAL_APIS = dict(
    # getDatasetList=AdditionalAPI(
    #     original_route="/Dataset/get/DatasetsPagedByProjectId/{page}/{pageSize}/{sort}/{search}/{projectId}",
    #     method="GET",
    #     fixed_route_params=dict(
    #         page=1,
    #         pageSize=-1,
    #         sort="empty",
    #         search="empty"
    #     )
    # ),

)

ADDITIONAL_APIS_NAME = list(ADDITIONAL_APIS.keys())
