previous_generation_instance_types = ['m1.medium', 'm1.large', 'm1.xlarge', 'm3.medium', 'm3.large', 'm3.xlarge', 'm3.2xlarge', 'm4.large', 'm4.xlarge', 'm4.2xlarge', 'm4.4xlarge', 'm4.10xlarge', 'm4.16xlarge', 'c1.medium', 'c1.xlarge', 'c2.8xlarge', 'c3.large', 'c3.xlarge', 'c3.2xlarge', 'c3.4xlarge', 'c3.8xlarge', 'c4.large', 'c4.xlarge', 'c4.2xlarge', 'c4.4xlarge', 'c4.8xlarge', 'm2.xlarge', 'm2.2xlarge', 'm2.4xlarge', 'r3.large', 'r3.xlarge', 'r3.2xlarge', 'r3.4xlarge', 'r3.8xlarge', 'r4.large', 'r4.xlarge', 'r4.2xlarge', 'r4.4xlarge', 'r4.8xlarge', 'r4.16xlarge', 'i2.xlarge', 'i2.2xlarge', 'i2.4xlarge', 'i2.8xlarge', 't1.micro']

previous_generation_db_instance_types= ['db.m1.small', 'db.m1.medium', 'db.m1.large', 'db.m1.xlarge', 'db.m3.medium', 'db.m3.large', 'db.m3.xlarge', 'db.m3.2xlarge', 'db.m2.xlarge', 'db.m2.2xlarge', 'db.m2.4xlarge', 'db.r3.large', 'db.r3.xlarge', 'db.r3.2xlarge', 'db.r3.4xlarge', 'db.r3.8xlarge', 'db.t2.micro', 'db.t2.small', 'db.t2.medium', 'db.t2.large', 'db.t2.xlarge', 'db.t2.2xlarge', 'db.m4.large', 'db.m4.xlarge', 'db.m4.2xlarge', 'db.m4.4xlarge', 'db.m4.10xlarge', 'db.m4.16xlarge', 'db.r4.large', 'db.r4.xlarge', 'db.r4.2xlarge', 'db.r4.4xlarge', 'db.r4.8xlarge', 'db.r4.16xlarge', 'db.r3.large', 'db.r3.xlarge', 'db.r3.2xlarge', 'db.r3.4xlarge', 'db.r3.8xlarge']  

previous_generation_ElastiCache_instance_types = ['cache.m1.small', 'cache.m1.medium', 'cache.m1.large', 'cache.m1.xlarge', 'cache.m3.medium', 'cache.m3.large', 'cache.m3.xlarge', 'cache.m3.2xlarge', 'cache.m2.xlarge', 'cache.m2.2xlarge', 'cache.m2.4xlarge', 'cache.r3.large', 'cache.r3.xlarge', 'cache.r3.2xlarge', 'cache.r3.4xlarge', 'cache.r3.8xlarge' 'cache.c1.xlarge', 'cache.t1.micro']

previous_generation_opensearch_instance_types =['c4.large.search', 'c4.xlarge.search', 'c4.2xlarge.search', 'c4.4xlarge.search', 'c4.8xlarge.search', 'i2.xlarge.search', 'i2.2xlarge.search', 'm3.medium.search', 'm3.large.search', 'm3.xlarge.search', 'm3.2xlarge.search', 'm4.large.search', 'm4.xlarge.search', 'm4.2xlarge.search', 'm4.4xlarge.search', 'm4.10xlarge.search', 'r3.large.search', 'r3.xlarge.search', 'r3.2xlarge.search', 'r3.4xlarge.search', 'r3.8xlarge.search', 'r4.large.search', 'r4.xlarge.search', 'r4.2xlarge.search', 'r4.4xlarge.search', 'r4.8xlarge.search', 'r4.16xlarge.search', 't2.micro.search', 't2.small.search', 't2.medium.search']


import boto3
import numpy as np
from datetime import datetime, timedelta, timezone

cloudwatch = boto3.client('cloudwatch')

def metrics_check(instance_id, metric_name, statistics, unit, period, daily, namespace, dim_name):
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=15)
    metrics = cloudwatch.get_metric_statistics(
        Period=period,  # data points interval
        StartTime=start_time,
        EndTime=end_time,
        MetricName=metric_name,
        Namespace=namespace,
        Statistics=[statistics],
        Dimensions=[{'Name': dim_name, 'Value': instance_id}],
        Unit = unit
    )
    if daily:
        return [datapoint[statistics] for datapoint in metrics['Datapoints']]
    else:
        return metrics['Datapoints']
    

def p99_check(instance_id, threshold, metric_values):
    P99_THRESHOLD = threshold
    if metric_values:
        # Calculate P99 CPU utilization
        p99_value = np.percentile(metric_values, 99) 
        print(f'p99 value for {instance_id}: ',p99_value)
        # Check for the threshold
        if p99_value < P99_THRESHOLD:
            return True
        else:
            return False
