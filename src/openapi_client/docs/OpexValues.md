# OpexValues


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**before** | **float** | The household&#39;s opex costs per week before electrification in NZD to 2 dp. | [optional] 
**after** | **float** | The household&#39;s opex costs per week after electrification in NZD to 2 dp. | [optional] 
**difference** | **float** | The difference in opex costs before &amp; after electrification, in NZD to 2 dp. | [optional] 

## Example

```python
from openapi_client.models.opex_values import OpexValues

# TODO update the JSON string below
json = "{}"
# create an instance of OpexValues from a JSON string
opex_values_instance = OpexValues.from_json(json)
# print the JSON string representation of the object
print OpexValues.to_json()

# convert the object into a dict
opex_values_dict = opex_values_instance.to_dict()
# create an instance of OpexValues from a dict
opex_values_from_dict = OpexValues.from_dict(opex_values_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


