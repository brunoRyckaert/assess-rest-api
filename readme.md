# Assess-rest-api
This project contains a tool to assess an assignment for the Erasmus University College Brussels Software Security course.

## Prerequisites

The preferred way of running this test utility is in a Docker container. The only prerequisite in this case is Docker.

The test utility can also be run as a Python3 script, but this is not recommended. Obviously Python3 is needed in this case, as well as pip and [pipenv](https://pipenv.readthedocs.io/en/latest/).

In either case, you need a file called `data.json` in a well-known location. If you are running Python on your host, this location is `/var/test_input`. If you are running a Docker image, you can place the file anywhere on your host and mount its directory on the container's `/var/test_input` directory, see below. For `data.json`'s format, see also below.

## Installation and usage

### Docker (recommended)

```
docker run --rm --name ara -v <absolute path to data.json's parent dir>:/var/test_input yopeeters/assess-rest-api
```

### Python (not recommended and not tested)

```
git clone https://github.com/JohanPeeters/assess-rest-api
cd assess-rest-api
pipenv check
pipenv install
pipenv run python assess-rest-api.py
```

On subsequent use, the last command should suffice.

## Assessment criteria

* The API is 'protected' with an API key
* The API has a public endpoint that does not require further authentication
* A protected endpoint requires authentication with a valid access token
* Only GET, HEAD and OPTIONS requests are allowed

|Condition                     |Expected status code|
|------------------------------|--------------------|
|Invocation successful         |200                 |
|Missing API key               |403 or 404          |
|Missing or invalid access token|401, 403 or 404    |
|Forbidden method              | 403, 404 or 405    |

## Data file

`data.json` contains a JSON array which contain elements with the following fields:

|Field           |Description               | |
|----------------|--------------------------|-|
|`owner`           |EhB email address of the student whose API is being assessed|mandatory|
|`api`             |The base URL of the API. If you are using AWS API Gateway, this would be the URL of the stage.|mandatory|
|`api_key`         |The API key. This test suite puts the API key in the `x-api-key` header. Let me know if you have a good reason to present the API key differently.|mandatory|
|`public`          |The public endpoint. In the full URL, this value trails the value of the `api` field.|mandatory|
|`protected`       |The endpoint that requires authentication. In the full URL, this value also trails the value of the `api` field.|mandatory|
|`iss`             |The issuer URL. This is the same URL as in tokens issued by the issuer. It is not necessarily a prefix of the authorization server's token or authorization endpoint.|mandatory|
|`client_id`       |The ID for the test client registered with the authorization server.|mandatory|
|`client_secret`   |The secret issued for the test client by the authorization server.|mandatory|
|`audience`        |The identifier of the API which will be invoked with the token. Not needed for Cognito, required by Auth0. If this field is absent, the token request is sent with an `audience` parameter consisting of the full endpoint URL.|optional|

### Example
```
[
  {
    "owner": "johan.peeters@ehb.be",
    "api": "https://<AWS API identifier>.execute-api.eu-west-1.amazonaws.com/<stage>",
    "api_key": "<secret key>",
    "public": "<public resource name>",
    "protected": "<protected resource name>",
    "iss": "https://cognito-idp.eu-west-1.amazonaws.com/<Pool Id>",
    "client_id": "<App client id>",
    "client_secret": "<App client secret>"
  }
]
 ```
