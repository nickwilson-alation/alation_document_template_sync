import argparse
import os
import requests
import json

class AlationAPI:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {
            'TOKEN': token,
            'accept': 'application/json, text/plain, */*'
        }

    def pretty_print_json(self, json_to_print):
        return json.dumps(json_to_print, indent=4)

    def make_request(self, method, endpoint, data=None):
        url = f'https://{self.base_url}{endpoint}'
        try:
            if method == 'GET':
                response = requests.get(url, headers=self.headers)
            elif method == 'POST':
                response = requests.post(url, headers=self.headers, json=data)
            elif method == 'PUT':
                response = requests.put(url, headers=self.headers, json=data)
            elif method == 'DELETE':
                response = requests.delete(url, headers=self.headers)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            if response.status_code == 400:
                print("Response content:", response.content.decode('utf-8'))
        except requests.exceptions.ConnectionError as conn_err:
            print(f"Connection error occurred: {conn_err}")
        except requests.exceptions.Timeout as timeout_err:
            print(f"Timeout error occurred: {timeout_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"An error occurred: {req_err}")
        return None

    def fetch_all_document_hubs(self):
        return self.make_request('GET', '/api/v1/collection_type/')

    def fetch_all_custom_template_mapping(self):
        return self.make_request('GET', '/api/v1/custom_template_sub_type_mapping/')

    def fetch_all_custom_templates(self):
        return self.make_request('GET', '/ajax/custom_template/')

    def fetch_visual_config_by_id(self, id):
        return self.make_request('GET', f'/api/v2/visual_config/{id}/')

    def fetch_template_fields(self, template_id):
        return self.make_request('GET', f'/api/custom_template/{template_id}/')

    def create_document_template(self, hub_id, template_title, template_layout_otype, template_field_ids, visual_config):
        data = visual_config
        data['collection_type_id'] = hub_id
        data['title'] = template_title
        data['layout_otype'] = template_layout_otype
        data['fields'] = template_field_ids

        return self.make_request('POST', '/api/v2/visual_config/', data)

    def update_document_template(self, hub_id, template_title, template_layout_otype, template_field_ids, visual_config, visual_config_id):
        data = visual_config
        data['collection_type_id'] = hub_id
        data['title'] = template_title
        data['layout_otype'] = template_layout_otype
        data['fields'] = template_field_ids

        return self.make_request('PUT', f'/api/v2/visual_config/{visual_config_id}/', data)

    def delete_document_template(self, template_id):
        return self.make_request('DELETE', f'/ajax/custom_template/{template_id}/')

    def get_primary_template_hub(self, all_document_hubs):
        if len(all_document_hubs) > 0:
            for hub in all_document_hubs:
                if hub['top_level_nav_name'] == 'Primary Glossary Templates':
                    return hub

    def get_child_glossary_hubs_from_all_document_hubs(self, all_document_hubs):
        all_glossary_hubs = []
        if len(all_document_hubs) > 0:
            for hub in all_document_hubs:
                if hub['top_level_nav_name'].endswith('Glossary'):
                    all_glossary_hubs.append(hub)
        return all_glossary_hubs

    def get_templates_by_hub(self, hub, custom_template_mapping, all_custom_templates):
        glossary_template_hub_templates = []
        for mapping in custom_template_mapping:
            if mapping['sub_type'] == hub['id']:
                for template in all_custom_templates:
                    if template['id'] == mapping['custom_template_id']:
                        glossary_template_hub_templates.append(template)
        return glossary_template_hub_templates

def main():
    parser = argparse.ArgumentParser(description='Script to sync Document Hub glossary templates.')

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

    api = AlationAPI(args.base_url, args.token)

    all_doc_hubs = api.fetch_all_document_hubs()
    primary_glossary_template_hub = api.get_primary_template_hub(all_doc_hubs)
    child_glossary_hubs = api.get_child_glossary_hubs_from_all_document_hubs(all_doc_hubs)

    all_custom_templates = api.fetch_all_custom_templates()
    template_mapping = api.fetch_all_custom_template_mapping()
    primary_hub_templates = api.get_templates_by_hub(primary_glossary_template_hub, template_mapping, all_custom_templates)
    
    for primary_template in primary_hub_templates:
        primary_template_title = primary_template['title']
        primary_template_otype = primary_template['layout_otype']
        primary_template_fields = primary_template['field_ids']
        primary_template_visual_config = api.fetch_visual_config_by_id(primary_template['visual_config_id'])
        print(f'Propagating primary template to children: {primary_template_title}')

        for child_hub in child_glossary_hubs:
            found_match = False
            child_hub_title = child_hub['top_level_nav_name']
            child_hub_id = child_hub['id']
            child_hub_templates = api.get_templates_by_hub(child_hub, template_mapping, all_custom_templates)

            for child_template in child_hub_templates:
                child_template_title = child_template['title']
                child_template_visual_config_id = child_template['visual_config_id']
                if child_template_title == primary_template_title:
                    found_match = True
                    print(f'Found a match! Primary template "{primary_template_title}" matches "{child_hub_title}" template: {child_template_title}. Syncing from primary template now...')
                    api.update_document_template(child_hub_id, child_template_title, primary_template_otype, primary_template_fields, primary_template_visual_config, child_template_visual_config_id)

            if not found_match:
                print(f'Did not find a match for primary template: {primary_template_title}. Creating a new template for {child_hub_title}')
                new_template = api.create_document_template(child_hub_id, primary_template_title, primary_template_otype, primary_template_fields, primary_template_visual_config)

    for child_hub in child_glossary_hubs:
        child_hub_templates = api.get_templates_by_hub(child_hub, template_mapping, all_custom_templates)
        for child_template in child_hub_templates:
            child_template_title = child_template['title']
            if not any(primary_template['title'] == child_template['title'] for primary_template in primary_hub_templates):
                print(f'Child template "{child_template_title}" not found in Primary templates. Deleting...')
                api.delete_document_template(child_template['id'])

if __name__ == "__main__":
    main()
