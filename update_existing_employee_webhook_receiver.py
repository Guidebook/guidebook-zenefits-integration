import json
import requests
import traceback

from ssm_util import fetch_ssm_params
import customlist_data_builder


def update_employee_in_guide(event, context):
    """
    This lambda triggers when an existing employee
    modifies their data in Zenefits.  The new data
    will be written to the appropriate Guide in Builder
    """

    try:
        # Fetch the Builder API key, the guide ID of the guide where the content
        # is published, and the custom list ID that the items are associated with
        api_key, guide_id, employee_customlist_id, zenefits_app_key = fetch_ssm_params()

        # Initialize a Session
        session = requests.Session()
        session.headers.update({"Authorization": f"JWT {api_key}"})

        # Use the lambda event data to build a CustomListItem
        data = event["data"]
        customlist_data = customlist_data_builder.build(
            data, guide_id, zenefits_app_key
        )

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
