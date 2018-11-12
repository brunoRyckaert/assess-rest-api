# Assess-rest-api
This project contains a tool to assess an assignment for the Erasmus University College Brussels Software Security course.

## Prerequisites

The preferred way of running this test utility is in a Docker container. The only prerequisite in this case is Docker.

The test utility can also be run as a Python3 script, but this is not recommended. Obviously Python3 is needed in this case, as well as pip and [pipenv](https://pipenv.readthedocs.io/en/latest/).

In either case, you need a file called `data.json` in a well-known location. If you are running Python on your host, this location is `/tmp`. If you are running a Docker image, you can place the file anywhere on your host and mount its directory on the container's `/tmp` directory, see below. For `data.json`'s format, see also below.

## Installation and usage

### Docker (recommended)

```
docker run --rm --name ara -v <absolute path to data.json's parent dir>:/tmp yopeeters/assess-rest-api
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

|Field           |Description               |
|----------------|--------------------------|
|`owner`           |EhB email address of the student whose API is being assessed|
|`api`             |The base URL of the API. If you are using AWS API Gateway, this would be the URL of the stage.|
|`api_key`         |The API key. This test suite puts the API key in the `x-api-key` header. Let me know if you have a good reason to present the API key differently.|
|`public`          |The public endpoint. This value will be appended to the value of the `api` field.|
|`protected`       |The endpoint that requires authentication. This value will also be appended to the value of the `api` field.|
|`iss`             |The issuer URL. This is the same URL as in tokens issued by the issuer. It is not necessarily a prefix of the authorization server's token or authorization endpoint.|
|`client_id`       |The ID for the test client registered with the authorization server.|
|`client_secret`   |The secret issued for the test client by the authorization server.|

All fields are mandatory.


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
