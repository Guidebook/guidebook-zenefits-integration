"""
This script will bootstrap a guide in Builder 
with all of currently active employees in Zenefits
Be sure all of the settings in settings.py are up
to date before running this.
"""

import json
import requests

import settings
from customlist_data_builder import CustomlistDataBuilder


def load_employee_data():

    # Initialize a Session for Builder and Zenefits
    builder_session = requests.Session()
    builder_session.headers.update({"Authorization": f"JWT {settings.builder_api_key}"})

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
        for employee in data["data"]:

            # Only add active employees to the list
            if not _is_active_employee(employee, zenefits_session):
                continue

            customlist_data = customlist_data_builder.build(employee)

            employee_custom_list_items_url = f"https://builder.guidebook.com/open-api/v1/custom-list-items/?guide={settings.guide_id}&custom_lists={settings.employee_customlist_id}"
            response = builder_session.post(
                employee_custom_list_items_url, data=customlist_data
            )
            response.raise_for_status()

            relations_data = {
                "custom_list": settings.employee_customlist_id,
                "custom_list_item": response.json()["id"],
            }
            response = builder_session.post(
                "https://builder.guidebook.com/open-api/v1/custom-list-item-relations/",
                data=relations_data,
            )
            response.raise_for_status()
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
