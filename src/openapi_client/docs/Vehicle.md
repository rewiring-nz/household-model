# Vehicle


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**fuel_type** | **str** |  | 
**kms_per_week** | **int** | Typical kilometres driven per week by this vehicle | [optional] 

## Example

```python
from openapi_client.models.vehicle import Vehicle

# TODO update the JSON string below
json = "{}"
# create an instance of Vehicle from a JSON string
vehicle_instance = Vehicle.from_json(json)
# print the JSON string representation of the object
print Vehicle.to_json()

# convert the object into a dict
vehicle_dict = vehicle_instance.to_dict()
# create an instance of Vehicle from a dict
vehicle_from_dict = Vehicle.from_dict(vehicle_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


