import requests
import json
import random
import string


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
        print("Could not contact the STS. Make sure the STS is correct, and that you have internet access.\n-----\n")
        # traceback.print_exc(file=sys.stdout)
        return

    try:
        j = json.loads(r.text)
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
        "Authorization": "Bearer 1234"})
    # print(getPrivateWrongAuth.text)

    postPublic = requests.post(data["endpoint"] + "/api/public")
    # print(postPublic)
    postPrivate = requests.post(data["endpoint"] + "/api/private")
    # print(postPrivate)

    getRandom = requests.get(data["endpoint"]+"/api/"+''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10)))
    print("Random path:",getRandom.request.url)

    rest_api_assess = True
    fout_code_assess = True

    if getPublic.status_code != 200:
        rest_api_assess = False
        print("Your public api endpoint is not available or accessible without authentication.")
        print(getPublic.status_code,getPublic.text)
    if getPrivateCorrectAuth.status_code != 200:
        rest_api_assess = False
        print("Your private api endpoint is not accessible with proper authentication.")
        print(getPrivateCorrectAuth.status_code,getPrivateCorrectAuth.text)
    if getPrivateWrongAuth.status_code not in [400, 401, 500]:
        rest_api_assess = False
        print("Your private api endpoint is accessible with an incorrect authentication.")
        print(getPrivateWrongAuth.status_code,getPrivateWrongAuth.text)
    if getPrivateWrongAuth.status_code != 401:
        fout_code_assess = False
        print("Private API Wrong Auth: The error code should be 401, not",getPrivateWrongAuth.status_code)
    if getPrivateNoAuth.status_code not in [401, 500]:
        rest_api_assess = False
        print("Your private api endpoint is accessible without authentication.")
        print(getPrivateNoAuth.status_code,getPrivateNoAuth.text)
    if getPrivateNoAuth.status_code != 401:
        fout_code_assess = False
        print("Private API No Auth: The error code should be 401, not",getPrivateNoAuth.status_code)
    if postPublic.status_code not in [403, 405, 500]:
        rest_api_assess = False
        print("Your public api endpoint is accessible with the POST method, but shouldn't.")
        print(postPublic.status_code,postPublic.text)
    if postPublic.status_code != 405:
        fout_code_assess = False
        print("The error code should be 405, not",postPublic.status_code)
    if postPrivate.status_code not in [403, 405, 500]:
        rest_api_assess = False
        print("Your private api endpoint is accessible with the POST method, but shouldn't.")
        print(postPrivate.status_code,postPublic.text)
    if postPrivate.status_code != 405:
        fout_code_assess = False
        print("Private API post: The error code should be 405, not",postPrivate.status_code)
    if getRandom.status_code != 404:
        fout_code_assess = False
        print("Get random path: The error code should be 404, not",getRandom.status_code)

    print("Rest api assessment:", "pass" if rest_api_assess else "fail")
    print("Foutcodes api assessment:", "pass" if fout_code_assess else "fail")
    print("-------------")
