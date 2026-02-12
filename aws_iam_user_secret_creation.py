import boto3
import botocore.exceptions
import subprocess

#setting profiles
def profile_setter(user_name):
    account_ids = ["954772230024", "122610519847", "861276124837", "535002871556", "717279695343", "202533495773", "039612850873", "890742599999", "491085420150", "345594584986", "597088024596", "050451378467", "443370702768", "833192497705"]
    result = {}
    for account_id in account_ids:
        print("Starting for ", account_id)
        if account_id == "443370702768":
            print("Degrees Common profile set using default creds set")
            profile = "default"
        else:
            role = "arn:aws:iam::{}:role/aws-security-reports".format(account_id)
            role_output = subprocess.call("aws sts assume-role --role-arn {} --role-session-name AWSCLI-session".format(role), shell=True)
            access_key_id = subprocess.call("echo {} | jq -r '.Credentials.AccessKeyId'".format(role_output), shell=True)
            secret_access_key = subprocess.call("echo {} | jq -r '.Credentials.SecretAccessKey'".format(role_output), shell=True)
            session_token = subprocess.call("echo {} | jq -r '.Credentials.SessionToken'".format(role_output), shell=True)
            subprocess.call("aws configure set aws_access_key_id {} --profile {}".format(access_key_id, account_id), shell=True)
            subprocess.call("aws configure set aws_secret_access_key {} --profile {}".format(secret_access_key, account_id), shell=True)
            subprocess.call("aws configure set aws_session_token {} --profile {}".format(session_token, account_id), shell=True)
            subprocess.call("aws configure set region ap-souht-1 --profile {}".format(account_id), shell=True)
            profile = account_id

        #now do user creation and role attached task
        session = boto3.Session(profile_name=profile, region_name='ap-south-1')
        iam = session.client('iam')
        try:
            #check if user exist or not
            iam.get_user(
                UserName = user_name
            )
            print("User is present")
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchEntity':
                print("User does not exist")
                #create user
                user_response = iam.create_user(
                    UserName = user_name,
                    Tags=[
                        {
                            'Key': 'CreatedVia',
                            'Value': 'ZeroOps'
                        },
                    ]
                )
                print("user name is: ", user_response['User']['UserName'])
        #create acces key only if not present
        #list access keys
        access_keys = iam.list_access_keys(UserName = user_name)
        if len(access_keys['AccessKeyMetadata']) < 1:
            #Create Access and secert keys
            acces_keys = iam.create_access_key( UserName = user_name)
            #attach policy to user
            policy_arn = "arn:aws:iam::{}:policy/developer-local-access".format(account_id)
            iam.attach_user_policy(UserName=user_name, PolicyArn=policy_arn)
            result[account_id] = {'aws_access_key_id': acces_keys['AccessKey']['AccessKeyId'], 'aws_secret_access_key': acces_keys['AccessKey']['SecretAccessKey']}
            # print("Access key id is: ", acces_keys['AccessKey']['AccessKeyId'])
            # print("Secret Access key is :", acces_keys['AccessKey']['SecretAccessKey'])
            return result
        else:
            print("Access key already exist")
            result[account_id] = {'aws_access_key_id': "Already Exist", 'aws_secret_access_key': 'Already Exist'}
            return result

def create_user(user_name):
    iam = boto3.client('iam')
    try:
        #check if user exist or not
        iam.get_user(
            UserName = user_name
        )
        print("User is present")
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchEntity':
            print("User does not exist")
            #create user
            user_response = iam.create_user(
                UserName = user_name,
                Tags=[
                    {
                        'Key': 'CreatedVia',
                        'Value': 'ZeroOps'
                    },
                ]
            )
            print("user name is: ", user_response['User']['UserName'])
    #create acces key only if not present
    #list access keys
    access_keys = iam.list_access_keys(UserName = user_name)
    if len(access_keys['AccessKeyMetadata']) < 1:
        #Create Access and secert keys
        acces_keys = iam.create_access_key( UserName = user_name)
        #attach policy to user
        policy_arn = "arn:aws:iam::097085170336:policy/upgrad-aadhar-pocs"
        iam.attach_user_policy(UserName=user_name, PolicyArn=policy_arn)
        print("Access key id is: ", acces_keys['AccessKey']['AccessKeyId'])
        print("Secret Access key is :", acces_keys['AccessKey']['SecretAccessKey'])
    else:
        print("Access key already exist")


create_user("zeroops-poc-user")