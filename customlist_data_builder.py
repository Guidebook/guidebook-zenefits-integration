import json
import requests

locations = {}
departments = {}

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
def build(employee, guide_id, zenefits_app_key):
    
    print(zenefits_app_key)
    # Build the basic CustomListItem object
    customlist_data = {
        "import_id": employee['id'],
        "guide": guide_id,
        "name": "{} {}".format(employee['preferred_name'], employee['last_name']),
        "subtitle": employee['title'],
    }

    # Build a string that contains most of the employee's info that can be
    # displayed in the description field of the custom list item
    work_email_string = '<p>Work Email: {}</p>'.format(employee['work_email'])
    work_phone_string = '<p>Work Phone: {}</p>'.format(employee['work_phone'])

    location_string = ''
    if employee['location']['url'] is not None:
        location_url = employee['location']['url']
        if location_url in locations.keys():
            location_string = '<p>Location: {}</p>'.format(
                locations[location_url])
        else:
            response = requests.get(location_url, headers={
                                    'Authorization': 'Bearer ' + zenefits_app_key})
            print(response.content)
            location_data = json.loads(response.content)['data']
            print(location_data)
            locations[location_url] = location_data['name']
            location_string = '<p>Location: {}</p>'.format(location_data['name'])

    department_string = ''
    # if employee['department']['url'] is not None:
    #     department_url = employee['department']['url']
    #     if department_url in departments.keys():
    #         department_string = 'Department: {}'.format(
    #             departments[department_url])
    #     else:
    #         response = requests.get(department_url, headers={
    #                                 'Authorization': 'Bearer ' + zenefits_app_key})
    #         department = json.loads(response.content)['data']
    #         departments[department_url] = department['name']
    #         department_string = 'Department: {}'.format(department['name'])

    description_html = '{}{}{}{}'.format(
        work_email_string, work_phone_string, location_string, department_string)
    customlist_data['description_html'] = description_html

    return customlist_data