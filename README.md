
# PYSwaggerAPIWrap

![PYSwaggerAPIWrap Logo](https://raw.githubusercontent.com/KlajdiBeqiraj/PySwaggerAPIWrap/main/resources/image/logo_xsK_icon.ico) <!-- Replace with the URL of your preferred image -->

## Description

**PYSwaggerAPIWrap** is a Python package designed to streamline interaction with online APIs that expose Swagger documentation. With PYSwaggerAPIWrap, you can easily generate Python wrappers for any API documented via Swagger, making it simpler to integrate and utilize APIs in your code.

## Features

- **Universal Support**: Compatible with any API that uses Swagger for documentation.
- **Automatic Generation**: Automatically creates the necessary Python classes and methods for API interaction.
- **Easy Integration**: Seamlessly integrate API calls into your Python project with an intuitive interface.
- **Error Handling**: Manages API call errors and provides clear, helpful messages.

## Python Version

The version of Python used for the package is Python 3.9.7, but there are no specific constraints on the Python version.


## Installation

You can install **PYSwaggerAPIWrap** using pip:

```bash
pip install pyswaggerapiwrap
```

## Complete Tutorial

For a complete tutorial, please refer to the notebook available at this link: [Tutorial](https://github.com/KlajdiBeqiraj/PySwaggerAPIWrap/blob/main/notebooks/pyswaggerapi_tutorial.ipynb)


## Http client

The following lines of code import the `HttpClient` class from the `PySwaggerAPIWrap.http_client` module and set up an HTTP client with a specific endpoint and authentication token.

```python
from PySwaggerAPIWrap.http_client import HttpClient

ENDPOINT = "https://petstore.swagger.io/v2"
AUTH_TOKEN = "special-key"

http_client = HttpClient(base_url=ENDPOINT, auth_token=AUTH_TOKEN)

```

The http_client module allows you to make classic HTTP **requests** using the requests library. It supports both POST and GET methods for interacting with web services.


Using this class, we can retrieve a pandas DataFrame containing all the information from the Swagger documentation with the following method:
```python
routes_dict = http_client.get_routes_df(swagger_route="/swagger.json")
```
![get_routes_df](https://github.com/KlajdiBeqiraj/PySwaggerAPIWrap/blob/main/resources/image/get_routes_df.png?raw=true)

## API DataFrame Filter
Through the API filter class, we can wrap this dictionary to navigate through all the APIs and find the one we are interested in.

First, we create the object by passing the DataFrame as follows:
```python
from PySwaggerAPIWrap.api_filter import APIDataFrameFilter
api_filter = APIDataFrameFilter(routes_dict)
```

### filter method
We can use the **filter method** to filter our APIs in several ways:

1. **By api_type**: In this case, the APIs are divided based on the first key. For example, in the APIs from the notebook (“https://petstore.swagger.io/v2”), we have pet, user, and store.
2. **By route_pattern**: This allows us to retrieve all APIs that contain the specified string within their route.
3. **By method**: We can filter by HTTP methods such as GET and POST.
4.
```python
api_filter.filter(method="GET", api_type="pet", route_pattern="id")
```
![get_routes_df](https://github.com/KlajdiBeqiraj/PySwaggerAPIWrap/blob/main/resources/image/filter_method.png?raw=true)


### Api as attributes
Additionally, the api_filter class dynamically allows the indexing of APIs, where various APIs are assigned through a tree structure within the object. This means we can access:
```python
api_filter.store
```

and we will have all the APIs with api_type equal to store. Furthermore, we can index the APIs directly as attributes. In this case, the actual API names are modified to comply with class attribute rules. To understand, let’s show an example:

The API located at the route "store/inventory" and of type GET can be accessed with the following command:
```python
api_filter.store.get_inventory
```
The API names follow these rules:

1. They start with the method: get, post, etc.
2. Slashes / are replaced with underscores _.
3. Attributes such as {petId} are replaced with with__petId.

To clarify, let’s provide another example:

The API located at the route "/pet/{petId}/uploadImage" and of type POST can be accessed through the api_filter object as follows:
```python
api_filter.pet.post_with_petId_uploadImage
```

## Run API
To call an API once we have identified the one we are interested in, we simply call the run method. This method dynamically takes both path and query parameters as inputs.

To understand, let’s show two examples:
#### 1. method=GET, route="/store/inventory"
```python
data = api_filter.store.get_inventory.run(http_client)
data
```
```json
{
  "totvs": 5,
  "sold": 10,
  "string": 623,
  "unavailable": 2,
  "invalid_status": 2,
  "pending": 14,
  "available": 306,
  "peric": 18
}

```
#### 2. method=GET, route="/pet/{petId}"

```python
data = api_filter.pet.get_with_petId.run(http_client=http_client, petId=1)
data
```
```json
{
  "id": 1,
  "category": {
    "id": 1,
    "name": "string"
  },
  "name": "doggie",
  "photoUrls": ["string"],
  "tags": [
    {
      "id": 1,
      "name": "string"
    }
  ],
  "status": "available"
}


```
