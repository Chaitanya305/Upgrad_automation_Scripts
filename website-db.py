
import random
import string
from requests.auth import HTTPDigestAuth
import requests

def generate_password():
    # Choose from letters (a-z, A-Z) and digits (0-9)
    length = 10
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def create_or_update_mongo_user(public_key, private_key, project_id, username, password, role_name):
    base_url = "https://cloud.mongodb.com/api/atlas/v2"
    user_url = "{}/groups/{}/databaseUsers".format(base_url, project_id)
    
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
        update_url = "{}/admin/{}".format(user_url, username)
        update_payload = {
            "databaseName": "admin",
            "groupId": project_id,
            "username": username,
            "password": password,
            "roles": [
                {
                    "databaseName": "admin",
                    "roleName": role_name
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


MONGO_PUBLIC_KEY = "mongo pubic key"
MONGO_PRIVATE_KEY = "mong key"
#user creatiom
#get dev user_created
db_user_name = 'chaitanyagolhar'
dev_password = generate_password()
dev_project_id = "5f5b37fdf"
public_key = MONGO_PUBLIC_KEY
private_key = MONGO_PRIVATE_KEY
dev_role_name = "readWriteAnyDatabase"
create_or_update_mongo_user(public_key, private_key, dev_project_id, db_user_name, dev_password, dev_role_name)