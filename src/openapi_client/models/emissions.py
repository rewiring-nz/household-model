# coding: utf-8

"""
    Household savings

    This is the API for a household savings model. You can provide details about a household's energy use, and receive information about the household's potential emissions & cost savings from electrifying their fossil fuel machines, as well as the upfront costs of switching.

    The version of the OpenAPI document: 0.0.2
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json


from typing import Optional
from pydantic import BaseModel, Field, StrictInt
from openapi_client.models.emissions_values import EmissionsValues

class Emissions(BaseModel):
    """
    Emissions
    """
    per_week: Optional[EmissionsValues] = Field(default=None, alias="perWeek")
    per_year: Optional[EmissionsValues] = Field(default=None, alias="perYear")
    over_lifetime: Optional[EmissionsValues] = Field(default=None, alias="overLifetime")
    operational_lifetime: Optional[StrictInt] = Field(default=None, alias="operationalLifetime", description="The assumed operational lifetime of the machines in years")
    __properties = ["perWeek", "perYear", "overLifetime", "operationalLifetime"]

    class Config:
        """Pydantic configuration"""
        allow_population_by_field_name = True
        validate_assignment = True

    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.dict(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Emissions:
        """Create an instance of Emissions from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self):
        """Returns the dictionary representation of the model using alias"""
        _dict = self.dict(by_alias=True,
                          exclude={
                          },
                          exclude_none=True)
        # override the default output from pydantic by calling `to_dict()` of per_week
        if self.per_week:
            _dict['perWeek'] = self.per_week.to_dict()
        # override the default output from pydantic by calling `to_dict()` of per_year
        if self.per_year:
            _dict['perYear'] = self.per_year.to_dict()
        # override the default output from pydantic by calling `to_dict()` of over_lifetime
        if self.over_lifetime:
            _dict['overLifetime'] = self.over_lifetime.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: dict) -> Emissions:
        """Create an instance of Emissions from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return Emissions.parse_obj(obj)

        _obj = Emissions.parse_obj({
            "per_week": EmissionsValues.from_dict(obj.get("perWeek")) if obj.get("perWeek") is not None else None,
            "per_year": EmissionsValues.from_dict(obj.get("perYear")) if obj.get("perYear") is not None else None,
            "over_lifetime": EmissionsValues.from_dict(obj.get("overLifetime")) if obj.get("overLifetime") is not None else None,
            "operational_lifetime": obj.get("operationalLifetime")
        })
        return _obj

