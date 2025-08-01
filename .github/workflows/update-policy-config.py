import requests
import json
import os
import sys

def update_policy_config():
    # Get environment variables
    api_endpoint = os.environ.get('PULUMI_API_ENDPOINT') or 'https://api.pulumi.com'
    auth_token = os.environ.get('PULUMI_ACCESS_TOKEN')  # The access token is set by the OIDC Issuer that is invoked in the github action
    org = os.environ.get('PULUMI_ORG') 
    
    if not org:
        print("Error: PULUMI_ORG environment variable is required")
        sys.exit(1)
    
    policy_groups_str = os.environ.get('POLICY_GROUPS')

    # Parse POLICY_GROUPS JSON string into a list
    try:
        policy_groups = json.loads(policy_groups_str) if policy_groups_str else []
        if not isinstance(policy_groups, list):
            print("Error: POLICY_GROUPS must be a JSON array")
            sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing POLICY_GROUPS JSON: {e}")
        print(f"POLICY_GROUPS value: {policy_groups_str}")
        sys.exit(1)

    component_versions_str = os.environ.get('PULUMI_COMPONENT_TYPE_VERSIONS')
    try:
        component_versions = json.loads(component_versions_str) if component_versions_str else {}
        if not isinstance(component_versions, dict):
            print("Error: PULUMI_COMPONENT_TYPE_VERSIONS must be a JSON object")
            sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing PULUMI_COMPONENT_TYPE_VERSIONS JSON: {e}")
        print(f"PULUMI_COMPONENT_TYPE_VERSIONS value: {component_versions_str}")
        sys.exit(1)

    if not component_versions:
        print("Error: PULUMI_COMPONENT_TYPE_VERSIONS environment variable is required and must contain at least one component")
        sys.exit(1)

    # Print environment variables for debugging

    print("environment variables:")
    print(f"API_ENDPOINT: {api_endpoint}")
    print(f"ORG: {org}")
    print(f"POLICY_GROUPS (raw): {policy_groups_str}")
    print(f"POLICY_GROUPS (parsed): {policy_groups}")
    print(f"PULUMI_ACCESS_TOKEN: {auth_token}")
    print(f"PULUMI_COMPONENT_TYPE_VERSIONS (raw): {component_versions_str}")
    print(f"PULUMI_COMPONENT_TYPE_VERSIONS (parsed): {component_versions}")

    # Construct the API URL
    base_api_url = f"{api_endpoint}/api/orgs/{org}/policygroups"
    
    # Set up headers
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # Add authentication if token is provided
    if auth_token:
        headers['Authorization'] = f'token {auth_token}'

    # Loop through each policy group
    for policy_group in policy_groups:
        print(f"Processing policy group: {policy_group}")
        api_url = f"{base_api_url}/{policy_group}"
    
        try:
            # GET request to retrieve policy groups
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            
            # Parse the JSON response
            policy_data = response.json()
            print(f"Retrieved policy data: {json.dumps(policy_data, indent=2)}")

            # Modify the policy data - update the component version
            updated = False
            if 'appliedPolicyPacks' in policy_data and policy_data['appliedPolicyPacks']:
                policy_pack = policy_data['appliedPolicyPacks'][0]  # Assuming we want the first policy pack
                
                if 'config' in policy_pack and 'check-component-versions' in policy_pack['config']:
                    allowed_versions = policy_pack['config']['check-component-versions']['allowedComponentVersions']

                    # Find and update component versions
                    for component in allowed_versions:
                        if 'type' in component and 'version' in component:
                            component_type = component['type']
                            # Check if this component type needs to be updated
                            if component_type in component_versions:
                                old_version = component['version']
                                new_version = component_versions[component_type]
                                component['version'] = new_version  # Update to new version
                                print(f"Updated {component_type} version from {old_version} to {new_version}")
                                updated = True
                
                if updated:
                    # Prepare PATCH request body in the required format
                    patch_body = {
                        "addPolicyPack": {
                            "name": policy_pack['name'],
                            "displayName": policy_pack['displayName'],
                            "versionTag": policy_pack['versionTag'],
                            "config": policy_pack['config']
                        }
                    }
                    
                    # PATCH request to update the policy
                    print(f"Updating policy group at: {api_url}")
                    print(f"PATCH body: {json.dumps(patch_body, indent=2)}")
                    
                    patch_response = requests.patch(
                        api_url, 
                        headers=headers,
                        json=patch_body
                    )
                    patch_response.raise_for_status()
                    
                    print("Policy update successful!")
                    print(f"Response: {patch_response.status_code}")
                    
                    if patch_response.text:
                        updated_data = patch_response.json()
                        print(f"Updated policy data: {json.dumps(updated_data, indent=2)}")
                else:
                    print(f"No updates needed - none of the specified component types found in policy: {list(component_versions.keys())}")
            else:
                print("No applied policy packs found")
            
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Status code: {e.response.status_code}")
                print(f"Response text: {e.response.text}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON response: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected error: {e}")
            sys.exit(1)
    
    return True

if __name__ == "__main__":
    update_policy_config()