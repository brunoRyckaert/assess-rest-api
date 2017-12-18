import requests
import json

def assess(data):
    print("Processing", data)
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
        if "sts" not in data:
            print("sts not set.")
        if "client_id" not in data:
            print("client_id not set.")
        if "client_secret" not in data:
            print("client_secret not set.")
        if "audience" not in data:
            print("audience not set.")
        return
    except requests.RequestException:
        print("Could not contact the STS. Check to make sure the STS is correct, and that you have internet access.\n-----\n")
        # traceback.print_exc(file=sys.stdout)
        return
    j = json.loads(r.text)
    try:
        access_token = j['access_token']
    except:
        print("Error retrieving access code:")
        print(r.text)
        return

    print("Access token:", access_token)

    try:
        requests.get(data["endpoint"] + "/api/public")
    except requests.RequestException:
        print("Could not connect to endpoint. Check to make sure the endpoint is correct, and that you have internet access.\n-----\n")
        # traceback.print_exc(file=sys.stdout)
        return

    getPublic = requests.get(data["endpoint"] + "/api/public")
    # print(getPublic)
    getPrivateNoAuth = requests.get(data["endpoint"] + "/api/private")
    # print(getPrivateNoAuth)
    getPrivateCorrectAuth = requests.get(data["endpoint"] + "/api/private",
                                         headers={"Authorization": "Bearer " + access_token})
    # print(getPrivateCorrectAuth)
    getPrivateWrongAuth = requests.get(data["endpoint"] + "/api/private", headers={
        "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImspZCI6IlFVRkNSRFpGUlRsQ01FUkZNRUpCTnpZMVFVWkROelF3UmpGR09ETkROVFl5T0VVelJqSXlSZyJ9.eyJpc3MiOiJodHRwczovL3NhbXZhbnJveS5ldS5hdXRoMC5jb20vIiwic3ziIjoiNWNCbXVLQTQ0c3pGSk9PVloya3VIRzdHYkNsWHJiOHJAY2xpZW50cyIsImF1ZCI6Imh0dHBzOi8vU29mdHdhcmVTZWN1cml0eVNhbS5lcyIsImlhdCI6MTUxMzI2MzgyNSwiZXhwIjoxNTEzMzUwMjI1LCJndHkiOiJjbGllbnQtY3JlZGVudGlhbHMifQ.Wszfjiw3g2eOwgQGSeJuWV93xaO4b5w6b99ZHGEfLQGjo2lPB7TdDCBmq7BaeP3DMkXN9jJK-evUP9yRPA_TMGtF75o5jCgkkePLt7twol0h_g2iuw6lqnMRsfhwyMXrs0UdGx1mPG59MUEvKFxFR6e30Qt1FMxgT4tsgV5efQyJYgCI8UtxGkh73yC0fZJOD-3Tobm4HIrXavcmh5CRphorLEvWuxj25Ghrpzu9vRKgZX5bsT--3oLJgjsN62WgmQCDi9P1y7nwClyhQlJ811QB24Ne1B2Ldc92poY4V3FdVPSqTKUcUtqfVa9kbGBclxr2OvfspMDFgepzNbl9gQ"})
    # print(getPrivateWrongAuth)

    postPublic = requests.post(data["endpoint"] + "/api/public")
    # print(postPublic)
    postPrivate = requests.post(data["endpoint"] + "/api/private")
    # print(postPrivate)

    success = True

    if getPublic.status_code != 200:
        success = False
        print("Your public api endpoint is not available or accessible without authentication.")
        print(getPublic.status_code,getPublic.text)
    if getPrivateCorrectAuth.status_code != 200:
        success = False
        print("Your private api endpoint is not accessible with proper authentication.")
        print(getPrivateCorrectAuth.status_code,getPrivateCorrectAuth.text)
    if getPrivateWrongAuth.status_code not in [401,500]:
        success = False
        print("Your private api endpoint is accessible with an incorrect authentication.")
        print(getPrivateWrongAuth.status_code,getPrivateWrongAuth.text)
    if getPrivateNoAuth.status_code not in [401,500]:
        success = False
        print("Your private api endpoint is accessible without authentication.")
        print(getPrivateNoAuth.status_code,getPrivateNoAuth.text)
    if postPublic.status_code not in [403, 405,500]:
        success = False
        print("Your public api endpoint is accessible with the POST method, but shouldn't.")
        print(postPublic.status_code,postPublic.text)
    if postPrivate.status_code not in [403, 405, 500]:
        success = False
        print("Your private api endpoint is accessible with the POST method, but shouldn't.")
        print(postPrivate.status_code,postPublic.text)

    print("The final assessment is:", "pass" if success else "fail")
    print("-------------")