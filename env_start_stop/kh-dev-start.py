import json
import boto3
import os
import botocore
import datetime
import pymysql

def lambda_handler(event, context):
    list1 = os.environ.get("ASGGroups").split(",")
    snsclient = boto3.client('sns')
    dbclient = boto3.client('dynamodb')
    asgclient = boto3.client('autoscaling')
    response = asgclient.describe_auto_scaling_groups(
        AutoScalingGroupNames=list1,
        MaxRecords=100
    )
    funcname = os.environ['AWS_LAMBDA_FUNCTION_NAME']
    timec = datetime.datetime.now()
    timei = timec + datetime.timedelta(0,19800)
    now = timei.strftime("%d/%m/%Y %H:%M")
    listasg = response["AutoScalingGroups"]
    try: 
        for i in listasg:
            asgvar = i["AutoScalingGroupName"]
            asgvar = str(asgvar)
            if "spinnaker" in asgvar:
                continue
            
            dbresponse = dbclient.get_item(
                TableName='autoscalinggroup',
                Key={'asgname': {'S': asgvar}}
                ) 
            print(dbresponse)
            print(asgvar)
            if "Item" in dbresponse:
                minsize = int(dbresponse["Item"]["min"]["N"])
                maxsize = int(dbresponse["Item"]["max"]["N"])
                dessize = int(dbresponse["Item"]["desired"]["N"])
            
                resupdate = asgclient.update_auto_scaling_group(
                    AutoScalingGroupName=asgvar,
                    MinSize=minsize,
                    MaxSize=maxsize,
                    DesiredCapacity=dessize
                )

        messagesns = funcname + " executed successfully at " + str(now)
        print(messagesns)
        
    except Exception as e:
        print("exception occured : ",e)
        messagesns = "<!channel>"+" "+funcname+ " failed with error : "+ str(e) + " at "+ str(now)
        print(messagesns)

    #update db values
    connection = pymysql.connect(
        host='zeroops-db.upgrad.com', 
        user='root',
        password='BJLXQYH',
        database='env_uptime',
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        with connection.cursor() as cursor:
            #update query
            sql = """
            UPDATE prism_env_status
            SET env_status = %s
            WHERE environment = %s
            """
            values = (1, 'dev')
            cursor.execute(sql, values)

        # Commit the transaction
        connection.commit()
        print("Update successful.")

    finally:
        connection.close()
