import json
import boto3
import os
import botocore
import datetime

def lambda_handler(event, context):
    list1 = os.environ.get("ASGGroups").split(",")
    print(list1)
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
            if "spinnaker" in asgvar:
                continue
            if i["MaxSize"] != 0:
                minasgsize = i["MinSize"]
                minasgsize = str(minasgsize)
                maxasgsize = i["MaxSize"]
                maxasgsize = str(maxasgsize)
                desasgsize = i["DesiredCapacity"]
                desasgsize = str(desasgsize)
    
                dbresponse = dbclient.put_item(
                    TableName='autoscalinggroup',
                    Item={'asgname':{'S':asgvar},'desired':{'N':desasgsize},'min':{'N':minasgsize},'max':{'N':maxasgsize}}
                    )
                print(dbresponse)
                resupdate = asgclient.update_auto_scaling_group(
                    AutoScalingGroupName=asgvar,
                    MinSize=0,
                    MaxSize=0,
                    DesiredCapacity=0
                )
            else:
                print("ASG size already 0, so won't update")
                
        messagesns = funcname + " executed successfully at " + str(now)
        print(messagesns)


    except Exception as e:
        print("exception occured : ",e)
        messagesns = "<!channel>"+" "+funcname+ " failed with error : "+ str(e) + " at "+ str(now)
        print(messagesns)
