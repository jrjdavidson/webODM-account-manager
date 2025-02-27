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
        logging.error(f"Failed to get groups: {response}")
        logging.error(response.json())

    else:
        results = response.json()['results']
        logging.info(results)
        matching_groups = [g for g in results if g['name'] == args.group_name]
        if len(matching_groups) == 1:

            logging.info('Updating Group with default permissions')
            # just get the first matching group
            default_group = next(
                (g for g in results if g['name'] == 'Default'), None)

            group_data = {
                "name": args.group_name,
                "permissions": default_group['permissions']
            }
            response = requests.put(
                f"{webodm_url}api/admin/groups/{matching_groups[0]['id']}/",
                headers={'Authorization': 'JWT {}'.format(token)},
                data=group_data,
            )
            if response.status_code == 200:
                logging.info(f"Updated group with data: {group_data}")

            else:
                logging.error(
                    f"Failed to create group: {response}, {response.json()}")
                return

        else:
            logging.error(
                f"Failed to get group as more than 1 group matches: {matching_groups}")
            return


if __name__ == "__main__":
    # Define the URL of your WebODM instance
    # Set up logging
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    # Set up argument parsing
    parser = argparse.ArgumentParser(
        description='Create WebODM accounts from a CSV file.')
    parser.add_argument('--admin_username', required=True,
                        help='The admin username')
    parser.add_argument('--group_name', required=True, type=str,
                        help='The Name of the group to add the users to')
    parser.add_argument('--webodm_url', required=True, type=str,
                        help='url to your instance of WebODM. eg. "http://132.181.102.65:8000/" ')

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
        logging.error("Failed to authenticate")

    logging.info("Script ended.")
