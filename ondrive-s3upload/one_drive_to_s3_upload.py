import requests
import boto3
import os
# Setup
CLIENT_ID = "5008ab1a-1d6a3d4cd990"
TENANT_ID = "2e08a381d-e078b350caaa"
SCOPE = "Files.ReadWrite.All offline_access"
S3_BUCKET_NAME = 'poc-upgrad-bucket'
FOLDER_NAME = 'onedrive_poc'

# OAuth Device Code Flow
device_code_url = f'https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/devicecode'
token_url = f'https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token'

resp = requests.post(device_code_url, data={'client_id': CLIENT_ID, 'scope': SCOPE})
resp.raise_for_status()
data = resp.json()

print(data['message'])  # Ask user to authenticate
device_code = data['device_code']

# Poll for token
access_token = None
import time
while not access_token:
    resp = requests.post(token_url, data={
        'grant_type': 'device_code',
        'client_id': CLIENT_ID,
        'device_code': device_code
    })
    data = resp.json()
    if 'access_token' in data:
        access_token = data['access_token']
    elif data.get('error') == 'authorization_pending':
        time.sleep(5)
    else:
        raise Exception(f"Token error: {data}")

headers = {'Authorization': f'Bearer {access_token}'}

# Find the base folder
root_resp = requests.get(
    f"https://graph.microsoft.com/v1.0/me/drive/root/children",
    headers=headers).json()

base_folder = next((item for item in root_resp['value'] if item['name'] == FOLDER_NAME and 'folder' in item), None)

if not base_folder:
    print(f"❌ Folder '{FOLDER_NAME}' not found in root.")
    exit(1)
base_folder_id = base_folder['id']

# Upload to S3 using streaming
s3_client = boto3.client('s3')

# Recursive function to traverse and upload
def process_folder(folder_id, current_path=""):
    url = f"https://graph.microsoft.com/v1.0/me/drive/items/{folder_id}/children"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    items = resp.json()['value']

    for item in items:
        item_name = item['name']
        item_path = os.path.join(current_path, item_name)

        if 'folder' in item:
            print(f"Entering folder: {item_path}")
            # Optional: create "folder" key in S3 to mimic folder structure
            s3_client.put_object(Bucket=S3_BUCKET_NAME, Key=item_path + '/')
            process_folder(item['id'], item_path)
        elif 'file' in item:
            download_url = item.get('@microsoft.graph.downloadUrl')
            if not download_url:
                print(f"⚠️ No download URL for {item_path}")
                continue

            print(f"⬆️ Uploading {item_path} to S3...")
            with requests.get(download_url, stream=True) as r:
                r.raise_for_status()
                s3_client.upload_fileobj(r.raw, S3_BUCKET_NAME, item_path)
            print(f"✅ Uploaded {item_path}")
        else:
            print(f"⏭️ Skipping unknown item: {item_name}")

# Start recursion from base folder
print(f"🚀 Starting upload from OneDrive folder '{FOLDER_NAME}'...")
process_folder(base_folder_id)
print("🎉 Upload complete!")