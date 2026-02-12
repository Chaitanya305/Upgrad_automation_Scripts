#!/bin/bash

CLIENT_ID="5008a1d6a3d4cd990"
TENANT_ID="2e08a2a8-a03d-e078b350caaa"
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
#SHARED_FOLDER_NAME="Periyar - SCORM and Videos"
SHARED_FOLDER_NAME="Alagappa - SCORM and Videos"
#SHARED_FOLDER_NAME="onedrive_poc"
SHARED_ITEMS=$(curl -s -H "Authorization: Bearer $ACCESS_TOKEN" \
    "https://graph.microsoft.com/v1.0/me/drive/sharedWithMe")

DRIVE_ID=$(echo "$SHARED_ITEMS" | jq -r ".value[] | select(.name==\"$SHARED_FOLDER_NAME\") | .remoteItem.parentReference.driveId")
ITEM_ID=$(echo "$SHARED_ITEMS" | jq -r ".value[] | select(.name==\"$SHARED_FOLDER_NAME\") | .remoteItem.id")

if [[ -z "$DRIVE_ID" || -z "$ITEM_ID" ]]; then
    echo "❌ Could not find shared folder named '$SHARED_FOLDER_NAME'"
    exit 1
fi

upload_file() {
    FILE_PATH="$1"
    FILE_NAME=$(basename "$FILE_PATH")
    FILE_DIR=$(dirname "$FILE_PATH")
    echo "file path is $FILE_PATH"
    #check if file has space in it
    if [[ "$FILE_NAME" == *" "* ]]; then
        echo "old path : $FILE_PATH"
        echo "file name contains a space updating file name as below"
        UPDATED_FILE=$(echo "$FILE_NAME" | sed 's/ /_/g')
        echo "Updated path: $FILE_DIR/$UPDATED_FILE"
        mv "$FILE_PATH" "$FILE_DIR"/"$UPDATED_FILE"
    else
        UPDATED_FILE="$FILE_NAME"
    fi
    if [[ "$FILE_DIR" == *" "* ]]; then
        UPDATED_FILE_DIR=$(echo "$FILE_DIR" | sed 's/ /_/g')
    else
        UPDATED_FILE_DIR="$FILE_DIR"
    fi

    # Check if already uploaded using OneDrive API
    CHECK_URL="https://graph.microsoft.com/v1.0/drives/$DRIVE_ID/items/$ITEM_ID:/SCORMs/$UPDATED_FILE_DIR/$UPDATED_FILE"
    STATUS_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "Authorization: Bearer $ACCESS_TOKEN" \
        "$CHECK_URL")

    if [[ "$STATUS_CODE" == "200" ]]; then
        echo "⏩ Skipping $UPDATED_FILE (already uploaded)"
        return
    fi
    echo "Uploading $FILE_PATH"

    UPLOAD_URL="https://graph.microsoft.com/v1.0/drives/$DRIVE_ID/items/$ITEM_ID:/SCORMs/$UPDATED_FILE_DIR/$UPDATED_FILE:/content"


    RESPONSE=$(curl -s -X PUT \
        -H "Authorization: Bearer $ACCESS_TOKEN" \
        -H "Content-Type: application/octet-stream" \
        --data-binary @"$FILE_DIR"/"$UPDATED_FILE" \
        "$UPLOAD_URL")

    if echo "$RESPONSE" | jq -e '.id' > /dev/null; then
        echo "✅ Uploaded $FILE_DIR/$UPDATED_FILE"
    else
        echo "❌ Failed to upload $FILE_PATH"
        echo "$RESPONSE"
    fi
}

# Function to find all HTML files in current directory and subdirectories
find_html_files() {
    find . -type f -iname "*.html"
}

# Main script logic
echo "Searching for html files..."
found_any=false

find_html_files | while IFS= read -r FILE; do
    found_any=true
    upload_file "$FILE"
done

if ! $found_any; then
    echo "No html files found."
    exit 0
fi