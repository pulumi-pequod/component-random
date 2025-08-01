import requests
import json
import os
import sys

def update_policy_config():
    # Get environment variables
    api_endpoint = os.environ.get('PULUMI_API_ENDPOINT') or 'https://api.pulumi.com'
    auth_token = os.environ.get('PULUMI_ACCESS_TOKEN')  # The access token is set by the OIDC Issuer that is invoked in the github action
    org = os.environ.get('PULUMI_ORG') 
    if not all([org]):
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

    print("environment variables:")
    print(f"API_ENDPOINT: {api_endpoint}")
    print(f"ORG: {org}")
    print(f"POLICY_GROUPS (raw): {policy_groups_str}")
    print(f"POLICY_GROUPS (parsed): {policy_groups}")
    print(f"PULUMI_ACCESS_TOKEN: {auth_token}")

    # Construct the API URL
    base_api_url = f"{api_endpoint}/api/orgs/{org}/policygroups"
    
    # Set up headers
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # Add authentication if token is provided
    if auth_token:
        headers['Authorization'] = f'Bearer {auth_token}'

    # Loop through each policy group
    for policy_group in policy_groups:
        print(f"Processing policy group: {policy_group}")
        api_url = f"{base_api_url}/{policy_group}"
    
        try:
            # GET request to retrieve policy groups
            print(f"Fetching policy groups from: {api_url}")
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            
            # Parse the JSON response
            policy_data = response.json()
            print(f"Retrieved policy data: {json.dumps(policy_data, indent=2)}")
            
        #     # Modify the policy data as needed
        #     # Example: Update a specific field
        #     if isinstance(policy_data, dict):
        #         # Add or modify fields in the policy data
        #         policy_data['last_updated'] = '2025-08-01'  # Example modification
        #         policy_data['updated_by'] = 'github-action'  # Example modification
            
        #     # PATCH request to update the policy
        #     print(f"Updating policy groups at: {api_url}")
        #     patch_response = requests.patch(
        #         api_url, 
        #         headers=headers,
        #         json=policy_data
        #     )
        #     patch_response.raise_for_status()
            
        #     print("Policy update successful!")
        #     print(f"Response: {patch_response.status_code}")
            
        #     if patch_response.text:
        #         updated_data = patch_response.json()
        #         print(f"Updated policy data: {json.dumps(updated_data, indent=2)}")
            
            return True
            
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

if __name__ == "__main__":
    update_policy_config()