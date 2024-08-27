# Savings


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**emissions** | [**Emissions**](Emissions.md) |  | [optional] 
**opex** | [**Opex**](Opex.md) |  | [optional] 
**upfront_cost** | [**UpfrontCost**](UpfrontCost.md) |  | [optional] 
**recommendation** | [**Recommendation**](Recommendation.md) |  | [optional] 

## Example

```python
from openapi_client.models.savings import Savings

# TODO update the JSON string below
json = "{}"
# create an instance of Savings from a JSON string
savings_instance = Savings.from_json(json)
# print the JSON string representation of the object
print Savings.to_json()

# convert the object into a dict
savings_dict = savings_instance.to_dict()
# create an instance of Savings from a dict
savings_from_dict = Savings.from_dict(savings_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


