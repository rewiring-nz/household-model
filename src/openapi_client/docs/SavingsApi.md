# openapi_client.SavingsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**calculate_savings**](SavingsApi.md#calculate_savings) | **POST** /savings | Calculate savings &amp; get upfront cost


# **calculate_savings**
> Savings calculate_savings(household)

Calculate savings & get upfront cost

Calculate the emissions savings, opex savings, and the upfront cost from electrifying a given household.

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.household import Household
from openapi_client.models.savings import Savings
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.SavingsApi(api_client)
    household = openapi_client.Household() # Household | Input a household's energy behaviour

    try:
        # Calculate savings & get upfront cost
        api_response = api_instance.calculate_savings(household)
        print("The response of SavingsApi->calculate_savings:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SavingsApi->calculate_savings: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **household** | [**Household**](Household.md)| Input a household&#39;s energy behaviour | 

### Return type

[**Savings**](Savings.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Success |  -  |
**400** | Invalid input |  -  |
**422** | Validation exception |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

