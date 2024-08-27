# UpfrontCost

The estimated total NZD cost of electrifying the household

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**solar** | **float** | The estimated cost of installing solar in NZD | [optional] 
**battery** | **float** | The estimated cost of installing a battery in NZD | [optional] 
**cooktop** | **float** | The estimated cost of switching to cooktop in NZD | [optional] 
**water_heating** | **float** | The estimated cost of switching to waterHeating in NZD | [optional] 
**space_heating** | **float** | The estimated cost of switching to spaceHeating in NZD | [optional] 

## Example

```python
from openapi_client.models.upfront_cost import UpfrontCost

# TODO update the JSON string below
json = "{}"
# create an instance of UpfrontCost from a JSON string
upfront_cost_instance = UpfrontCost.from_json(json)
# print the JSON string representation of the object
print UpfrontCost.to_json()

# convert the object into a dict
upfront_cost_dict = upfront_cost_instance.to_dict()
# create an instance of UpfrontCost from a dict
upfront_cost_from_dict = UpfrontCost.from_dict(upfront_cost_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


