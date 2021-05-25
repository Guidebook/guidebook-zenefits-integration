# About
This project contains code for syncing Zenefits HR data with a Guidebook Guide via webhooks.

# Setup
### What you will need
1. An [Amazon Web Services (AWS) account](https://aws.amazon.com/)
2. A Guide set up in [Builder](https://builder.guidebook.com/) with an empty CustomList
3. An API key from Builder
4. A Zenefits account
5. A Zenefits app key

## Environment Setup
1. Create a [virtualenv](https://virtualenv.pypa.io/en/stable/) and run `pip install -r requirements.txt` to get the package dependencies.

## Initial Data Load
This project uses webhooks in Zenefits to add, update and remove employees from a CustomList in Builder.  However, an initial data load must be performed to populate the guide with data.

**Steps to load data:**
1. Update all of the values in `settings.py` to your settings
2. Run `python data_loader.py` from within your virtualenv.

## Lambdas Setup
**Steps to setup lambdas:**
1. Login to your AWS account and create three new [lambdas](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html) 
2. Create [deployment packages](https://docs.aws.amazon.com/lambda/latest/dg/python-package-create.html#python-package-create-with-dependency) for each of the lambdas and either upload the package to AWS via the console or using [lambda-uploader](https://github.com/rackerlabs/lambda-uploader)
The lambdas are contained in:
 - `add_new_employee_webhook_receiver.py`
 - `remove_employee_webhook_receiver.py`
 - `update_existing_employee_webhook_receiver.py`
3. Create an [API Gateway](https://aws.amazon.com/api-gateway/) and add the three lambdas as resources
4. Add the following parameters to AWS Systems Manager (Parameter Store)

| Name | Type | Value |
| ----------- | ----------- | ----------- |
| `/lambdas/zenefitswebhookreceiver/api_key` | SecureString| Your Builder API key |
| `/lambdas/zenefitswebhookreceiver/guide_id` | String | Guide ID in Builder |
| `/lambdas/zenefitswebhookreceiver/employee_customlist_id` | String | The ID of your CustomList in Builder |
5. Deploy the lambdas and API Gateway


## Webhooks Setup
In order for the lambdas to receive data from Zenefits, several webhooks will need to be setup to push the data to our lambdas.
Login to your Zenefits account and create the following webhooks:
| Zenefits Events | Lambda |  
| ----------- | ----------- |  
| `people.did_change` | `update_existing_employee_webhook_receiver_lambda` |  
| `employments.did_terminate` | `remove_employee_webhook_receiver` |
|`employments.did_start`|`add_new_employee_webhook_receiver_lambda`|
More information about Zenefits events can be found [here](https://developers.zenefits.com/docs/events)


