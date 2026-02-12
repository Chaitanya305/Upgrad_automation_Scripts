#!/bin/bash

#CLIENT_ID="5bd3ccf-a58a-5c41c852cc5f"
CLIENT_ID="5008a-1d6a3d4cd990"
SCOPE="Files.ReadWrite offline_access"
# AUTH_URL="https://login.microsoftonline.com/common/oauth2/v2.0/devicecode"
# TOKEN_URL="https://login.microsoftonline.com/common/oauth2/v2.0/token"
AUTH_URL="https://login.microsoftonline.com/2e08a381-ba90-42a8-a03d-e078b350caaa/oauth2/v2.0/devicecode"
TOKEN_URL="https://login.microsoftonline.com/2e08a381-ba90-42a8-a03d-e078b350caaa/oauth2/v2.0/token"

echo "Getting device code..."
RESPONSE=$(curl -s -X POST -d "client_id=$CLIENT_ID&scope=$SCOPE" "$AUTH_URL")

DEVICE_CODE=$(echo "$RESPONSE" | jq -r '.device_code')
USER_CODE=$(echo "$RESPONSE" | jq -r '.user_code')
VERIFICATION_URI=$(echo "$RESPONSE" | jq -r '.verification_uri')
MESSAGE=$(echo "$RESPONSE" | jq -r '.message')

if [[ "$DEVICE_CODE" == "null" || "$USER_CODE" == "null" ]]; then
    echo "Failed to get device code. Response:"
    echo "$RESPONSE"
    exit 1
fi

echo "$MESSAGE"
echo "Waiting for authentication..."

# Poll token endpoint until user authenticates
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

# Upload function
upload_file() {
    FILE_PATH="$1"
    if [ ! -f "$FILE_PATH" ]; then
        echo "Skipping invalid file: $FILE_PATH"
        return
    fi
    FILE_NAME=$(basename "$FILE_PATH")
    echo "Uploading $FILE_NAME..."

    RESPONSE=$(curl -s -X PUT \
        -H "Authorization: Bearer $ACCESS_TOKEN" \
        -H "Content-Type: application/octet-stream" \
        --data-binary @"$FILE_PATH" \
        "https://graph.microsoft.com/v1.0/me/drive/root:/onedrive_poc/$FILE_NAME:/content")

    if echo "$RESPONSE" | jq -e '.id' > /dev/null; then
        echo "✅ Uploaded $FILE_NAME"
    else
        echo "❌ Failed to upload $FILE_NAME"
        echo "$RESPONSE"
    fi
}

# Main logic
if [ "$#" -eq 0 ]; then
    echo "Usage: $0 <file1> <file2> ... <fileN>"
    exit 1
fi

for FILE in "$@"; do
    upload_file "$FILE"
done

echo "All uploads completed!"
