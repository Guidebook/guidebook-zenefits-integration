import os
import json
import requests
import boto3
import ssm_utils
import customlist_data_builder

# This lambda triggers when an existing employee
# modifies their data in Zenefits.  The new data 
# will be written to the appropriate Guide in Builder
def lambda_handler(event, context):
    try:
        # Fetch the Builder API key, the guide ID of the guide where the content
        # is published, and the custom list ID that the items are associated with
        api_key, guide_id, employee_customlist_id = ssm_utils.fetch_ssm_params()

        employee_data = event['data']['data'][0]
        customlist_data = customlist_data_builder.build(employee_data, guide_id)

        # Fetch the existing CustomListItem from Builder by filtering on the import_id field.
        # This is needed to obtain the CustomListItem.id, which is required in the PATCH request
        custom_list_items_url = 'https://builder.guidebook.com/open-api/v1/custom-list-items/?guide={}&custom_lists={}&import_id={}'.format(
            guide_id, employee_customlist_id, data['id'])
        response = requests.get(custom_list_items_url, headers={
                                'Authorization': 'JWT ' + api_key})
        custom_list_item = json.loads(response.content)['results'][0]
        #TODO how to handle the case if there are duplicates ^

        # Update the existing CustomListItem
        url = 'https://builder.guidebook.com/open-api/v1/custom-list-items/{}/'.format(
            custom_list_item['id'])
        requests.patch(url, data=customlist_data, headers={
                       'Authorization': 'JWT ' + api_key})

        # Publish the changes
        publish_url = 'https://builder.guidebook.com/open-api/v1/guides/{}/publish/'.format(guide_id)
        requests.post(publish_url, headers={'Authorization': 'JWT ' + api_key})

    except:
        print('Unable to update data for event {}'.format(event))

    # Always return 200 so Zenefits doesn't keep retrying
    return {
        'statusCode': 200
    }
