import boto3
import datetime

iam = boto3.client('iam')
DAYS_THRESHOLD = 90
def lambda_handler(event, context):
    try:
        # Get current date
        now = datetime.datetime.now(datetime.timezone.utc)
        # List all IAM users
        paginator = iam.get_paginator('list_users')
        for response in paginator.paginate():
            for user in response['Users']:
                user_name = user['UserName']
                print(user_name)
                # Check if username starts with "developer" and not developer-local-access
                if user_name.startswith('developer') and user_name!="developer-local-access":
                    # List access keys for this user
                    keys = iam.list_access_keys(UserName=user_name)['AccessKeyMetadata']
                    for key in keys:
                        key_id = key['AccessKeyId']
                        create_date = key['CreateDate']
                        age = (now - create_date).days
                        print("age for user {} is {}".format(user_name, age))
                        if age >= DAYS_THRESHOLD:
                            print(f"Deleting key {key_id} (age: {age} days) for user {user_name}")
                            iam.delete_access_key(UserName=user_name, AccessKeyId=key_id)
                            print("Keys deletes successfully")
        return {
            'statusCode': 200,
            'body': 'Old keys deleted successfully'
        }
    except Exception as e:
        print("Error is",e)
        return {
            'statusCode': 500,
            'body': f'Error occurred: {str(e)}'
        }
