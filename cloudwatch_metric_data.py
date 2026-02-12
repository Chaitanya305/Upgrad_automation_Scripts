import boto3
from datetime import datetime, timedelta, timezone

def get_cloudwatch_metrics(instance_id):
    cloudwatch = boto3.client('cloudwatch', region_name="us-east-1")

    end = datetime.now(timezone.utc)
    start = end - timedelta(minutes=30)

    def fetch_metric(metric_name, stat='Maximum'):
        response = cloudwatch.get_metric_statistics(
            Namespace='AWS/RDS',
            MetricName=metric_name,
            Dimensions=[{'Name': name, 'Value': instance_id}],
            StartTime=start,
            EndTime=end,
            Period=300,
            Statistics=[stat]
        )
        datapoints = sorted(response['Datapoints'], key=lambda x: x['Timestamp'], reverse=True)
        return datapoints[0][stat] if datapoints else None

    metrics = {
        "FreeStorageSpace": fetch_metric("FreeStorageSpace", "Maximum"),
        "CPUUtilization": fetch_metric("CPUUtilization", "Average"),
        "ReadIOPS": fetch_metric("ReadIOPS", "Average"),
        "WriteIOPS": fetch_metric("WriteIOPS", "Average"),
        "FreeableMemory": fetch_metric("FreeableMemory", "Average"),
        "DatabaseConnections": fetch_metric("DatabaseConnections", "Average")
    }
    return {"instance_id": instance_id, "metrics": metrics}