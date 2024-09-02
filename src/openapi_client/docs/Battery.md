# Battery

The household's home battery system

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**has_battery** | **bool** | Whether the household has battery | 
**capacity** | **float** | The capacity of the battery system in kWh. Should be null if hasBattery is False and installBattery is False. | [optional] 
**power_output** | **float** | The continuous power output of the battery system in kW. Should be null if hasBattery is False and installBattery is False. | [optional] 
**peak_power_output** | **float** | The peak power output of the battery system in kW. Should be null if hasBattery is False and installBattery is False. | [optional] 
**install_battery** | **bool** | Whether the household wants to install a battery. Should be null is hasBattery is True. | [optional] 

## Example

```python
from openapi_client.models.battery import Battery

# TODO update the JSON string below
json = "{}"
# create an instance of Battery from a JSON string
battery_instance = Battery.from_json(json)
# print the JSON string representation of the object
print Battery.to_json()

# convert the object into a dict
battery_dict = battery_instance.to_dict()
# create an instance of Battery from a dict
battery_from_dict = Battery.from_dict(battery_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


