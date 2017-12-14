import requests
import sys
from data import *

try:
    r = requests.post(data["sts"], None, {
        "client_id": data["client_id"],
        "client_secret": data["client_secret"],
        "audience": data["audience"],
        "grant_type": data["grant_type"],
        "username": data["username"] if "grant_type" in data and data["grant_type"] == "password" else "",
        "password": data["password"] if "grant_type" in data and data["grant_type"] == "password" else ""
    })
except KeyError:
    print("Invalid data. See details below:")
    if "grant_type" not in data:
        print("grant_type not set.")
    if "grant_type" in data and data["grant_type"] == "password":
        if "username" not in data:
            print("grant_type is \"password\", but username is not set.")
        if "password" not in data:
            print("grant_type is \"password\", but password is not set.")
    sys.exit(2)
j = json.loads(r.text)
try:
    access_token = j['access_token']
except:
    print("Error retrieving access code:")
    print(r.text)
    sys.exit(1)

print("Access token:", access_token)

getPublic = requests.get(data["endpoint"] + "/api/public")
print(getPublic)
getPrivateNoAuth = requests.get(data["endpoint"] + "/api/private")
print(getPrivateNoAuth)
getPrivateCorrectAuth = requests.get(data["endpoint"] + "/api/private",
                                     headers={"Authorization": "Bearer " + access_token})
print(getPrivateCorrectAuth)
getPrivateWrongAuth = requests.get(data["endpoint"] + "/api/private", headers={
    "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImspZCI6IlFVRkNSRFpGUlRsQ01FUkZNRUpCTnpZMVFVWkROelF3UmpGR09ETkROVFl5T0VVelJqSXlSZyJ9.eyJpc3MiOiJodHRwczovL3NhbXZhbnJveS5ldS5hdXRoMC5jb20vIiwic3ziIjoiNWNCbXVLQTQ0c3pGSk9PVloya3VIRzdHYkNsWHJiOHJAY2xpZW50cyIsImF1ZCI6Imh0dHBzOi8vU29mdHdhcmVTZWN1cml0eVNhbS5lcyIsImlhdCI6MTUxMzI2MzgyNSwiZXhwIjoxNTEzMzUwMjI1LCJndHkiOiJjbGllbnQtY3JlZGVudGlhbHMifQ.Wszfjiw3g2eOwgQGSeJuWV93xaO4b5w6b99ZHGEfLQGjo2lPB7TdDCBmq7BaeP3DMkXN9jJK-evUP9yRPA_TMGtF75o5jCgkkePLt7twol0h_g2iuw6lqnMRsfhwyMXrs0UdGx1mPG59MUEvKFxFR6e30Qt1FMxgT4tsgV5efQyJYgCI8UtxGkh73yC0fZJOD-3Tobm4HIrXavcmh5CRphorLEvWuxj25Ghrpzu9vRKgZX5bsT--3oLJgjsN62WgmQCDi9P1y7nwClyhQlJ811QB24Ne1B2Ldc92poY4V3FdVPSqTKUcUtqfVa9kbGBclxr2OvfspMDFgepzNbl9gQ"})
print(getPrivateWrongAuth)

postPublic = requests.post(data["endpoint"] + "/api/public")
print(postPublic)
postPrivate = requests.post(data["endpoint"] + "/api/private")
print(postPrivate)

success = True

if getPublic.status_code != 200:
    success = False
    print("Your public api endpoint is not available or accessible without authentication.")
if getPrivateCorrectAuth.status_code != 200:
    success = False
    print("Your private api endpoint is not accessible with proper authentication.")
if getPrivateWrongAuth.status_code != 401:
    success = False
    if getPrivateWrongAuth.status_code == 200:
        print("Your private api endpoint is accessible with an incorrect authentication.")
if getPrivateNoAuth.status_code != 401:
    success = False
    if getPrivateWrongAuth.status_code == 200:
        print("Your private api endpoint is accessible without authentication.")
if postPublic.status_code != 403:
    success = False
    print("Your public api endpoint is accessible with the POST method, but shouldn't.")
if postPrivate.status_code != 403:
    success = False
    print("Your private api endpoint is accessible with the POST method, but shouldn't.")

print("The final assessment is:", "pass" if success else "fail")
