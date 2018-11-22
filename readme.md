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
* Public methods do not require authentication
* Authenticated methods require a valid access token
* Methods not listed as public or authenticated are denied access. The script tests for following methods: HEAD, GET, POST, PUT, PATCH and DELETE. OPTIONS is not being tested and will be discussed in the OAuth and OIDC module in connection with CORS preflight requests
* The access token must contain at the scope specified with an authenticated method to gain access
* No other scopes affords access

|Condition                     |Expected status code|
|------------------------------|--------------------|
|Invocation successful         |200                 |
|Missing API key               |403 or 404          |
|Missing                       |401, 403 or 404     |
|Forbidden method              |403, 404 or 405     |
|Invalid access token          |401, 403, 404 or 500|

## Data file

`data.json` contains a JSON array which contain elements with the following fields:

|Field           |Description               | |
|----------------|--------------------------|-|
|`owner`           |EhB email address of the student whose API is being assessed|mandatory|
|`api`             |The base URL of the API. If you are using AWS API Gateway, this would be the URL of the stage.|mandatory|
|`api_key`         |The API key. This test suite puts the API key in the `x-api-key` header. Let me know if you have a good reason to present the API key differently.|mandatory|
|`resource`        |The endpoint to be tested.|mandatory|
|`public`          |An array of methods which afford anonymous access to the resource.|this field or the `authenticated` field must be present, or both|
|`authenticated`       |A JSON object. The keys are the methods that require authentication. The value is the corresponding scope string needed for authorization.|this field or the `public` field must be present, or both|
|`iss`             |The issuer URL. This is the same URL as in tokens issued by the issuer. It is not necessarily a prefix of the authorization server's token or authorization endpoint.|mandatory if `authenticated` is present|
|`client_id`       |The ID for the test client registered with the authorization server.|mandatory if `authenticated` is present|
|`client_secret`   |The secret issued for the test client by the authorization server.|mandatory if `authenticated` is present|
|`audience`        |The identifier of the API which will be invoked with the token. Not needed for Cognito, required by Auth0. If this field is absent, the token request is sent with an `audience` parameter consisting of the full endpoint URL.|optional|

### Example
```
[
  {
    "owner": "johan.peeters@ehb.be",
    "api": "https://<AWS API identifier>.execute-api.eu-west-1.amazonaws.com/<stage>",
    "api_key": "<secret key>",
    "resource": "rides",
    "public": ["GET"],
    "authenticated": {"POST": "rides/create"},
    "iss": "https://cognito-idp.eu-west-1.amazonaws.com/<Pool Id>",
    "client_id": "<App client id>",
    "client_secret": "<App client secret>",
    "audience": "rides"
  },
  {
    "owner": "johan.peeters@ehb.be",
    "api": "https://<AWS API identifier>.execute-api.eu-west-1.amazonaws.com/<stage>",
    "api_key": "<secret key>",
    "public": ["GET"],
    "authenticated": {"PUT": "rides/update", "DELETE": "rides/delete"},
    "resource": "rides/alice",
    "iss": "https://cognito-idp.eu-west-1.amazonaws.com/<Pool Id>",
    "client_id": "<App client id>",
    "client_secret": "<App client secret>",
    "audience": "rides"
  }
]
 ```
