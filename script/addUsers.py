import csv
import requests
import argparse
import logging
from getpass import getpass


def main():

    # GET group
    response = requests.get(
        f"{webodm_url}api/admin/groups/",
        headers={'Authorization': 'JWT {}'.format(token)},
        # data=group_data
    )
    if response.status_code != 200:
        logging.error(f"Failed to get group: {response}")
        logging.error(response.json())

    else:
        results = response.json()['results']
        logging.info(results)
        matching_groups = [g for g in results if g['name'] == args.group_name]
        if len(matching_groups) == 0:

            logging.info('Creating Group with default permissions')
            default_group = next((g for g in results if g['name'] == 'Default'), None) # just get the first matching group

            group_data = {
                "name": args.group_name,
                "permissions": default_group['permissions']
            }
            response = requests.post(
                f"{webodm_url}api/admin/groups/",
                headers={'Authorization': 'JWT {}'.format(token)},
                data=group_data,
            )
            if response.status_code == 201:

                group_id = response.json()['id']
            else:
                logging.error(f"Failed to create group: {response}, {response.json()}")
                return

        elif len(matching_groups) == 1:
            group_id = matching_groups[0]['id']
        else:
            logging.error(f"Failed to get group as more than 1 group matches: {matching_groups}")
            return

        # Open the CSV file
        with open(args.csv_file_path, "r") as csv_file:
            # Create a CSV reader
            csv_reader = csv.reader(csv_file)

            # Iterate over each row in the CSV file
            for row in csv_reader:
                # Get the email address from the first column
                email = row[3]
                first_name = row[0]
                last_name = row[1]
                password = row[4]

                # Define the data for the new user
                user_data = {
                    "username": email.split("@")[0],  # Use the part before the "@" in the email as the username
                    "password": password,  # Use a default password - user id
                    "email": email,
                    "groups": [group_id],
                    "last_name": last_name,
                    "first_name": first_name,
                    "is_active": True,
                }

                # Send a POST request to the WebODM API to create a new user
                response = requests.post(
                    f"{webodm_url}api/admin/users/",
                    data=user_data,
                    headers={'Authorization': 'JWT {}'.format(token)},
                )

                # Check if the request was successful

                if response.status_code == 201:
                    logging.info(f"Successfully created user {user_data['username']} with password: {user_data['password']}.")
                else:
                    logging.error(f"Failed to create user {user_data['username']} with pass: {user_data['password']}.")
                    logging.error(response)
                    logging.error(response.json())


if __name__ == "__main__":
    # Define the URL of your WebODM instance
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Create WebODM accounts from a CSV file.')
    parser.add_argument('--admin_username', required=True, help='The admin username')
    parser.add_argument('--csv_file_path', required=True, help='The path to the CSV file')
    parser.add_argument('--group_name', required=True, type=str, help='The Name of the group to add the users to')
    parser.add_argument('--webodm_url', required=True, type=str, help='url to your inbsance of WebODM. eg. "http://132.181.102.65:8000/" ')

    # Parse the arguments
    args = parser.parse_args()
    webodm_url = args.webodm_url

    # Define the group ID
    admin_password = getpass('Please enter the admin password: ')

    auth_response = requests.post(f'{webodm_url}api/token-auth/',
                                  data={'username': args.admin_username,
                                        'password': admin_password})

    if auth_response.status_code == 200:

        logging.info("Successfully authenticated.")
        result = auth_response.json()
        token = result['token']

        main()

    else:
        logging.error(f"Failed to authenticate")

    logging.info("Script ended.")
