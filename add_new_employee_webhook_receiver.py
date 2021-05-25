import json
import requests
import ssm_util
import customlist_data_builder

# This lambda adds a new employee
# to the guide after they are added
# in Zenefits
def lambda_handler(event, context):
    try:
        # Fetch the Builder API key, the guide ID of the guide where the content
        # is published, and the custom list ID that the items are associated with
        api_key, guide_id, employee_customlist_id, zenefits_app_key = ssm_util.fetch_ssm_params()

        employee_data = event['data']['data'][0]
        customlist_data = customlist_data_builder.build(employee_data, guide_id, zenefits_app_key)

        # Create a new CustomListItem
        url = 'https://builder.guidebook.com/open-api/v1/custom-list-items/?guide={}&custom_lists={}'.format(guide_id, employee_customlist_id)
        response = requests.post(url, data=customlist_data, headers={'Authorization': 'JWT ' + api_key}).json()

        #Create a new CustomListItemRelation
        relations_data = {
            "custom_list": employee_customlist_id,
            "custom_list_item": response['id']
        }
        url = 'https://builder.guidebook.com/open-api/v1/custom-list-item-relations/'
        response = requests.post(url, data=relations_data, headers={
                                 'Authorization': 'JWT ' + api_key}).json()

        # Publish the changes
        publish_url = 'https://builder.guidebook.com/open-api/v1/guides/{}/publish/'.format(guide_id)
        requests.post(publish_url, headers={'Authorization': 'JWT ' + api_key})

    except:
        print('Unable to add data for event {}'.format(event))
    
    return {
        'statusCode': 200
    }
