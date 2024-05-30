import argparse
import os
import requests

# def fetch_all_datasources(base_url, headers):
#     url = f'https://{base_url}/integration/v2/datasource/'
#     response = requests.get(url, headers=headers)

#     if response.status_code == 200:
#         data = response.json()
#         return data

# def did_last_mde_job_succeed_by_ds_id(ds_id, base_url, headers):
#     url = f'https://{base_url}/api/v1/job/?job_type=0&external_service_otype=data&external_service_aid={ds_id}&skip=0&limit=1&order_by=-ts_started&with_num_errors=true&enable_server_count=true'
#     response = requests.get(url, headers=headers)
#     last_job_status = ''

#     if response.status_code == 200:
#         data = response.json()
#         if len(data) > 0:
#             last_job_status = data[0]["status"]
#             print(f'Last job status: {last_job_status}')
#         else: # MDE has never ran on the source; skip the rest
#             return True
              
#     if last_job_status == 'SUCCEEDED':
#         return True
#     else: 
#         return False

# def get_ds_owner_email_address_by_user_id(user_id, base_url, headers):
#     owner_email_address = ''
#     url = f'https://{base_url}/integration/v1/user/{user_id}'
#     response = requests.get(url, headers=headers)

#     if response.status_code == 200:
#         data = response.json()
#         owner_email_address = data['email']

#     return owner_email_address

# def get_email_owner_addresses_by_ds(ds, base_url, headers):
#     ds_owner_email_addresses = []
#     for user_id in ds['owner_ids']:   
#         ds_owner_email_address = get_ds_owner_email_address_by_user_id(user_id, base_url, headers)
#         ds_owner_email_addresses.append(ds_owner_email_address)
#     return ds_owner_email_addresses

# def email_admins_by_email_address(ds, ds_owner_email_addresses):
#     ds_title = ds['title']
#     ds_id = ds['id']
#     subject = f'Last Metadata Extraction (MDE) Job Failed for Data Source: "{ds_title}" (DS ID: {ds_id})'
#     body = f'Last Metadata Extraction (MDE) Job Failed for Data Source: "{ds_title}" (DS ID: {ds_id})'
#     send_email_by_addresses_subject_and_body(ds_owner_email_addresses, subject, body)

# def send_email_by_addresses_subject_and_body(email_addresses, subject, body):
#     print('Skipping email, as function not yet implemented')
#     print(f'Recipients: {email_addresses}')
#     print(f'Subject: {subject}')
#     print(f'Body: {body}')

def fetch_all_document_hubs(base_url, headers):
    url = f'https://{base_url}/api/v1/collection_type/'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
    return data

def main():
    # Create arg parser
    parser = argparse.ArgumentParser(description='Script to sync Document Hub glossary templates.')

    # Add arguments
    parser.add_argument(
        '--token',
        type=str,
        default=os.environ.get('ALATION_TOKEN', None),
        required=os.environ.get('ALATION_TOKEN', None) is None,
        help='Alation API Token'
    )

    parser.add_argument(
        '--base_url',
        type=str,
        default=os.environ.get('ALATION_BASE_URL', None),
        required=os.environ.get('ALATION_BASE_URL', None) is None,
        help='Base URL for your Alation instance (i.e., "alation.mydomain.com")'
    )

    args = parser.parse_args()

    api_token = args.token
    base_url = args.base_url
    headers = {
        'TOKEN': api_token,
        'accept': 'application/json, text/plain, */*'
    }

    # 1. Get all Document Hubs
    all_doc_hubs = fetch_all_document_hubs(base_url, headers)
    print(all_doc_hubs)

if __name__ == "__main__":
    main()