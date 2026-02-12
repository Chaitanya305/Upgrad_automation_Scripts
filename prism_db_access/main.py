import requests
from requests.auth import HTTPDigestAuth
import random
import string


def generate_password():
    # Choose from letters (a-z, A-Z) and digits (0-9)
    length = 10
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def create_or_update_mongo_user(public_key, private_key, project_id, username, password, role_name):
    base_url = "https://cloud.mongodb.com/api/atlas/v2"
    user_url = f"{base_url}/groups/{project_id}/databaseUsers"
    
    auth = HTTPDigestAuth(public_key, private_key)
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/vnd.atlas.2023-02-01+json"
    }

    payload = {
        "databaseName": "admin",
        "username": username,
        "password": password,
        "roles": [
            {
                "databaseName": "admin",
                "roleName": role_name
            }
        ]
    }

    # Try creating the user
    response = requests.post(user_url, headers=headers, auth=auth, json=payload)

    if response.status_code == 201:
        print("MongoDB user created successfully.")
    elif response.status_code == 409:
        print("User already exists. Attempting to update the user...")
        # PATCH existing user
        update_url = f"{user_url}/admin/{username}"
        update_payload = {
            "databaseName": "admin",
            "groupId": project_id,
            "username": username,
            "password": password,
            "roles": [
                {
                    "databaseName": "admin",
                    "roleName": "readWriteAnyDatabase"
                }
            ]
        }

        patch_response = requests.patch(update_url, headers=headers, auth=auth, json=update_payload)

        if patch_response.status_code == 200:
            print("MongoDB user updated successfully.")
        else:
            print("Failed to update user. Status code: {}".format(patch_response.status_code))
            print("Response:", patch_response.text)
    else:
        print("Failed to create user. Status code: {}".format(response.status_code))
        print("Response:", response.text)


#dbpass = generate_password()
dbpass = "wKVcDvbMvB"
print(dbpass)
#for dev
public_key = "keu publci"
private_key = "9097bd082"
role_name = "readWriteAnyDatabase" 
project_id = "5f565163e2f68"


# #for prod
# project_id = "638f1160b957145caf9d0129"

username = "chaitanyagolhar"
#role_name can be readAnyDatabase (prod) or readWriteAnyDatabase (dev)
# role_name = "readAnyDatabase" 
create_or_update_mongo_user(public_key, private_key, project_id, username, dbpass, role_name)