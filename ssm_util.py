import os
import boto3


# Util for fetching the params stored in SSM (Parameter Store)
def fetch_ssm_params():
    region = os.environ['AWS_REGION']
    client = boto3.client('ssm', region_name=region)
    api_key = client.get_parameter(
        Name='/lambdas/zenefitswebhookreceiver/api_key', WithDecryption=False)['Parameter']['Value']
    guide_id = client.get_parameter(
        Name='/lambdas/zenefitswebhookreceiver/guide_id', WithDecryption=False)['Parameter']['Value']
    employee_customlist_id = client.get_parameter(
        Name='/lambdas/zenefitswebhookreceiver/employee_customlist_id', WithDecryption=False)['Parameter']['Value']
    return api_key, guide_id, employee_customlist_id