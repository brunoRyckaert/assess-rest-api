# Assess-rest-api
This project is part of a school project for Erasmus University College Brussels as part of the Software Security course.
## Requirements
* Python 3
* requests (pip install requests)
## Running
Run assess-rest-api.py in command line or run it in an IDE.
## Data file
* data.json by default, but can be modified in assess-rest-api.py
* list of objects containing the following components (in any order)
### Components
* sts (GET endpoint where your Oauth token can be requested)
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
