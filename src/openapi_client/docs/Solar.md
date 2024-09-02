# Solar

The household's solar panel system

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**has_solar** | **bool** | Whether the household has solar | 
**size** | **float** | The size of the solar panel system in kW. Should be null if hasSolar is False and installSolar is False. | [optional] 
**install_solar** | **bool** | Whether the household wants to install solar. Should be null if hasSolar is True. | [optional] 

## Example

```python
from openapi_client.models.solar import Solar

# TODO update the JSON string below
json = "{}"
# create an instance of Solar from a JSON string
solar_instance = Solar.from_json(json)
# print the JSON string representation of the object
print Solar.to_json()

# convert the object into a dict
solar_dict = solar_instance.to_dict()
# create an instance of Solar from a dict
solar_from_dict = Solar.from_dict(solar_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


