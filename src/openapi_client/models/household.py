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


from typing import List, Optional
from pydantic import BaseModel, Field, StrictStr, conint, conlist, validator
from openapi_client.models.battery import Battery
from openapi_client.models.solar import Solar
from openapi_client.models.vehicle import Vehicle

class Household(BaseModel):
    """
    Household
    """
    location: Optional[StrictStr] = Field(default=None, description="Where the household is located")
    occupancy: Optional[conint(strict=True, le=100, ge=1)] = Field(default=None, description="Number of occupants")
    space_heating: Optional[StrictStr] = Field(default=None, alias="spaceHeating", description="The main method of space heating")
    water_heating: Optional[StrictStr] = Field(default=None, alias="waterHeating", description="The method of water heating")
    cooktop: Optional[StrictStr] = Field(default=None, description="The main energy source for cooking")
    vehicles: Optional[conlist(Vehicle)] = None
    solar: Optional[Solar] = None
    battery: Optional[Battery] = None
    __properties = ["location", "occupancy", "spaceHeating", "waterHeating", "cooktop", "vehicles", "solar", "battery"]

    @validator('location')
    def location_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('NORTHLAND', 'AUCKLAND_NORTH', 'AUCKLAND_CENTRAL', 'AUCKLAND_EAST', 'AUCKLAND_WEST', 'AUCKLAND_SOUTH', 'WAIKATO', 'BAY_OF_PLENTY', 'GISBORNE', 'HAWKES_BAY', 'TARANAKI', 'MANAWATU_WANGANUI', 'WELLINGTON', 'TASMAN', 'NELSON', 'MARLBOROUGH', 'WEST_COAST', 'CANTERBURY', 'OTAGO', 'SOUTHLAND', 'STEWART_ISLAND', 'CHATHAM_ISLANDS', 'GREAT_BARRIER_ISLAND', 'OVERSEAS', 'OTHER'):
            raise ValueError("must be one of enum values ('NORTHLAND', 'AUCKLAND_NORTH', 'AUCKLAND_CENTRAL', 'AUCKLAND_EAST', 'AUCKLAND_WEST', 'AUCKLAND_SOUTH', 'WAIKATO', 'BAY_OF_PLENTY', 'GISBORNE', 'HAWKES_BAY', 'TARANAKI', 'MANAWATU_WANGANUI', 'WELLINGTON', 'TASMAN', 'NELSON', 'MARLBOROUGH', 'WEST_COAST', 'CANTERBURY', 'OTAGO', 'SOUTHLAND', 'STEWART_ISLAND', 'CHATHAM_ISLANDS', 'GREAT_BARRIER_ISLAND', 'OVERSEAS', 'OTHER')")
        return value

    @validator('space_heating')
    def space_heating_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('WOOD', 'GAS', 'LPG', 'ELECTRIC_RESISTANCE', 'ELECTRIC_HEAT_PUMP', 'DONT_KNOW'):
            raise ValueError("must be one of enum values ('WOOD', 'GAS', 'LPG', 'ELECTRIC_RESISTANCE', 'ELECTRIC_HEAT_PUMP', 'DONT_KNOW')")
        return value

    @validator('water_heating')
    def water_heating_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('GAS', 'LPG', 'ELECTRIC_RESISTANCE', 'ELECTRIC_HEAT_PUMP', 'SOLAR', 'DONT_KNOW'):
            raise ValueError("must be one of enum values ('GAS', 'LPG', 'ELECTRIC_RESISTANCE', 'ELECTRIC_HEAT_PUMP', 'SOLAR', 'DONT_KNOW')")
        return value

    @validator('cooktop')
    def cooktop_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('GAS', 'LPG', 'ELECTRIC_RESISTANCE', 'ELECTRIC_INDUCTION', 'DONT_KNOW'):
            raise ValueError("must be one of enum values ('GAS', 'LPG', 'ELECTRIC_RESISTANCE', 'ELECTRIC_INDUCTION', 'DONT_KNOW')")
        return value

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
    def from_json(cls, json_str: str) -> Household:
        """Create an instance of Household from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self):
        """Returns the dictionary representation of the model using alias"""
        _dict = self.dict(by_alias=True,
                          exclude={
                          },
                          exclude_none=True)
        # override the default output from pydantic by calling `to_dict()` of each item in vehicles (list)
        _items = []
        if self.vehicles:
            for _item in self.vehicles:
                if _item:
                    _items.append(_item.to_dict())
            _dict['vehicles'] = _items
        # override the default output from pydantic by calling `to_dict()` of solar
        if self.solar:
            _dict['solar'] = self.solar.to_dict()
        # override the default output from pydantic by calling `to_dict()` of battery
        if self.battery:
            _dict['battery'] = self.battery.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: dict) -> Household:
        """Create an instance of Household from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return Household.parse_obj(obj)

        _obj = Household.parse_obj({
            "location": obj.get("location"),
            "occupancy": obj.get("occupancy"),
            "space_heating": obj.get("spaceHeating"),
            "water_heating": obj.get("waterHeating"),
            "cooktop": obj.get("cooktop"),
            "vehicles": [Vehicle.from_dict(_item) for _item in obj.get("vehicles")] if obj.get("vehicles") is not None else None,
            "solar": Solar.from_dict(obj.get("solar")) if obj.get("solar") is not None else None,
            "battery": Battery.from_dict(obj.get("battery")) if obj.get("battery") is not None else None
        })
        return _obj

