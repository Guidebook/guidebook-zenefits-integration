import json
import requests
import boto3
import customlist_data_builder

builder_api_key = 'CHANGE-ME'
zenefits_app_key = 'CHANGE-ME'
guide_id = 'CHANGE-ME'
employee_customlist_id = 'CHANGE-ME'
zenefits_company_id = 'CHANGE-ME'

employee_custom_list_items_url = 'https://builder.guidebook.com/open-api/v1/custom-list-items/?guide={}&custom_lists={}'.format(
    guide_id, employee_customlist_id)
locations = {}
departments = {}


# This script will bootstrap a guide with all of the initial data by
# fetching all employee data from Zenefits and pushing it to
# a specific guide in Builder
def load_employee_data():
    next_url = 'https://api.zenefits.com/core/companies/{}/people'.format(
        zenefits_company_id)
    employee_list = []
    while next_url is not None:
        response = requests.get(
            next_url, headers={'Authorization': 'Bearer ' + zenefits_app_key})
        data = json.loads(response.content)['data']
        for employee in data['data']:
            
            # Only add active employees to the list
            active = _is_active_employee(employee)
            if active:
                customlist_data = customlist_data_builder.build(employee, guide_id)

                response = requests.post(employee_custom_list_items_url, data=customlist_data, headers={
                                         'Authorization': 'JWT ' + builder_api_key}).json()
                relations_data = {
                    "custom_list": employee_customlist_id,
                    "custom_list_item": response['id']
                }
                response = requests.post('https://builder.guidebook.com/open-api/v1/custom-list-item-relations/', data=relations_data, headers={
                                         'Authorization': 'JWT ' + builder_api_key}).json()
                print('Added {} to Builder'.format(customlist_data['name']))
        next_url = data['next_url']


def _is_active_employee(employee):
    url = employee['employments']['url']
    response = requests.get(
        url, headers={'Authorization': 'Bearer ' + zenefits_app_key})
    employment_list = json.loads(response.content)['data']['data']
    for employment in employment_list:
        if employment['termination_date'] == None:
            return True
    return False


if __name__ == "__main__":
    load_employee_data()
