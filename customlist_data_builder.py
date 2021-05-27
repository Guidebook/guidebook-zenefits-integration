import json
import requests


def build(employee, guide_id, zenefits_app_key):
    """
    Builds the CustomList data structure that will be
    send to Builder.  The includes the following fields:
        1) Import ID - the employee's ID used in Zenefits
        2) Name - The employee's preferred name and last name
        3) Title - The employee's title
        4) Work Email
        5) Work Phone
        6) Location - which location they work out of
        7) Department
    """

    # Cache the Locations and Departments so they don't have to
    # be fetched over and over from Zenefits
    location_cache = {}
    department_cache = {}

    # Build the basic CustomListItem object
    customlist_data = {
        "import_id": employee["id"],
        "guide": guide_id,
        "name": f"{employee['preferred_name']} {employee['last_name']}",
        "subtitle": employee["title"],
    }

    # Build a string that contains most of the employee's info that can be
    # displayed in the description field of the custom list item
    work_email_string = "<p>Work Email: {}</p>".format(employee["work_email"])
    work_phone_string = "<p>Work Phone: {}</p>".format(employee["work_phone"])

    if employee["location"]["url"] is not None:
        location_url = employee["location"]["url"]
        if location_url in location_cache:
            location_string = location_cache[location_url]
        else:
            location = get_zenefits_info(location_url, zenefits_app_key)
            location_cache[location_url] = location["name"]
            location_string = f"<p>Location: {location_cache[location_url]}</p>"
    else:
        location_string = ""

    if employee["department"]["url"] is not None:
        department_url = employee["department"]["url"]
        if department_url in department_cache:
            department_string = f"Department: {department_cache[department_url]}"
        else:
            department = get_zenefits_info(department_url, zenefits_app_key)
            department_cache[department_url] = department["name"]
            department_string = "Department: {}".format(department["name"])
    else:
        department_string = ""

    description_html = "".join(
        [work_email_string, work_phone_string, location_string, department_string]
    )
    customlist_data["description_html"] = description_html

    return customlist_data


def get_zenefits_info(resource_url, zenefits_app_key):
    response = requests.get(
        resource_url, headers={"Authorization": f"Bearer {zenefits_app_key}"}
    )
    response.raise_for_status()
    return response.json()["data"]
