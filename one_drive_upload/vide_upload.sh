#!/bin/bash

CLIENT_ID="5008ab3d4cd990"
TENANT_ID="2e08a3878b350caaa"
SCOPE="Files.ReadWrite.All offline_access"
AUTH_URL="https://login.microsoftonline.com/$TENANT_ID/oauth2/v2.0/devicecode"
TOKEN_URL="https://login.microsoftonline.com/$TENANT_ID/oauth2/v2.0/token"

echo "Getting device code..."
RESPONSE=$(curl -s -X POST -d "client_id=$CLIENT_ID&scope=$SCOPE" "$AUTH_URL")

DEVICE_CODE=$(echo "$RESPONSE" | jq -r '.device_code')
MESSAGE=$(echo "$RESPONSE" | jq -r '.message')

echo "$MESSAGE"
echo "Waiting for authentication..."

while :; do
    TOKEN_RESPONSE=$(curl -s -X POST -d "grant_type=device_code&client_id=$CLIENT_ID&device_code=$DEVICE_CODE" "$TOKEN_URL")
    if echo "$TOKEN_RESPONSE" | grep -q 'access_token'; then
        ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.access_token')
        break
    elif echo "$TOKEN_RESPONSE" | grep -q 'authorization_pending'; then
        sleep 5
    else
        echo "Error while fetching token:"
        echo "$TOKEN_RESPONSE"
        exit 1
    fi
done

# Look for the shared folder by name
SHARED_FOLDER_NAME="onedrive_poc"
SHARED_ITEMS=$(curl -s -H "Authorization: Bearer $ACCESS_TOKEN" \
    "https://graph.microsoft.com/v1.0/me/drive/sharedWithMe")

DRIVE_ID=$(echo "$SHARED_ITEMS" | jq -r ".value[] | select(.name==\"$SHARED_FOLDER_NAME\") | .remoteItem.parentReference.driveId")
ITEM_ID=$(echo "$SHARED_ITEMS" | jq -r ".value[] | select(.name==\"$SHARED_FOLDER_NAME\") | .remoteItem.id")

if [[ -z "$DRIVE_ID" || -z "$ITEM_ID" ]]; then
    echo "❌ Could not find shared folder named '$SHARED_FOLDER_NAME'"
    exit 1
fi

# Get the list of files already in the /Videos folder
# Step 1: Get the ID of the "Videos" folder inside the shared folder
VIDEOS_FOLDER_ID=$(curl -s -H "Authorization: Bearer $ACCESS_TOKEN" \
    "https://graph.microsoft.com/v1.0/drives/$DRIVE_ID/items/$ITEM_ID/children" | \
    jq -r '.value[] | select(.name == "Videos") | .id')

if [[ -z "$VIDEOS_FOLDER_ID" ]]; then
    echo "❌ 'Videos' folder not found inside shared folder."
    exit 1
fi

# Step 2: Get list of existing files inside the "Videos" folder
EXISTING_FILES=$(curl -s -H "Authorization: Bearer $ACCESS_TOKEN" \
    "https://graph.microsoft.com/v1.0/drives/$DRIVE_ID/items/$VIDEOS_FOLDER_ID/children" | \
    jq -r '.value[]?.name')

echo "✅ Retrieved list of existing files in /Videos"
# Upload function
upload_file() {
    FILE_PATH="$1"
    FILE_NAME=$(basename "$FILE_PATH")

    # Check if already uploaded
    if echo "$EXISTING_FILES" | grep -Fxq "$FILE_NAME"; then
        echo "⏩ Skipping $FILE_NAME (already uploaded)"
        return
    fi

    echo "Uploading $FILE_PATH"

    UPLOAD_URL="https://graph.microsoft.com/v1.0/drives/$DRIVE_ID/items/$ITEM_ID:/Videos/$FILE_PATH:/content"

    RESPONSE=$(curl -s -X PUT \
        -H "Authorization: Bearer $ACCESS_TOKEN" \
        -H "Content-Type: application/octet-stream" \
        --data-binary @"$FILE_PATH" \
        "$UPLOAD_URL")

    if echo "$RESPONSE" | jq '.id' > /dev/null; then
        echo "✅ Uploaded $FILE_PATH"
    else
        echo "❌ Failed to upload $FILE_PATH"
        echo "$RESPONSE"
    fi
}

# Function to find all HTML files in current directory and subdirectories
find_html_files() {
    find . -type f -iname "*.mp4"
}

# Main script logic
echo "Searching for mp4 files..."
HTML_FILES=$(find_html_files)

if [[ -z "$HTML_FILES" ]]; then
    echo "No mp4 files found."
    exit 0
fi

while IFS= read -r FILE; do
    upload_file "$FILE"
done <<< "$HTML_FILES"

echo "All uploads completed!"