import json
import requests


class CustomlistItemDataBuilder(object):
    def __init__(self, guide_id, zenefits_app_key):
        self.location_cache = {}
        self.department_cache = {}
        self.guide_id = guide_id
        self.zenefits_app_key = zenefits_app_key

    def build(self, employee):
        """
        Builds the CustomListItem data structure that will be
        sent to Builder.  This includes the following fields:
            1) Import ID - the employee's ID in Zenefits
            2) Name - The employee's preferred name and last name
            3) Title - The employee's title
            4) Work Email
            5) Work Phone
            6) Location - which physical location an employee works from
            7) Department
        """

        # Cache the Locations and Departments so they don't have to
        # be fetched over and over from Zenefits
        location_cache = {}
        department_cache = {}

        # Build the basic CustomListItem object
        customlist_data = {
            "import_id": employee["id"],
            "guide": self.guide_id,
            "name": f"{employee['preferred_name']} {employee['last_name']}",
            "subtitle": employee["title"],
        }

        # Build a string that contains most of the employee's info that can be
        # displayed in the description field of the custom list item
        work_email_string = '<p>Work Email: <a href="mailto:{}">{}</a></p>'.format(employee["work_email"], employee["work_email"]) if employee.get("work_email") else '<p>Work Email: None</p>'
        work_phone_string = '<p>Work Phone: <a href="tel:{}">{}</a></p>'.format(employee["work_phone"], employee["work_phone"]) if employee.get("work_phone") else '<p>Work Phone: None</p>'

        if employee["location"]["url"] is not None:
            location_url = employee["location"]["url"]
            if location_url not in location_cache:
                location = self._get_zenefits_info(location_url)
                location_cache[location_url] = location["name"]
            location_string = f"<p>Location: {location_cache[location_url]}</p>"
        else:
            location_string = ""

        if employee["department"]["url"] is not None:
            department_url = employee["department"]["url"]
            if department_url not in department_cache:
                department = self._get_zenefits_info(department_url)
                department_cache[department_url] = department["name"]
            department_string = f"<p>Department: {department_cache[department_url]}</p>"
        else:
            department_string = ""

        description_html = "".join(
            [work_email_string, work_phone_string, location_string, department_string]
        )
        customlist_data["description_html"] = description_html

        return customlist_data

    def _get_zenefits_info(self, resource_url):
        response = requests.get(
            resource_url, headers={"Authorization": f"Bearer {self.zenefits_app_key}"}
        )
        response.raise_for_status()
        return response.json()["data"]
