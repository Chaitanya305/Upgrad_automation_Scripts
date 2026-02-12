import requests
import boto3

# Setup
CLIENT_ID = "5008ab1b-d9dd-494a-b88a-1d6a3d4cd990"
TENANT_ID = "2e08a381-ba90-42a8-a03d-e078b350caaa"
SCOPE = "Files.ReadWrite.All offline_access"
S3_BUCKET_NAME = 'poc-upgrad-bucket'
FOLDER_NAME = 'Videos'

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

# List files in Videos folder
list_url = f'https://graph.microsoft.com/v1.0/me/drive/root:/{FOLDER_NAME}:/children'
resp = requests.get(list_url, headers=headers)
resp.raise_for_status()
files = resp.json()['value']

# Upload to S3 using streaming
s3_client = boto3.client('s3')

for f in files:
    file_name = f['name']
    # if not file_name.lower().endswith('.html'):
    #     continue

    download_url = f['@microsoft.graph.downloadUrl']
    print(f"Streaming {file_name} from OneDrive to S3...")

    # Open a streaming GET request (do not load the whole file into memory)
    with requests.get(download_url, stream=True) as r:
        r.raise_for_status()
        s3_client.upload_fileobj(r.raw, S3_BUCKET_NAME, file_name)

    print(f"✅ Uploaded {file_name} to S3")

print("All files streamed directly to S3")
