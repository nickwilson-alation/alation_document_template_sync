import argparse
import os
import requests
import json

def pretty_print_json(json_to_print):
    return json.dumps(json_to_print, indent=4)

def fetch_all_document_hubs(base_url, headers):
    url = f'https://{base_url}/api/v1/collection_type/'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
    return data

def fetch_all_custom_template_mapping(base_url, headers):
    url = f'https://{base_url}/api/v1/custom_template_sub_type_mapping/'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
    return data

def fetch_all_custom_templates(base_url, headers):
    url = f'https://{base_url}/ajax/custom_template/'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
    return data

def fetch_visual_config_by_id(base_url, headers, id):
    url = f'https://{base_url}/api/v2/visual_config/{id}/'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
    return data

def fetch_template_fields(base_url, headers, template_id):
    url = f'https://{base_url}/api/custom_template/{template_id}/'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
    return data

def create_document_template(base_url, headers, hub_id, template_title, template_layout_otype, template_field_ids, visual_config):
    data = visual_config
    data['collection_type_id'] = hub_id
    data['title'] = template_title
    data['layout_otype'] = template_layout_otype
    data['fields'] = template_field_ids

    url = f'https://{base_url}/api/v2/visual_config/'
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        if response.status_code == 400:
            print("Response content:", response.content.decode('utf-8'))  # Get error details
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred: {req_err}")
    return None

def update_document_template(base_url, headers, hub_id, template_title, template_layout_otype, template_field_ids, visual_config, visual_config_id):
    data = visual_config
    data['collection_type_id'] = hub_id
    data['title'] = template_title
    data['layout_otype'] = template_layout_otype
    data['fields'] = template_field_ids

    url = f'https://{base_url}/api/v2/visual_config/{visual_config_id}/'
    try:
        response = requests.put(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        if response.status_code == 400:
            print("Response content:", response.content.decode('utf-8'))  # Get error details
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred: {req_err}")
    return None

def delete_document_template(base_url, headers, template_id):
    url = f'https://{base_url}/ajax/custom_template/{template_id}/'
    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        if response.status_code == 400:
            print("Response content:", response.content.decode('utf-8'))  # Get error details
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred: {req_err}")
    return None

def get_primary_template_hub(all_document_hubs): 
    if len(all_document_hubs) > 0:
        for hub in all_document_hubs:
            if hub['top_level_nav_name'] == 'Primary Glossary Templates':
                return hub
            
def get_child_glossary_hubs_from_all_document_hubs(all_document_hubs):
    all_glossary_hubs = []
    if len(all_document_hubs) > 0:
        for hub in all_document_hubs:
            if hub['top_level_nav_name'].endswith('Glossary'):
                all_glossary_hubs.append(hub)
    return all_glossary_hubs

def get_templates_by_hub(hub, custom_template_mapping, all_custom_templates):
    glossary_template_hub_templates = []
    # 1. Loop through template mapping:
    for mapping in custom_template_mapping:
        if mapping['sub_type'] == hub['id']:
            for template in all_custom_templates:
                if template['id'] == mapping['custom_template_id']:
                    glossary_template_hub_templates.append(template)
    return glossary_template_hub_templates

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

    # 1. Get all Document Hubs and sort into Glossary Template hub and other glossary hubs:
    all_doc_hubs = fetch_all_document_hubs(base_url, headers)
    primary_glossary_template_hub = get_primary_template_hub(all_doc_hubs)
    child_glossary_hubs = get_child_glossary_hubs_from_all_document_hubs(all_doc_hubs)

    # 2. Get all primary Glossary Hub templates
    all_custom_templates = fetch_all_custom_templates(base_url, headers)
    template_mapping = fetch_all_custom_template_mapping(base_url, headers)
    primary_hub_templates = get_templates_by_hub(primary_glossary_template_hub, template_mapping, all_custom_templates)
    
    # 3. Apply each primary template to all child hubs

    # 3.1 Iterate through each primary template
    for primary_template in primary_hub_templates:
        primary_template_title = primary_template['title']
        primary_template_otype = primary_template['layout_otype']
        primary_template_fields = primary_template['field_ids']
        primary_template_visual_config = fetch_visual_config_by_id(base_url, headers, primary_template['visual_config_id'])
        print(f'Propagating primary template to children: {primary_template_title}')

        # 3.1.1 Iterate through each child glossary hub and find matching template (by name)
        for child_hub in child_glossary_hubs:
            found_match = False
            child_hub_title = child_hub['top_level_nav_name']
            child_hub_id = child_hub['id']
            child_hub_templates = get_templates_by_hub(child_hub, template_mapping, all_custom_templates)

            for child_template in child_hub_templates:
                child_template_title = child_template['title']
                child_template_visual_config_id = child_template['visual_config_id']
                if child_template_title == primary_template_title:
                    found_match = True
                    print(f'Found a match! Primary template "{primary_template_title}" matches "{child_hub_title}" template: {child_template_title}. Syncing from primary template now...')
                    update_document_template(base_url, headers, child_hub_id, child_template_title, primary_template_otype, primary_template_fields, primary_template_visual_config, child_template_visual_config_id)

            if found_match == False:
                print(f'Did not find a match for primary template: {primary_template_title}. Creating a new template for {child_hub_title}')
                new_template = create_document_template(base_url, headers, child_hub_id, primary_template_title, primary_template_otype, primary_template_fields, primary_template_visual_config)

    # 4. Remove non-conforming templates on children
    for child_hub in child_glossary_hubs:
        child_hub_templates = get_templates_by_hub(child_hub, template_mapping, all_custom_templates)
        for child_template in child_hub_templates:
            child_template_title = child_template['title']
            if not any(primary_template['title'] == child_template['title'] for primary_template in primary_hub_templates):
                print(f'Child template "{child_template_title}" not found in Primary templates. Deleting...')
                delete_document_template(base_url, headers, child_template['id'])

# TODO: what if a non-conforming template is already being used?
# TODO: for some reason new doc hub doesn't get the primary templates created... but deleted, yes.
# TODO: what if the name of a primary template is changed?

if __name__ == "__main__":
    main()