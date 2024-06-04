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

def get_primary_hub_templates(primary_glossary_template_hub, custom_template_mapping, all_custom_templates):
    glossary_template_hub_templates = []
    # 1. Loop through template mapping:
    for mapping in custom_template_mapping:
        if mapping['sub_type'] == primary_glossary_template_hub['id']:
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
    primary_hub_templates = get_primary_hub_templates(primary_glossary_template_hub, template_mapping, all_custom_templates)
    
    # 3. Apply each primary template to all child hubs

    # 3.1 Iterate through each primary template
    for primary_template in primary_hub_templates:
        primary_template_title = primary_template['title']
        visual_config = fetch_visual_config_by_id(base_url, headers, primary_template['visual_config_id'])
        print(f'visual_config for {primary_template_title}: {pretty_print_json(visual_config)}')

if __name__ == "__main__":
    main()