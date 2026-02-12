#!/bin/bash

CLIENT_ID="5008ab1b-d9dd-494a-b88a-1d6a3d4cd990"
TENANT_ID="2e08a381-ba90-42a8-a03d-e078b350caaa"
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
SHARED_FOLDER_NAME="Periyar - SCORM and Videos"
SHARED_ITEMS=$(curl -s -H "Authorization: Bearer $ACCESS_TOKEN" \
    "https://graph.microsoft.com/v1.0/me/drive/sharedWithMe")

DRIVE_ID=$(echo "$SHARED_ITEMS" | jq -r ".value[] | select(.name==\"$SHARED_FOLDER_NAME\") | .remoteItem.parentReference.driveId")
ITEM_ID=$(echo "$SHARED_ITEMS" | jq -r ".value[] | select(.name==\"$SHARED_FOLDER_NAME\") | .remoteItem.id")

if [[ -z "$DRIVE_ID" || -z "$ITEM_ID" ]]; then
    echo "❌ Could not find shared folder named '$SHARED_FOLDER_NAME'"
    exit 1
fi

# Upload function
upload_file() {
    FILE_PATH="$1"
    FILE_NAME=$(basename "$FILE_PATH")
    echo "Uploading $FILE_PATH..."

    UPLOAD_URL="https://graph.microsoft.com/v1.0/drives/$DRIVE_ID/items/$ITEM_ID:/SCORMs/$FILE_PATH:/content"

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

# upload folder 
# upload_folder() {
#     LOCAL_FOLDER_PATH="$1"
#     REMOTE_PARENT_ID="$2"

#     for ENTRY in "$LOCAL_FOLDER_PATH"/*; do
#         ENTRY_NAME=$(basename "$ENTRY")

#         if [ -f "$ENTRY" ]; then
#             echo "Uploading file $ENTRY_NAME..."

#             UPLOAD_URL="https://graph.microsoft.com/v1.0/drives/$DRIVE_ID/items/$REMOTE_PARENT_ID:/$ENTRY_NAME:/content"

#             RESPONSE=$(curl -s -X PUT \
#                 -H "Authorization: Bearer $ACCESS_TOKEN" \
#                 -H "Content-Type: application/octet-stream" \
#                 --data-binary @"$ENTRY" \
#                 "$UPLOAD_URL")

#             if echo "$RESPONSE" | jq -e '.id' > /dev/null; then
#                 echo "✅ Uploaded $ENTRY_NAME"
#             else
#                 echo "❌ Failed to upload $ENTRY_NAME"
#                 echo "$RESPONSE"
#             fi

#         elif [ -d "$ENTRY" ]; then
#             echo "Creating folder $ENTRY_NAME..."

#             CREATE_FOLDER_PAYLOAD="{\"name\": \"$ENTRY_NAME\", \"folder\": {}, \"@microsoft.graph.conflictBehavior\": \"rename\"}"

#             CREATE_RESPONSE=$(curl -s -X POST \
#                 -H "Authorization: Bearer $ACCESS_TOKEN" \
#                 -H "Content-Type: application/json" \
#                 -d "$CREATE_FOLDER_PAYLOAD" \
#                 "https://graph.microsoft.com/v1.0/drives/$DRIVE_ID/items/$REMOTE_PARENT_ID/children")

#             NEW_FOLDER_ID=$(echo "$CREATE_RESPONSE" | jq -r '.id')

#             if [ -z "$NEW_FOLDER_ID" ] || [ "$NEW_FOLDER_ID" == "null" ]; then
#                 echo "❌ Failed to create folder $ENTRY_NAME"
#                 echo "$CREATE_RESPONSE"
#             else
#                 echo "📁 Entering folder $ENTRY_NAME..."
#                 upload_folder "$ENTRY" "$NEW_FOLDER_ID"  # Pass the new folder ID for recursion
#             fi
#         fi
#     done
# }

# create_folder() {
#     LOCAL_FOLDER_PATH="$1"
#     FOLDER_NAME=$(basename "$LOCAL_FOLDER_PATH")
#     CREATE_FOLDER_PAYLOAD="{\"name\": \"$FOLDER_NAME\", \"folder\": {}, \"@microsoft.graph.conflictBehavior\": \"rename\"}"

#     CREATE_RESPONSE=$(curl -s -X POST \
#         -H "Authorization: Bearer $ACCESS_TOKEN" \
#         -H "Content-Type: application/json" \
#         -d "$CREATE_FOLDER_PAYLOAD" \
#         "https://graph.microsoft.com/v1.0/drives/$DRIVE_ID/items/$ITEM_ID/children")

#     NEW_FOLDER_ID=$(echo "$CREATE_RESPONSE" | jq -r '.id')

#     if [ -z "$NEW_FOLDER_ID" ] || [ "$NEW_FOLDER_ID" == "null" ]; then
#         echo "❌ Failed to create folder $FOLDER_NAME"
#         echo "$CREATE_RESPONSE"
#     else
#         echo "📂 Uploading contents of $FOLDER_NAME recursively..."
#         upload_folder "$FILE" "$NEW_FOLDER_ID"
#     fi
# }

# Main code
if [ "$#" -eq 0 ]; then
    echo "Usage: $0 <file1> <file2> ... <fileN>"
    exit 1
fi

for FILE in "$@"; do
    if [[ -f "$FILE" ]]; then
        upload_file "$FILE"
    # elif [[ -d "$FILE" ]]; then
    #     create_folder "$FILE"
    else
        echo "Skipping $FILE – not a file"
    fi
done

echo "All uploads completed!"
