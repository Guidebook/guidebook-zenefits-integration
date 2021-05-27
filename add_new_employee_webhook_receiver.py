import traceback
import json
import requests

from ssm_util import fetch_ssm_params
import customlist_data_builder


def add_employee_to_guide(event, context):
    """
    This lambda adds a new employee
    to the guide after they are added
    in Zenefits
    """
    
    try:
        # Fetch the Builder API key, the guide ID of the guide where the content
        # is published, and the custom list ID that the items are associated with
        api_key, guide_id, employee_customlist_id, zenefits_app_key = fetch_ssm_params()

        # Initialize a Session
        session = requests.Session()
        session.headers.update({"Authorization": f"JWT {api_key}"})

        employee_data = event["data"]
        customlist_data = customlist_data_builder.build(
            employee_data, guide_id, zenefits_app_key
        )

        # Create a new CustomListItem
        url = f"https://builder.guidebook.com/open-api/v1/custom-list-items/?guide={guide_id}&custom_lists={employee_customlist_id}"
        response = session.post(url, data=customlist_data)
        response.raise_for_status()

        # Create a new CustomListItemRelation
        relations_data = {
            "custom_list": employee_customlist_id,
            "custom_list_item": response.json()["id"],
        }
        url = "https://builder.guidebook.com/open-api/v1/custom-list-item-relations/"
        response = session.post(url, data=relations_data)
        response.raise_for_status()

        # Publish the changes
        response = session.post(
            f"https://builder.guidebook.com/open-api/v1/guides/{guide_id}/publish/"
        )
        if response.status_code == 403:
            print(response.content)

    except Exception as e:
        print(e)
        traceback.print_exc()
        return {"statusCode": 500}

    return {"statusCode": 200}
