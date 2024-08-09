# Opex


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**per_week** | [**OpexValues**](OpexValues.md) |  | [optional] 
**per_year** | [**OpexValues**](OpexValues.md) |  | [optional] 
**over_lifetime** | [**OpexValues**](OpexValues.md) |  | [optional] 
**operational_lifetime** | **int** | The assumed operational lifetime of the machines in years | [optional] 

## Example

```python
from openapi_client.models.opex import Opex

# TODO update the JSON string below
json = "{}"
# create an instance of Opex from a JSON string
opex_instance = Opex.from_json(json)
# print the JSON string representation of the object
print Opex.to_json()

# convert the object into a dict
opex_dict = opex_instance.to_dict()
# create an instance of Opex from a dict
opex_from_dict = Opex.from_dict(opex_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


