import json
import requests
import traceback

from ssm_util import fetch_ssm_params
from customlist_data_builder import CustomlistDataBuilder


def update_employee_in_guide(event, context):
    """
    This lambda triggers when an existing employee
    modifies their data in Zenefits.  The new data
    will be written to the appropriate Guide in Builder
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
            data = event["data"]
            customlist_data_builder = CustomlistDataBuilder(guide_id, zenefits_app_key)
            customlist_data = customlist_data_builder.build(data)

            # Fetch the existing CustomListItem from Builder by filtering on the import_id field.
            # This is needed to obtain the CustomListItem.id, which is required in the PATCH request
            url = "https://builder.guidebook.com/open-api/v1/custom-list-items?guide={}&custom_lists={}&import_id={}".format(
                guide_id, employee_customlist_id, data["id"]
            )
            response = session.get(url)
            response.raise_for_status()
            custom_list_item = response.json()["results"][0]

            # Update the existing CustomListItem
            url = "https://builder.guidebook.com/open-api/v1/custom-list-items/{}/".format(
                custom_list_item["id"]
            )
            photo_available = False
            if employee_data.get('photo_url'):
                img_response = requests.get(employee_data['photo_url'])
                photo_available = True if img_response.status_code == 200 else False

            if photo_available:
                with open('image.jpg', 'wb') as handler:
                    handler.write(img_response.content)
                with open('image.jpg', 'rb') as handler:
                    patch_response = session.patch(url, data=customlist_data, files={"thumbnail": handler})
                os.remove('image.jpg')
            else:
                patch_response = session.patch(url, data=customlist_data)
            patch_response.raise_for_status()

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

    # Always return 200 so Zenefits doesn't keep retrying
    return {"statusCode": 200}
