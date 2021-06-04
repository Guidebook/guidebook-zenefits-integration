import traceback
import json
import requests

from ssm_util import fetch_ssm_params


def remove_employee_from_guide(event, context):
    """
    Removes an employee from the guide
    once their employment has been terminated
    """

    try:
        # Fetch the Builder API key, the guide ID of the guide where the content
        # is published, and the custom list ID that the items are associated with
        api_key, guide_and_list_ids, zenefits_app_key = fetch_ssm_params()

        # Initialize a Session
        session = requests.Session()
        session.headers.update({"Authorization": f"JWT {api_key}"})

        data = event["data"]

        for guide_id, employee_customlist_id in guide_and_list_ids:
            # Fetch the existing CustomListItem from Builder by filtering on the import_id field.
            # This is needed to obtain the CustomListItem.id, which is required in the PATCH request
            url = "https://builder.guidebook.com/open-api/v1/custom-list-items/?guide={}&custom_lists={}&import_id={}".format(
                guide_id, employee_customlist_id, data["id"]
            )
            response = session.get(url)
            response.raise_for_status()
            custom_list_items = response.json()["results"]

            # If there is more than one matching CustomListItem, delete them all
            for custom_list_item in custom_list_items:
                url = f"https://builder.guidebook.com/open-api/v1/custom-list-items/{custom_list_item['id']}/"
                session.delete(url)

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
