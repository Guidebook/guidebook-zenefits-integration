import requests
import ssm_utils
import ssm_util

# Removes an employee from the guide
# once their employment has been terminated
def lambda_handler(event, context):
    try:
        # Fetch the Builder API key, the guide ID of the guide where the content
        # is published, and the custom list ID that the items are associated with
        api_key, guide_id, employee_customlist_id = ssm_utils.fetch_ssm_params()

        # Fetch the existing CustomListItem from Builder by filtering on the import_id field.
        # This is needed to obtain the CustomListItem.id, which is required in the PATCH request
        custom_list_items_url = 'https://builder.guidebook.com/open-api/v1/custom-list-items/?guide={}&custom_lists={}&import_id={}'.format(
            guide_id, employee_customlist_id, data['id'])
        response = requests.get(custom_list_items_url, headers={
                                'Authorization': 'JWT ' + api_key})
        custom_list_items = json.loads(response.content)['results']

        # If there is more than one matching CustomListItem, delete them all
        for custom_list_item in custom_list_items:
            delete_url = 'https://builder.guidebook.com/open-api/v1/custom-list-items/{}/'.format(custom_list_item['id'])
            requests.delete(delete_url, 'Authorization': 'JWT ' + api_key})

        # Publish the changes
        publish_url = 'https://builder.guidebook.com/open-api/v1/guides/{}/publish/'.format(guide_id)
        requests.post(publish_url, headers={'Authorization': 'JWT ' + api_key})

    except:
        print('Unable to update data for event {}'.format(event))

    # Always return 200 so Zenefits doesn't keep retrying
    return {
        'statusCode': 200
    }