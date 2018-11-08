# Assess-rest-api
This project contains a tool to assess an assignment for the Erasmus University College Brussels Software Security course.

## Prerequisites

* Python3
* In  `~/.bash_profile` or equivalent
```
   export LC_ALL=en_US.UTF-8
   export LANG=en_US.UTF-8
```
* pipenv

## Installation

```
> git clone git@github.com:brunoRyckaert/assess-rest-api.git
...
> pipenv --three install
...
> pipenv shell
...
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
