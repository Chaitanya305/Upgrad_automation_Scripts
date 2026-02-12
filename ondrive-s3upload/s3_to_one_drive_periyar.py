import boto3
import requests
import json
import time

# ==============================================================
# CONFIG - CHANGE THESE FOR EACH RUN
# ==============================================================

CLIENT_ID = "5008ab1ba-1d6a3d4cd990"
TENANT_ID = "2e08a381-ba9-e078b350caaa"

# For NIU:
# SHARED_FOLDER_NAME = "NIU - LMS Backup"
# S3_BUCKET = "niu-prod-pedagogy"

# For Periyar:
SHARED_FOLDER_NAME = "Periyar University LMS Backup"
S3_BUCKET = "periyar-prod-pedagogy"

GRAPH_BASE = "https://graph.microsoft.com/v1.0"
AUTH_URL = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/devicecode"
TOKEN_URL = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"

# ==============================================================

class TokenManager:
    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = 0
    
    def get_token(self):
        """Get access token, refreshing if needed"""
        # Check if token is expired or will expire in next 5 minutes
        if time.time() >= (self.token_expiry - 300):
            if self.refresh_token:
                print("🔄 Refreshing access token...")
                self._refresh_access_token()
            else:
                print("🔑 Getting new access token...")
                self._get_new_token()
        
        return self.access_token
    
    def _get_new_token(self):
        """Get initial access token via device code flow"""
        print("🔑 Getting device code for login...")

        device = requests.post(
            AUTH_URL,
            data={"client_id": CLIENT_ID, "scope": "Files.ReadWrite.All offline_access"},
        ).json()

        print(f"\nPlease authenticate here: {device['message']}\n")

        while True:
            time.sleep(3)
            token = requests.post(
                TOKEN_URL,
                data={
                    "grant_type": "device_code",
                    "client_id": CLIENT_ID,
                    "device_code": device["device_code"],
                },
            ).json()

            if "access_token" in token:
                print("✅ Logged in successfully!")
                self.access_token = token["access_token"]
                self.refresh_token = token.get("refresh_token")
                # Token typically expires in 3600 seconds (1 hour)
                self.token_expiry = time.time() + token.get("expires_in", 3600)
                return

            elif token.get("error") != "authorization_pending":
                raise Exception(f"❌ Token error: {token}")
    
    def _refresh_access_token(self):
        """Refresh access token using refresh token"""
        response = requests.post(
            TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "client_id": CLIENT_ID,
                "refresh_token": self.refresh_token,
            },
        ).json()
        
        if "access_token" in response:
            self.access_token = response["access_token"]
            # Update refresh token if a new one is provided
            if "refresh_token" in response:
                self.refresh_token = response["refresh_token"]
            self.token_expiry = time.time() + response.get("expires_in", 3600)
            print("✅ Token refreshed successfully!")
        else:
            print("❌ Failed to refresh token, getting new token...")
            self._get_new_token()


def find_shared_folder(token_manager):
    print(f"\n🔍 Searching OneDrive using Search API for: {SHARED_FOLDER_NAME}")

    headers = {"Authorization": f"Bearer {token_manager.get_token()}", "Content-Type": "application/json"}

    body = {
        "requests": [
            {
                "entityTypes": ["driveItem"],
                "query": {"queryString": SHARED_FOLDER_NAME},
                "size": 5,
                "fields": ["id", "name", "parentReference"]
            }
        ]
    }

    r = requests.post(f"{GRAPH_BASE}/search/query", headers=headers, json=body).json()

    try:
        hits = r["value"][0]["hitsContainers"][0]["hits"]
    except:
        print(json.dumps(r, indent=2))
        raise Exception("❌ Search API response invalid")

    for h in hits:
        item = h["resource"]

        name = item["name"]
        if name == SHARED_FOLDER_NAME:
            print("✅ Folder matched via search!")

            parent = item["parentReference"]
            drive_id = parent["driveId"]
            item_id = item["id"]

            print(f"📌 driveId = {drive_id}")
            print(f"📌 itemId  = {item_id}")

            return drive_id, item_id

    raise Exception(f"❌ Shared folder '{SHARED_FOLDER_NAME}' not found via search.")


def file_exists_on_onedrive(token_manager, drive_id, folder_id, file_path):
    """Check if a file already exists in OneDrive"""
    headers = {"Authorization": f"Bearer {token_manager.get_token()}"}
    
    url = f"{GRAPH_BASE}/drives/{drive_id}/items/{folder_id}:/{file_path}"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return True
    elif response.status_code == 404:
        return False
    else:
        return False


def ensure_folder_path(token_manager, drive_id, folder_id, file_path):
    """Create folder structure if it doesn't exist - with caching"""
    headers = {"Authorization": f"Bearer {token_manager.get_token()}"}
    
    # Split path into folders
    parts = file_path.split("/")
    
    # If there's only a filename (no folders), return the original folder_id
    if len(parts) <= 1:
        return folder_id
    
    # Navigate/create each folder in the path
    current_folder_id = folder_id
    current_path = ""
    
    for i, folder_name in enumerate(parts[:-1]):  # Exclude the filename
        current_path = "/".join(parts[:i+1])
        
        # Try to get folder by path first (faster than listing children)
        check_url = f"{GRAPH_BASE}/drives/{drive_id}/items/{folder_id}:/{current_path}"
        check_response = requests.get(check_url, headers=headers)
        
        if check_response.status_code == 200:
            # Folder exists
            current_folder_id = check_response.json()["id"]
            continue
        
        # Folder doesn't exist, need to create it
        # First, get parent folder ID
        if i == 0:
            parent_folder_id = folder_id
        else:
            parent_path = "/".join(parts[:i])
            parent_url = f"{GRAPH_BASE}/drives/{drive_id}/items/{folder_id}:/{parent_path}"
            parent_response = requests.get(parent_url, headers=headers)
            
            if parent_response.status_code == 200:
                parent_folder_id = parent_response.json()["id"]
            else:
                print(f"⚠️  Could not find parent folder: {parent_path}")
                return folder_id
        
        # Create the folder
        create_url = f"{GRAPH_BASE}/drives/{drive_id}/items/{parent_folder_id}/children"
        payload = {
            "name": folder_name,
            "folder": {},
            "@microsoft.graph.conflictBehavior": "rename"
        }
        
        create_response = requests.post(create_url, headers=headers, json=payload)
        
        if create_response.status_code in [200, 201]:
            current_folder_id = create_response.json()["id"]
            print(f"📁 Created folder: {current_path}")
        elif create_response.status_code == 409:
            # Folder already exists (race condition), try to get it
            time.sleep(0.5)
            check_response = requests.get(check_url, headers=headers)
            if check_response.status_code == 200:
                current_folder_id = check_response.json()["id"]
            else:
                print(f"⚠️  Folder conflict: {folder_name}")
        else:
            print(f"⚠️  Could not create folder: {folder_name} - Status: {create_response.status_code}")
            print(create_response.text)
    
    return current_folder_id


def create_upload_session(token_manager, drive_id, folder_id, file_path):
    headers = {"Authorization": f"Bearer {token_manager.get_token()}"}
    
    # Extract just the filename
    filename = file_path.split("/")[-1]
    
    # Ensure folder structure exists and get the target folder ID
    target_folder_id = ensure_folder_path(token_manager, drive_id, folder_id, file_path)
    
    # Create upload session using just the filename
    url = f"{GRAPH_BASE}/drives/{drive_id}/items/{target_folder_id}:/{filename}:/createUploadSession"

    payload = {
        "item": {
            "@microsoft.graph.conflictBehavior": "replace"
        }
    }

    response = requests.post(url, headers=headers, json=payload).json()

    if "uploadUrl" not in response:
        print("❌ Upload session error:")
        print(json.dumps(response, indent=2))
        raise Exception("Upload session creation failed")

    return response["uploadUrl"]


def upload_s3_to_onedrive(s3, bucket, key, upload_url):
    print(f"⬆️  Uploading: {key}")

    # Get file size first
    head = s3.head_object(Bucket=bucket, Key=key)
    file_size = head["ContentLength"]

    chunk_size = 10 * 1024 * 1024  # 10 MB

    start = 0
    while start < file_size:
        end = min(start + chunk_size - 1, file_size - 1)
        
        # Get the chunk data
        response = s3.get_object(Bucket=bucket, Key=key, Range=f"bytes={start}-{end}")
        chunk_data = response["Body"].read()
        
        actual_chunk_size = len(chunk_data)

        headers = {
            "Content-Length": str(actual_chunk_size),
            "Content-Range": f"bytes {start}-{end}/{file_size}",
        }

        r = requests.put(upload_url, data=chunk_data, headers=headers)

        if r.status_code not in [200, 201, 202]:
            print("❌ Chunk upload failed:")
            print(f"Status: {r.status_code}")
            print(r.text)
            raise Exception("Upload error")

        start = end + 1

    print(f"✅ Completed: {key}")


def get_all_s3_objects(s3, bucket):
    """Get ALL objects from S3 bucket using pagination"""
    print(f"📁 Scanning S3 bucket: {bucket}")
    
    all_objects = []
    continuation_token = None
    page = 1
    
    while True:
        if continuation_token:
            response = s3.list_objects_v2(
                Bucket=bucket,
                ContinuationToken=continuation_token
            )
        else:
            response = s3.list_objects_v2(Bucket=bucket)
        
        objects = response.get("Contents", [])
        all_objects.extend(objects)
        
        print(f"📄 Page {page}: Found {len(objects)} objects (Total so far: {len(all_objects)})")
        page += 1
        
        # Check if there are more objects
        if response.get("IsTruncated"):
            continuation_token = response.get("NextContinuationToken")
        else:
            break
    
    print(f"✅ Total objects found: {len(all_objects)}\n")
    return all_objects


def main():
    token_manager = TokenManager()

    drive_id, shared_folder_id = find_shared_folder(token_manager)

    s3 = boto3.client("s3")

    # Get ALL objects from S3 (with pagination)
    all_objects = get_all_s3_objects(s3, S3_BUCKET)

    uploaded_count = 0
    skipped_count = 0
    failed_count = 0

    for idx, obj in enumerate(all_objects, 1):
        key = obj["Key"]

        print(f"\n[{idx}/{len(all_objects)}] Processing: {key}")

        # Skip "folder" keys
        if key.endswith("/"):
            print(f"⏩ Skipping folder marker: {key}")
            continue

        upload_path = key.replace("\\", "/")

        # Check if file already exists on OneDrive
        if file_exists_on_onedrive(token_manager, drive_id, shared_folder_id, upload_path):
            print(f"⏭️  Skipping (already exists): {key}")
            skipped_count += 1
            continue

        try:
            # Create OneDrive upload session
            upload_url = create_upload_session(token_manager, drive_id, shared_folder_id, upload_path)

            # Upload from S3 → OneDrive
            upload_s3_to_onedrive(s3, S3_BUCKET, key, upload_url)
            uploaded_count += 1
            
        except Exception as e:
            print(f"❌ Failed to upload {key}: {e}")
            failed_count += 1
            continue

    print(f"\n{'='*60}")
    print(f"🎉 Upload complete!")
    print(f"{'='*60}")
    print(f"   ✅ Uploaded: {uploaded_count} files")
    print(f"   ⏭️  Skipped: {skipped_count} files (already existed)")
    print(f"   ❌ Failed: {failed_count} files")
    print(f"   📊 Total processed: {len(all_objects)} objects")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()