import json
import requests
import traceback

import ssm_util
import customlist_data_builder

# This lambda triggers when an existing employee
# modifies their data in Zenefits.  The new data 
# will be written to the appropriate Guide in Builder
def lambda_handler(event, context):
    try:
        # Fetch the Builder API key, the guide ID of the guide where the content
        # is published, and the custom list ID that the items are associated with
        api_key, guide_id, employee_customlist_id, zenefits_app_key = ssm_util.fetch_ssm_params()

        # Use the lambda event data to build a CustomListItem
        data = event['data']
        customlist_data = customlist_data_builder.build(data, guide_id, zenefits_app_key)

        # Fetch the existing CustomListItem from Builder by filtering on the import_id field.
        # This is needed to obtain the CustomListItem.id, which is required in the PATCH request
        custom_list_items_url = 'https://builder.guidebook.com/open-api/v1/custom-list-items?guide={}&custom_lists={}&import_id={}'.format(
            guide_id, employee_customlist_id, data['id'])
        response = requests.get(custom_list_items_url, headers={
                                'Authorization': 'JWT ' + api_key})
        custom_list_item = json.loads(response.content)['results'][0]
        #TODO how to handle the case if there are duplicates ^

        # Update the existing CustomListItem
        url = 'https://builder.guidebook.com/open-api/v1/custom-list-items/{}/'.format(
            custom_list_item['id'])
        patch_response = requests.patch(url, data=customlist_data, headers={
                       'Authorization': 'JWT ' + api_key})

        # Publish the changes
        publish_url = 'https://builder.guidebook.com/open-api/v1/guides/{}/publish/'.format(guide_id)
        requests.post(publish_url, headers={'Authorization': 'JWT ' + api_key})

    except Exception as e:
        print(e)
        traceback.print_exc()

    # Always return 200 so Zenefits doesn't keep retrying
    return {
        'statusCode': 200
    }
