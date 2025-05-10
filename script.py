import os
from cloudflare import Cloudflare
import requests

# Retrieve API token, account ID, and access group ID from environment variables (as defined in GitHub Actions secrets)

api_token = os.environ.get("CLOUDFLARE_API_TOKEN", "")
account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")
group_id = os.environ.get("CLOUDFLARE_GROUP_ID", "")  # the specific Cloudflare Access Group you want to update

# checks for the presence of each variable individually and reports specifically which ones are missing

missing = []
if not api_token:
    missing.append("API Token")
if not account_id:
    missing.append("Account ID")
if not group_id:
    missing.append("Group ID")

if missing:
    print("The following required environment variables are missing:")
    for variable in missing:
        print(f"- {variable}")
    exit(1)

# This function retrieves a list of Google's IPv4 and IPv6 address ranges
# by fetching and parsing the JSON data from Google's public IP range file.
# It handles potential HTTP errors by raising an exception, which will stop the script.

def get_google_addresses():
    r = requests.get("https://www.gstatic.com/ipranges/goog.json")
    r.raise_for_status()  # If there is an error, the script will stop
    ips = [entry['ipv4Prefix'] for entry in r.json()['prefixes'] if 'ipv4Prefix' in entry]
    ips += [entry['ipv6Prefix'] for entry in r.json()['prefixes'] if 'ipv6Prefix' in entry]
    return ips

# Update access group in Zero Trust - Cloudflare

def update_access_group():
    # Initialize Cloudflare client with secrets
    cf = Cloudflare() # read secrets from variebles

# Get Google IP addresses
    
    ips = get_google_addresses()

# This dictionary defines the data structure for creating or updating an IP Group,
# specifically for Google's IP addresses. It sets the group's name and includes
# a list of IP address objects derived from a previously obtained list ('ips').
# Exclusion and requirement lists are currently empty.
    
    data = {
        "name": "Google IP Group", # New name for the group
        "include": [{"ip": {"ip": ip}} for ip in ips],
        "exclude": [],
        "require": []
    }

# Updates an existing Cloudflare Access Group with the specified group ID,
# applying the provided data (which likely includes the group's name and included IP addresses)
# within the context of the given Cloudflare account ID.
    cf.zero_trust.access.groups.update(group_id, account_id=account_id, **data)

# Ensures that the 'update_access_group' function is called

if __name__ == "__main__":
    update_access_group()