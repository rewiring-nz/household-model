# Household


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**location** | [**LocationEnum**](LocationEnum.md) |  | [optional] 
**occupancy** | **int** | Number of occupants | [optional] 
**space_heating** | [**SpaceHeatingEnum**](SpaceHeatingEnum.md) |  | [optional] 
**water_heating** | [**WaterHeatingEnum**](WaterHeatingEnum.md) |  | [optional] 
**cooktop** | [**CooktopEnum**](CooktopEnum.md) |  | [optional] 
**vehicles** | [**List[Vehicle]**](Vehicle.md) |  | [optional] 
**solar** | [**Solar**](Solar.md) |  | [optional] 
**battery** | [**Battery**](Battery.md) |  | [optional] 

## Example

```python
from openapi_client.models.household import Household

# TODO update the JSON string below
json = "{}"
# create an instance of Household from a JSON string
household_instance = Household.from_json(json)
# print the JSON string representation of the object
print Household.to_json()

# convert the object into a dict
household_dict = household_instance.to_dict()
# create an instance of Household from a dict
household_from_dict = Household.from_dict(household_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


