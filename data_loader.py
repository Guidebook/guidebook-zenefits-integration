"""
This script will bootstrap a guide in Builder 
with all of currently active employees in Zenefits
Be sure all of the settings in settings.py are up
to date before running this.
"""

import json
import requests
import os

import settings
from customlist_data_builder import CustomlistDataBuilder
from builder_client import BuilderClient


def load_employee_data():

    # Initialize a Session for Builder and Zenefits
    builder_client = BuilderClient(settings.builder_api_key)

    zenefits_session = requests.Session()
    zenefits_session.headers.update(
        {"Authorization": f"Bearer {settings.zenefits_app_key}"}
    )

    customlist_data_builder = CustomlistDataBuilder(
        settings.guide_id, settings.zenefits_app_key
    )

    next_url = (
        f"https://api.zenefits.com/core/companies/{settings.zenefits_company_id}/people"
    )
    employee_list = []
    while next_url is not None:
        response = zenefits_session.get(next_url)
        response.raise_for_status()

        data = response.json()["data"]
        for guide_id, employee_customlist_id in settings.guide_and_list_ids:
            for employee in data["data"]:

                # Only add active employees to the list
                if not _is_active_employee(employee, zenefits_session):
                    continue

                customlist_data = customlist_data_builder.build(employee)

                employee_custom_list_items_url = f"https://builder.guidebook.com/open-api/v1/custom-list-items/?guide={guide_id}&custom_lists={employee_customlist_id}"
                
                # Download and add employee photo to the builder post request if the photo is available
                photo_available = False
                if employee_data.get('photo_url'):
                    img_response = requests.get(employee_data['photo_url'])
                    photo_available = True if img_response.status_code == 200 else False

                if photo_available:
                    with open('image.jpg', 'wb') as handler:
                        handler.write(img_response.content)
                    with open('image.jpg', 'rb') as handler:
                        response = builder_client.post(employee_custom_list_items_url, customlist_data, {"thumbnail": handler})
                    os.remove('image.jpg')
                else:
                    response = builder_client.post(employee_custom_list_items_url, customlist_data)

                # Attach the new custom list item to the custom list
                relations_data = {
                    "custom_list": employee_customlist_id,
                    "custom_list_item": response.json()["id"],
                }
                builder_client.post("https://builder.guidebook.com/open-api/v1/custom-list-item-relations/", relations_data)
                print("Added {} to Builder".format(customlist_data["name"]))

        next_url = data["next_url"]


def _is_active_employee(employee, zenefits_session):
    response = zenefits_session.get(employee["employments"]["url"])
    response.raise_for_status()
    employment_list = response.json()["data"]["data"]
    for employment in employment_list:
        if employment["termination_date"] is None:
            return True
    return False


if __name__ == "__main__":
    load_employee_data()
