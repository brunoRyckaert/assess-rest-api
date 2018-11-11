# Assess-rest-api
This project contains a tool to assess an assignment for the Erasmus University College Brussels Software Security course.

## Prerequisites

The preferred way of running this test utility is in a Docker container. It can also be run as a Python3 script, but this is not recommended.

In either case, you need a file called `data.json` in a well-known location. If you are running Python on your host, this location is `/tmp`. If you are running a Docker image, you can place the file anywhere on your host and mount its directory on the container's `/tmp` directory, see below. For `data.json`'s format, see also below.

## Installation

```
docker run --rm --name ara -v <absolute path data.json parent dir>:/tmp yopeeters/assess-rest-api 
```

## Assessment criteria
### Rest-api
* Public api endpoint available without any auth
* Private api endpoint available with correct auth
* Private api endpoint unavailable with wrong auth
* Private api endpoint unavailable with no auth
* Public api endpoint not available through POST method
* Private api endpoint not available through POST method
### Error codes
* Access to resources other than /api/public and /api/private should return 404
* Unauthorized access to private resources should return 401
* Post request to public endpoint should return 405
## Requirements
* Python 3
* requests (pip install requests)
## Running
Run assess-rest-api.py in command line or run it in an IDE.
## Data file
* data.json by default, but can be modified in assess-rest-api.py
* list of objects containing the following components (in any order)
### Components
* sts (POST endpoint where your OAuth token can be requested)
* client_id, client_secret, audience, grant_type
* additionally, if grant_type == "password", the object should also contain username and password
* endpoint to your API, without /api/public and /api/private
### Example
```
[
    {
        "sts": "https://ryckaert.eu.auth0.com/oauth/token",
        "client_id": "I8lfgv91Hj7cTHplw...",
        "client_secret": "aM2TWKD4ajZEKci3r...",
        "audience": "https://your-api-gateway",
        "grant_type": "client_credentials",
        "endpoint": "https://tstu2yjkke.execute-api.eu-central-1.amazonaws.com/SoftSec"
      }
  ]
 ```
