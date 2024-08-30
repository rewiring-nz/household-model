# Recommendation


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**action** | [**RecommendationActionEnum**](RecommendationActionEnum.md) |  | 
**url** | **str** | A URL to a resource to give more information about this recommended action. | [optional] 

## Example

```python
from openapi_client.models.recommendation import Recommendation

# TODO update the JSON string below
json = "{}"
# create an instance of Recommendation from a JSON string
recommendation_instance = Recommendation.from_json(json)
# print the JSON string representation of the object
print Recommendation.to_json()

# convert the object into a dict
recommendation_dict = recommendation_instance.to_dict()
# create an instance of Recommendation from a dict
recommendation_from_dict = Recommendation.from_dict(recommendation_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


