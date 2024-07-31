from typing import Any

from PySwaggerAPIWrap import *  # pylint: disable=W0406
from copy import copy
from pydantic import BaseModel, Field


class AdditionalAPI(BaseModel):
    original_route: str = Field(..., description="The original route.")
    method: str = Field(..., description="Method used for the api")
    fixed_route_params: dict = Field(..., description="The parameter you want to set")
    new_route: str = Field(None, description="The new route")

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.new_route = self.get_new_route()

    def get_new_route(self) -> str:
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


class AdditionalAPISContainer:
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

    @staticmethod
    def add_additional_api(new_api: AdditionalAPI, name: str):
        AdditionalAPISContainer.ADDITIONAL_APIS.update({name: new_api})

    @staticmethod
    def get_additional_apis_name():
        return list(AdditionalAPISContainer.ADDITIONAL_APIS)
