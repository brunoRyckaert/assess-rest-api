from assess import *

# The data should be a JSON list of objects containing following elements:
# sts, client_id, client_secret, audience, grant_type
# additionally, if grant_type == "password", the object should also contain username and password

data_file = "data.json"
try:
    dataset=json.load(open(data_file))
    for data in dataset:
        assess(data)
except json.decoder.JSONDecodeError:
    print("Error: The json file containing the data is malformed.")
