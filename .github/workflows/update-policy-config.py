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
    
    # Parse POLICY_GROUPS JSON string into a list
    policy_groups_str = os.environ.get('POLICY_GROUPS')
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
        component_versions = json.loads(component_versions_str) if component_versions_str else []
        if not isinstance(component_versions, list):
            print("Error: PULUMI_COMPONENT_TYPE_VERSIONS must be a JSON array")
            sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing PULUMI_COMPONENT_TYPE_VERSIONS JSON: {e}")
        print(f"PULUMI_COMPONENT_TYPE_VERSIONS value: {component_versions_str}")
        sys.exit(1)

    # Helper function to find version for a component type
    def get_component_version(component_type, component_versions_list):
        """
        Search for component_type in the list of dictionaries and return its version.
        component_versions_list format: [{'component:type': 'version'}, ...]
        """
        for item in component_versions_list:
            if component_type in item:
                return item[component_type]
        return None
            
    # Print environment variables for debugging

    print("environment variables:")
    print(f"API_ENDPOINT: {api_endpoint}")
    print(f"ORG: {org}")
    print(f"POLICY_GROUPS: {policy_groups}")
    print(f"PULUMI_COMPONENT_TYPE_VERSIONS: {component_versions}")

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
        print("**************")
        print(f"Processing policy group: {policy_group}")
        api_url = f"{base_api_url}/{policy_group}"
    
        try:
            # GET request to retrieve policy group config
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            
            # Parse the JSON response
            policy_data = response.json()
            # print(f"Retrieved policy data: {json.dumps(policy_data, indent=2)}")

            # Modify the policy data - update the component version to reflect:
            # - new component type version if it exists
            # - add new component type and version if it doesn't exist
            print("Updating policy pack configuration...")
            updated = False
            if 'appliedPolicyPacks' in policy_data and policy_data['appliedPolicyPacks']:
                # Process all policy packs in this policy group
                for policy_pack in policy_data['appliedPolicyPacks']:
                
                      if 'config' in policy_pack and 'check-component-versions' in policy_pack['config']:
                          allowed_versions = policy_pack['config']['check-component-versions']['allowedComponentVersions']

                          # Keep track of which components we've found and updated
                          found_components = set()

                          # Find and update existing component versions
                          for component in allowed_versions:
                              if 'type' in component and 'version' in component:
                                  component_type = component['type']
                                  print(f"Checking component: {component_type}")
                                  
                                  # Check if this component type needs to be updated
                                  new_version = get_component_version(component_type, component_versions)
                                  if new_version:
                                      found_components.add(component_type)
                                      old_version = component['version']
                                      component['version'] = new_version  # Update to new version
                                      print(f"Updated {component_type} version from {old_version} to {new_version}")
                                      updated = True
                                  else:
                                      print(f"No update needed for {component_type}")
                              else:
                                  print(f"Component missing type or version: {component}")
                          
                          # Add new components that weren't found in the existing policy
                          for component_dict in component_versions:
                              for component_type, version in component_dict.items():
                                  if component_type not in found_components:
                                      new_component = {
                                          "type": component_type,
                                          "version": version
                                      }
                                      allowed_versions.append(new_component)
                                      print(f"Added new component: {component_type} with version {version}")
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
                    # Get all component types from the list for the error message
                    all_component_types = []
                    for item in component_versions:
                        all_component_types.extend(item.keys())
                    print(f"No updates needed - none of the specified component types found in policy: {all_component_types}")
            else:
                print("No applied policy packs found")
            
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Status code: {e.response.status_code}")
                print(f"Response text: {e.response.text}")
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON response: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected error: {e}")
            sys.exit(1)
    
    return True

if __name__ == "__main__":
    update_policy_config()