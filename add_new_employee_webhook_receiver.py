import traceback
import json
import requests
import os

from ssm_util import fetch_ssm_params
from customlist_data_builder import CustomlistDataBuilder


def add_employee_to_guide(event, context):
    """
    This lambda adds a new employee
    to the guide after they are added
    in Zenefits
    """

    try:
        # Fetch the Builder API key, the guide ID of the guide where the content
        # is published, and the custom list ID that the items are associated with
        api_key, guide_and_list_ids, zenefits_app_key = fetch_ssm_params()

        # Initialize a Session
        session = requests.Session()
        session.headers.update({"Authorization": f"JWT {api_key}"})

        for guide_id, employee_customlist_id in guide_and_list_ids:
            # Use the lambda event data to build a CustomListItem
            employee_data = event["data"]
            customlist_data_builder = CustomlistDataBuilder(guide_id, zenefits_app_key)
            customlist_data = customlist_data_builder.build(employee_data)

            # Create a new CustomListItem in Builder
            url = f"https://builder.guidebook.com/open-api/v1/custom-list-items/?guide={guide_id}&custom_lists={employee_customlist_id}"
            photo_available = False
            if employee_data.get('photo_url'):
                img_response = requests.get(employee_data['photo_url'])
                photo_available = True if img_response.status_code == 200 else False

            if photo_available:
                with open('/tmp/image.jpg', 'wb') as handler:
                    handler.write(img_response.content)
                with open('/tmp/image.jpg', 'rb') as handler:
                    response = _post_to_builder(session, url, customlist_data, {"thumbnail": handler})
                os.remove('/tmp/image.jpg')
            else:
                response = _post_to_builder(session, url, customlist_data)

            # Create a new CustomListItemRelation in Builder
            relations_data = {
                "custom_list": employee_customlist_id,
                "custom_list_item": response.json()["id"],
            }
            url = "https://builder.guidebook.com/open-api/v1/custom-list-item-relations/"
            _post_to_builder(session, url, data=relations_data)

        # Publish the changes
        response = _post_to_builder(session, f"https://builder.guidebook.com/open-api/v1/guides/{guide_id}/publish/", raise_error=False)
        if response.status_code == 403:
            print(response.content)

    except Exception as e:
        print(e)
        traceback.print_exc()
        return {"statusCode": 500}

    return {"statusCode": 200}


def _post_to_builder(session, url, data=None, files=None, raise_error=True):
    if data and files:
        response = session.post(url, data=data, files=files)
    elif data:
        response = session.post(url, data=data)
    else:
        response = session.post(url)

    if raise_error:
        response.raise_for_status()
    return response
