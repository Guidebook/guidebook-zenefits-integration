import os
import boto3


# Util for fetching the params stored in SSM (Parameter Store)
def fetch_ssm_params():
    region = os.environ["AWS_REGION"]
    client = boto3.client("ssm", region_name=region)

    # The api key used to send data to Builder
    api_key = client.get_parameter(
        Name="/lambdas/zenefitswebhookreceiver/api_key", WithDecryption=True
    )["Parameter"]["Value"]

    # The ids of the guides and custom lists that will be updated in Builder
    guide_and_list_ids = client.get_parameter(
        Name="/lambdas/zenefitswebhookreceiver/guide_and_list_ids", WithDecryption=False
    )["Parameter"]["Value"]
    guide_and_list_ids = list(eval(guide_and_list_ids))

    zenefits_app_key = client.get_parameter(
        Name="/lambdas/zenefitswebhookreceiver/zenefits_app_key", WithDecryption=True
    )["Parameter"]["Value"]

    return api_key, guide_and_list_ids, zenefits_app_key

